import os
import io
import logging
from datetime import datetime

from urarovite.auth.google_drive import (
    create_drive_service,
    get_auth_secret_from_json,
)
from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(logs_dir, "gsheets_to_xlsx.log")),
    ],
)
logger = logging.getLogger(__name__)


class GSheetToXlsx:
    def __init__(
        self,
        service_account_file: str,
        src_master_sheet_url: str,
        shared_drive_id: str,
        url_column_nr: int = 2,
        base_folder_name: str = "GSheetToXlsx",
        dest_master_sheet_name: str = "Master Sheet",
    ):
        self.src_master_sheet_url = src_master_sheet_url
        self.url_column_nr = url_column_nr
        self.dest_master_sheet_name = dest_master_sheet_name
        self.base_folder_name = base_folder_name
        self.shared_drive_id = shared_drive_id
        self.target_folder_id = None

        auth_secret = get_auth_secret_from_json(service_account_file)
        self.drive_service = create_drive_service(auth_secret)
        self.sheets_service = create_sheets_service_from_encoded_creds(auth_secret)

        self.file_links: list[tuple[str, str]] = []

    def _sheet_id_from_url(self, url: str) -> str:
        """Extract the sheet ID from a Google Sheets URL."""
        try:
            return url.split("/d/")[1].split("/edit")[0]
        except Exception:
            return ""

    def _get_urls_from_master_sheet(self) -> list[str]:
        """Get the URLs from the master sheet."""
        sheet_id = self._sheet_id_from_url(self.src_master_sheet_url)
        result = (
            self.sheets_service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range="Sheet1", valueRenderOption="FORMULA")
            .execute()
        )
        values = result.get("values", [])
        return [
            self._extract_url_from_hyperlink(row[self.url_column_nr])
            for row in values
            if len(row) > self.url_column_nr
        ]

    def _extract_url_from_hyperlink(self, cell_value: str) -> str:
        """Extract the actual URL from a HYPERLINK formula in Google Sheets."""
        if not cell_value or not isinstance(cell_value, str):
            return ""

        if cell_value.strip().startswith("=HYPERLINK("):
            try:
                url = cell_value.split('"')[1]
                return url.strip()
            except Exception as e:
                logger.warning(
                    f"⚠️ Failed to parse HYPERLINK formula: {cell_value}, error: {str(e)}"
                )
                return ""

        elif cell_value.startswith("http"):
            return cell_value.strip()

        return ""

    def _create_target_folder(self) -> str:
        """Create a new folder with timestamp-based name in Google Drive."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{self.base_folder_name}_{timestamp}"

            logger.info(f"📁 Creating target folder: {folder_name}")

            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }

            if self.shared_drive_id:
                folder_metadata["driveId"] = self.shared_drive_id
                folder_metadata["parents"] = [self.shared_drive_id]
            else:
                folder_metadata["parents"] = ["root"]

            folder = (
                self.drive_service.files()
                .create(
                    body=folder_metadata,
                    fields="id, name, webViewLink",
                    supportsAllDrives=True,
                )
                .execute()
            )

            self.target_folder_id = folder["id"]
            logger.info(
                f"✅ Created target folder: {folder_name} (ID: {self.target_folder_id})"
            )
            return self.target_folder_id

        except Exception as e:
            error_msg = f"Failed to create target folder: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)

    def _drive_copy_and_convert_files(self, sheet_url: str):
        """Convert existing Google Sheets to Excel format in Google Drive."""

        logger.info("📄 Copying specific Google Sheets...")

        for url in [sheet_url]:
            print(f"⬇️ Exporting Sheet ID: {url}")

            try:
                sheet_id = self._sheet_id_from_url(url)
                # Get sheet title
                sheet = (
                    self.sheets_service.spreadsheets()
                    .get(spreadsheetId=sheet_id)
                    .execute()
                )
                title = sheet["properties"]["title"]
                filename = f"{title}.xlsx"

                # Export as Excel
                request = self.drive_service.files().export_media(
                    fileId=sheet_id,
                    mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

                fh.seek(0)

                # Upload Excel to Drive folder
                file_metadata = {"name": filename, "parents": [self.target_folder_id]}

                media = MediaIoBaseUpload(
                    fh,
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                uploaded = (
                    self.drive_service.files()
                    .create(
                        body=file_metadata,
                        media_body=media,
                        fields="id, webViewLink",
                        supportsAllDrives=True,
                    )
                    .execute()
                )

                self.file_links.append((title, uploaded["webViewLink"]))
                print(f"✅ Exported: {title} → {uploaded['webViewLink']}")

            except Exception as e:
                print(f"❌ Failed to export {sheet_id}: {e}")

    def _convert_and_upload_files(self):
        """Convert files based on the local flag setting."""
        sheet_urls = self._get_urls_from_master_sheet()
        logger.info(f"🔗 Found {len(sheet_urls)} sheets to convert.")
        for sheet_url in sheet_urls:
            if sheet_url:
                self._drive_copy_and_convert_files(sheet_url=sheet_url)

    def _create_master_sheet(self) -> str:
        """Create a master sheet with links to the converted files in the same folder."""
        try:
            logger.info("📄 Creating master sheet...")

            metadata = {
                "name": self.dest_master_sheet_name,
                "mimeType": "application/vnd.google-apps.spreadsheet",
                "parents": [self.target_folder_id],
            }

            if self.shared_drive_id:
                metadata["driveId"] = self.shared_drive_id

            sheet = (
                self.drive_service.files()
                .create(body=metadata, fields="id", supportsAllDrives=True)
                .execute()
            )

            sheet_id = sheet["id"]
            master_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

            try:
                values = [["File Name", "Google Sheets Link"]]
                for name, link in self.file_links:
                    values.append([name, f'=HYPERLINK("{link}", "{name}")'])

                body = {"values": values}

                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range="Sheet1!A1",
                    valueInputOption="USER_ENTERED",
                    body=body,
                ).execute()

                logger.info(f"📎 Master sheet created and populated: {master_url}")
                return master_url

            except Exception as populate_error:
                logger.warning(
                    f"⚠️ Created master sheet but failed to populate it: {str(populate_error)}"
                )
                logger.info(f"📎 Master sheet created (empty): {master_url}")
                return master_url

        except Exception as e:
            error_msg = f"Failed to create master sheet: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)

    def run(self):
        """Run the full process based on the local flag."""
        logger.info("🚀 Starting XLSX to Google Sheets conversion...")

        self._create_target_folder()

        self._convert_and_upload_files()

        if self.file_links:
            master_url = self._create_master_sheet()
            logger.info("🎉 All done!")
            logger.info(f"🔗 Master Sheet URL: {master_url}")
            logger.info(f"📁 Target Folder ID: {self.target_folder_id}")
        else:
            logger.warning("⚠️ No files were processed. Check your configuration.")
