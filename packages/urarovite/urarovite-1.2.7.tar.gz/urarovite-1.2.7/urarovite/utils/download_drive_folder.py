import os
import io
import logging
from typing import List, Tuple, Dict, Optional
from datetime import datetime
from googleapiclient.http import MediaIoBaseDownload
from urarovite.auth.google_drive import create_drive_service, get_auth_secret_from_json

logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(logs_dir, "download_drive_folder.log")),
    ],
)
logger = logging.getLogger(__name__)


class DriveFolderDownloader:
    def __init__(
        self,
        service_account_file: str,
        folder_id: str,
        local_download_path: str = "./downloads",
        base_folder_name: str = "DriveFolderDownload",
        preserve_structure: bool = True,
        file_types_to_download: Optional[List[str]] = None,
        max_file_size_mb: int = 100,
    ):
        """
        Initialize the Drive Folder Downloader.

        Args:
            service_account_file: Path to Google service account JSON file
            folder_id: Google Drive folder ID to download
            local_download_path: Local directory to save downloaded files
            base_folder_name: Base name for the download folder
            preserve_structure: Whether to maintain folder hierarchy
            file_types_to_download: List of MIME types to download (None = all)
            max_file_size_mb: Maximum file size to download in MB
        """
        self.folder_id = folder_id
        self.local_download_path = local_download_path
        self.base_folder_name = base_folder_name
        self.preserve_structure = preserve_structure
        self.file_types_to_download = file_types_to_download
        self.max_file_size_mb = max_file_size_mb * 1024 * 1024  # Convert to bytes

        # Initialize Google Drive service
        auth_secret = get_auth_secret_from_json(service_account_file)
        self.drive_service = create_drive_service(auth_secret)

        # Statistics
        self.downloaded_files: List[Dict[str, str]] = []
        self.skipped_files: List[Dict[str, str]] = []
        self.errors: List[Dict[str, str]] = []

        # Create download directory
        self._create_download_directory()

    def _create_download_directory(self):
        """Create the main download directory with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.download_folder = os.path.join(
            self.local_download_path, f"{self.base_folder_name}_{timestamp}"
        )

        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            logger.info(f"📁 Created download directory: {self.download_folder}")

    def _get_folder_info(self, folder_id: str) -> Dict:
        """Get information about a Google Drive folder with improved error handling."""
        try:
            logger.info(f"🔍 Attempting to access folder: {folder_id}")

            # First, try to get basic file info
            folder = (
                self.drive_service.files()
                .get(
                    fileId=folder_id,
                    fields="id, name, mimeType, size, parents, permissions, owners",
                    supportsAllDrives=True,
                )
                .execute()
            )

            # Verify it's actually a folder
            if folder.get("mimeType") != "application/vnd.google-apps.folder":
                logger.error(
                    f"❌ The ID {folder_id} is not a folder. MIME type: {folder.get('mimeType')}"
                )
                return {}

            logger.info(
                f"✅ Successfully accessed folder: {folder.get('name', 'Unknown')}"
            )
            return folder

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Failed to get folder info for {folder_id}")

            # Provide more specific error information
            if "404" in error_msg or "not found" in error_msg.lower():
                logger.error(
                    "   → Folder not found. Check if the folder ID is correct."
                )
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                logger.error(
                    "   → Access forbidden. Check if the service account has permission to access this folder."
                )
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                logger.error(
                    "   → Unauthorized. Check if the service account credentials are valid."
                )
            else:
                logger.error(f"   → Error details: {error_msg}")

            return {}

    def _verify_folder_access(self, folder_id: str) -> bool:
        """Verify that we can actually access the folder contents."""
        try:
            print(f"🔐 Verifying access to folder: {folder_id}")

            # Try to list just one item to verify access
            results = (
                self.drive_service.files()
                .list(
                    q=f"'{folder_id}' in parents and trashed=false",
                    fields="files(id, name)",
                    pageSize=100,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )

            print(f"Access verification results: {results}")
            print(f"Files found: {len(results.get('files', []))}")

            logger.info("✅ Folder access verified. Can list contents.")
            return True

        except Exception as e:
            logger.error(f"❌ Cannot access folder contents: {e}")
            print(f"❌ Access verification failed: {e}")
            return False

    def _list_folder_contents(
        self, folder_id: str, parent_path: str = ""
    ) -> List[Dict]:
        """Recursively list all contents of a Google Drive folder."""
        items = []

        try:
            logger.info(f"📋 Listing contents of folder: {folder_id}")

            # Get files and folders in this directory
            results = (
                self.drive_service.files()
                .list(
                    q=f"'{folder_id}' in parents and trashed=false",
                    fields="files(id, name, mimeType, size, parents, webViewLink)",
                    pageSize=100,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            files = results.get("files", [])
            logger.info(f"   Found {len(files)} items in this folder")

            for file in files:
                file_info = {
                    "id": file["id"],
                    "name": file["name"],
                    "mimeType": file["mimeType"],
                    "size": file.get("size", 0),
                    "webViewLink": file.get("webViewLink", ""),
                    "local_path": os.path.join(parent_path, file["name"]),
                }

                if file["mimeType"] == "application/vnd.google-apps.folder":
                    logger.info(f"   📁 Found subfolder: {file['name']}")
                    # Recursively process subfolder
                    subfolder_path = os.path.join(parent_path, file["name"])
                    subfolder_items = self._list_folder_contents(
                        file["id"], subfolder_path
                    )
                    items.extend(subfolder_items)
                else:
                    logger.info(
                        f"   📄 Found file: {file['name']} ({file['mimeType']})"
                    )
                    # Add file to list
                    items.append(file_info)

        except Exception as e:
            logger.error(f"❌ Failed to list contents of folder {folder_id}: {e}")

        return items

    def _should_download_file(self, file_info: Dict) -> bool:
        """Determine if a file should be downloaded based on criteria."""
        # Check file size
        if int(file_info.get("size", 0)) > self.max_file_size_mb:
            logger.warning(
                f"⚠️ File too large: {file_info['name']} ({file_info.get('size', 0)} bytes)"
            )
            return False

        # Check file type if specified
        if self.file_types_to_download:
            if file_info["mimeType"] not in self.file_types_to_download:
                logger.info(
                    f"ℹ️ Skipping file type: {file_info['name']} ({file_info['mimeType']})"
                )
                return False

        return True

    def _download_file(self, file_info: Dict) -> bool:
        """Download a single file from Google Drive."""
        try:
            file_path = os.path.join(self.download_folder, file_info["local_path"])

            # Create directory structure if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Handle different file types
            if file_info["mimeType"] == "application/vnd.google-apps.document":
                # Export Google Docs as DOCX
                request = self.drive_service.files().export_media(
                    fileId=file_info["id"],
                    mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
                file_path = file_path.replace(".gdoc", ".docx")

            elif file_info["mimeType"] == "application/vnd.google-apps.spreadsheet":
                # Export Google Sheets as XLSX
                request = self.drive_service.files().export_media(
                    fileId=file_info["id"],
                    mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                file_path = file_path.replace(".gsheet", ".xlsx")

            elif file_info["mimeType"] == "application/vnd.google-apps.presentation":
                # Export Google Slides as PPTX
                request = self.drive_service.files().export_media(
                    fileId=file_info["id"],
                    mimeType="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )
                file_path = file_path.replace(".gslides", ".pptx")

            else:
                # Download regular files
                request = self.drive_service.files().get_media(fileId=file_info["id"])

            # Download the file
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(
                        f"Downloaded {int(status.progress() * 100)}% of {file_info['name']}"
                    )

            # Save to local file
            fh.seek(0)
            with open(file_path, "wb") as f:
                f.write(fh.read())

            # Update file info with local path
            file_info["local_path"] = file_path
            file_info["download_status"] = "success"

            self.downloaded_files.append(file_info)
            logger.info(f"✅ Downloaded: {file_info['name']} → {file_path}")
            return True

        except Exception as e:
            error_info = {
                "name": file_info["name"],
                "id": file_info["id"],
                "error": str(e),
                "download_status": "failed",
            }
            self.errors.append(error_info)
            logger.error(f"❌ Failed to download {file_info['name']}: {e}")
            return False

    def _create_download_report(self):
        """Create a summary report of the download operation."""
        report_path = os.path.join(self.download_folder, "download_report.txt")

        try:
            with open(report_path, "w") as f:
                f.write("Google Drive Folder Download Report\n")
                f.write("=" * 40 + "\n\n")
                f.write(
                    f"Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write(f"Source Folder ID: {self.folder_id}\n")
                f.write(f"Download Location: {self.download_folder}\n\n")

                f.write(f"Downloaded Files: {len(self.downloaded_files)}\n")
                f.write(f"Skipped Files: {len(self.skipped_files)}\n")
                f.write(f"Errors: {len(self.errors)}\n\n")

                if self.downloaded_files:
                    f.write("Successfully Downloaded:\n")
                    f.write("-" * 25 + "\n")
                    for file_info in self.downloaded_files:
                        f.write(f"✓ {file_info['name']}\n")
                    f.write("\n")

                if self.skipped_files:
                    f.write("Skipped Files:\n")
                    f.write("-" * 15 + "\n")
                    for file_info in self.skipped_files:
                        f.write(
                            f"- {file_info['name']} ({file_info.get('reason', 'Unknown')})\n"
                        )
                    f.write("\n")

                if self.errors:
                    f.write("Errors:\n")
                    f.write("-" * 7 + "\n")
                    for error_info in self.errors:
                        f.write(f"✗ {error_info['name']}: {error_info['error']}\n")

            logger.info(f"📄 Download report created: {report_path}")

        except Exception as e:
            logger.error(f"❌ Failed to create download report: {e}")

    def run(self):
        """Run the complete folder download process."""
        logger.info(f"🚀 Starting download of Google Drive folder: {self.folder_id}")

        # Get folder information
        folder_info = self._get_folder_info(self.folder_id)
        if not folder_info:
            logger.error("❌ Could not retrieve folder information. Exiting.")
            return False

        logger.info(f"📁 Folder: {folder_info.get('name', 'Unknown')}")

        # Verify we can actually access the folder contents
        if not self._verify_folder_access(self.folder_id):
            logger.error("❌ Cannot access folder contents. Check permissions.")
            return False

        # List all contents
        logger.info("🔍 Scanning folder contents...")
        all_files = self._list_folder_contents(self.folder_id)
        logger.info(f"📋 Found {len(all_files)} files/folders")

        if not all_files:
            logger.warning(
                "⚠️ No files found in the folder. It might be empty or inaccessible."
            )
            return True

        # Download files
        logger.info("⬇️ Starting downloads...")
        for file_info in all_files:
            if self._should_download_file(file_info):
                self._download_file(file_info)
            else:
                self.skipped_files.append(file_info)

        # Create report
        self._create_download_report()

        # Summary
        logger.info("🎉 Download completed!")
        logger.info(f"✅ Downloaded: {len(self.downloaded_files)} files")
        logger.info(f"⏭️ Skipped: {len(self.skipped_files)} files")
        logger.info(f"❌ Errors: {len(self.errors)} files")
        logger.info(f"📁 Download location: {self.download_folder}")

        return len(self.errors) == 0

    def _test_service_account_access(self):
        """Test what the service account can actually access."""
        print("🧪 Testing service account access...")
        try:
            # Try to list all files the service account can see
            results = (
                self.drive_service.files()
                .list(
                    fields="files(id, name, mimeType, parents)",
                    pageSize=10,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )

            print(f"Service account can see {len(results.get('files', []))} files:")
            for file in results.get("files", [])[:5]:  # Show first 5
                print(
                    f"  - {file.get('name', 'Unknown')} ({file.get('mimeType', 'Unknown')}) - ID: {file.get('id', 'Unknown')}"
                )

            if len(results.get("files", [])) > 5:
                print(f"  ... and {len(results.get('files', [])) - 5} more files")

        except Exception as e:
            print(f"❌ Service account access test failed: {e}")
