import re
from typing import Any, Dict, List, Optional

from googleapiclient.errors import HttpError

FOLDER_ID_RE = re.compile(r"/folders/([a-zA-Z0-9-_]+)")
QUERY_ID_RE = re.compile(r"[?&]id=([a-zA-Z0-9-_]+)")


def extract_folder_id(url: str | None) -> Optional[str]:
    if not url:
        return None
    match = FOLDER_ID_RE.search(url)
    if match:
        return match.group(1)
    match = QUERY_ID_RE.search(url)
    return match.group(1) if match else None


def extract_google_file_id(url: str) -> str | None:
    patterns = [
        r"/d/([a-zA-Z0-9_-]{10,})",  # /d/<id>/
        r"id=([a-zA-Z0-9_-]{10,})",  # ?id=<id>
        r"spreadsheets/d/([a-zA-Z0-9_-]{10,})",  # spreadsheets/d/<id>
        r"drive/folders/([a-zA-Z0-9_-]{10,})",  # folders/<id>
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_parent_folder_id(sheets_url: str, auth_secret: str) -> Optional[str]:
    """Get the parent folder ID of a Google Sheets document.

    Args:
        sheets_url: URL of the Google Sheets document
        auth_secret: Base64 encoded service account credentials

    Returns:
        Parent folder ID, or None if not found

    Raises:
        Exception: If unable to access the file or Drive API
    """
    from urarovite.auth.google_drive import create_drive_service_from_encoded_creds

    # Extract file ID from the URL
    file_id = extract_google_file_id(sheets_url)
    if not file_id:
        return None

    try:
        # Create Drive service
        drive_service = create_drive_service_from_encoded_creds(auth_secret)

        # Get file metadata including parents
        file_metadata = (
            drive_service.files().get(fileId=file_id, fields="parents").execute()
        )

        # Return the first parent folder ID (files can have multiple parents but usually have one)
        parents = file_metadata.get("parents", [])
        return parents[0] if parents else None

    except Exception as e:
        # Log the error but don't fail completely
        import logging

        logging.warning(f"Failed to get parent folder for {sheets_url}: {str(e)}")
        return None


def duplicate_file_to_drive_folder(
    drive_service: Any,
    file_url: str,
    folder_url: str,
    prefix_file_name: str | None = None,
    sheets_service: Any | None = None,
) -> Dict[str, Any]:
    """Duplicate a Google Drive file into a target folder.

    Args:
        drive_service: Google Drive API service instance.
        file_url: Full URL of the source Drive file to duplicate.
        folder_url: Full URL of the destination Drive folder.
        prefix_file_name: Optional string to prepend to the duplicated file's name.
        sheets_service: Optional Google Sheets API service instance. If provided,
                       will use actual spreadsheet title for Google Sheets files.

    Returns:
        Dict with keys:
        - success: Boolean
        - id: The ID of the newly created file when successful, else None.
        - url: URL of the duplicated file or sheet when successful, else None.
        - error: Error code string on failure, otherwise None.
        - error_msg: Optional raw error message from the API when available.
    """
    file_id = extract_google_file_id(file_url)

    if not file_id:
        return {"success": False, "id": None, "url": None, "error": "Invalid file url"}

    folder_id = extract_folder_id(folder_url)
    if not folder_id:
        return {
            "success": False,
            "id": None,
            "url": None,
            "error": "missing_or_malformed_url",
        }

    try:
        src = (
            drive_service.files()
            .get(fileId=file_id, fields="id,name,mimeType", supportsAllDrives=True)
            .execute()
        )

        src_mime = src.get("mimeType", "")

        # Get the proper filename - use spreadsheet title for Google Sheets if possible
        if src_mime == "application/vnd.google-apps.spreadsheet" and sheets_service:
            try:
                # Get actual spreadsheet title from Sheets API
                spreadsheet_metadata = (
                    sheets_service.spreadsheets()
                    .get(spreadsheetId=file_id, fields="properties.title")
                    .execute()
                )
                spreadsheet_title = spreadsheet_metadata.get("properties", {}).get(
                    "title", ""
                )

                if spreadsheet_title:
                    # Only sanitize if title contains invalid filesystem characters
                    invalid_chars = '<>:"/\\|?*'
                    if any(char in spreadsheet_title for char in invalid_chars):
                        # Minimal sanitization - only replace problematic characters
                        name = "".join(
                            c if c not in invalid_chars else "_"
                            for c in spreadsheet_title
                        ).rstrip()
                    else:
                        name = spreadsheet_title
                else:
                    # Fallback to Drive API name
                    name = src.get("name", "Copy")
            except Exception:
                # Fallback to Drive API name if Sheets API fails
                name = src.get("name", "Copy")
        else:
            # Use Drive API name for non-spreadsheet files or when no Sheets service
            name = src.get("name", "Copy")

        if prefix_file_name:
            name = f"{prefix_file_name}{name}"

        body = {"name": name, "parents": [folder_id]}
        dup = (
            drive_service.files()
            .copy(
                fileId=file_id,
                body=body,
                fields="id,webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )

        new_id = dup.get("id")

        if src_mime == "application/vnd.google-apps.spreadsheet":
            new_url = f"https://docs.google.com/spreadsheets/d/{new_id}/edit"
        else:
            new_url = (
                dup.get("webViewLink")
                or f"https://drive.google.com/file/d/{new_id}/view"
            )

        return {"success": True, "id": new_id, "url": new_url, "error": None}

    except Exception as e:
        msg = str(e)
        if "HttpError 403" in msg or "HttpError 404" in msg:
            return {
                "success": False,
                "id": None,
                "url": None,
                "error": "forbidden_or_not_found",
                "error_msg": msg,
            }
        return {
            "success": False,
            "id": None,
            "url": None,
            "error": f"request_exception:{e.__class__.__name__}",
            "error_msg": msg,
        }


def move_sheets_to_folder(
    drive_service: Any,
    sheet_urls: List[str],
    folder_url: str,
) -> List[Dict[str, Any]]:
    """
    Move files to the destination folder.
    - If only_google_sheets=True, skips non‑Sheets files.
    - Works with My Drive and Shared drives (if you have permission).

    Returns:
        List of dictionaries, one for each file, with keys:
        - success: Boolean
        - id: The ID of the moved file when successful, else None.
        - name: Name of the file when successful, else None.
        - error: Error code string on failure, otherwise None.
        - error_msg: Optional raw error message from the API when available.
    """
    results = []

    # Extract folder ID from URL
    folder_id = extract_folder_id(folder_url)
    if not folder_id:
        # Return error for all files if folder URL is invalid
        return [
            {
                "success": False,
                "id": None,
                "name": None,
                "error": "missing_or_malformed_folder_url",
                "error_msg": f"Could not extract folder ID from: {folder_url}",
            }
            for _ in sheet_urls
        ]

    # We'll set supportsAllDrives on read & write in case of Shared drives
    for sheet_url in sheet_urls:
        # Extract file ID from URL
        file_id = extract_google_file_id(sheet_url)
        if not file_id:
            results.append(
                {
                    "success": False,
                    "id": None,
                    "name": None,
                    "error": "invalid_file_url",
                    "error_msg": f"Could not extract file ID from: {sheet_url}",
                }
            )
            continue

        try:
            file = (
                drive_service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, parents, mimeType, driveId",
                    supportsAllDrives=True,
                )
                .execute()
            )

            name = file.get("name", "Unknown")
            parents = file.get("parents", [])

            add_parents = folder_id
            remove_parents = ",".join(parents) if parents else ""

            drive_service.files().update(
                fileId=file_id,
                addParents=add_parents,
                removeParents=remove_parents,
                fields="id, name, parents",
                supportsAllDrives=True,
            ).execute()

            results.append(
                {
                    "success": True,
                    "id": file_id,
                    "name": name,
                    "error": None,
                    "error_msg": None,
                }
            )

        except HttpError as e:
            # Helpful error context
            status = getattr(e, "status_code", None) or getattr(e, "resp", {}).get(
                "status"
            )
            error_msg = f"HTTP {status} - {e}"

            if status in [403, 404]:
                error_code = "forbidden_or_not_found"
            else:
                error_code = f"http_error_{status}"

            results.append(
                {
                    "success": False,
                    "id": file_id,
                    "name": None,
                    "error": error_code,
                    "error_msg": error_msg,
                }
            )

        except Exception as e:
            results.append(
                {
                    "success": False,
                    "id": file_id,
                    "name": None,
                    "error": f"request_exception:{e.__class__.__name__}",
                    "error_msg": str(e),
                }
            )

    return results


def download_file_from_drive(
    file_url: str, local_path: str, auth_credentials: Dict[str, Any]
) -> Dict[str, Any]:
    """Download a file from Google Drive to local disk.

    Args:
        file_url: Google Drive file URL
        local_path: Local path where the file should be saved
        auth_credentials: Authentication credentials (dict with 'auth_secret' key)

    Returns:
        Dict with success status and error info if applicable
    """
    from urarovite.auth.google_drive import create_drive_service_from_encoded_creds
    from googleapiclient.http import MediaIoBaseDownload
    import io

    try:
        # Extract file ID from URL
        file_id = extract_google_file_id(file_url)
        if not file_id:
            return {"success": False, "error": "Could not extract file ID from URL"}

        # Get auth secret from credentials
        if isinstance(auth_credentials, dict):
            auth_secret = auth_credentials.get("auth_secret")
            if not auth_secret:
                return {
                    "success": False,
                    "error": "No auth_secret found in auth_credentials",
                }
        else:
            auth_secret = auth_credentials

        # Create Drive service
        drive_service = create_drive_service_from_encoded_creds(auth_secret)

        # Download the file
        request = drive_service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Write to local file
        with open(local_path, "wb") as f:
            f.write(fh.getvalue())

        return {"success": True, "local_path": local_path}

    except Exception as e:
        return {"success": False, "error": f"Failed to download file: {str(e)}"}


def get_file_metadata(file_url: str, auth_secret: str) -> Dict[str, Any]:
    """Get metadata for a Google Drive file including mimetype.

    Args:
        file_url: Google Drive file URL
        auth_secret: Base64 encoded service account credentials

    Returns:
        Dict containing file metadata or error info

    Example:
        {
            "success": True,
            "id": "1ABC123...",
            "name": "My Spreadsheet",
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "is_google_sheets": True,
            "is_excel": False,
            "is_supported_spreadsheet": True
        }
    """
    from urarovite.auth.google_drive import create_drive_service_from_encoded_creds

    try:
        # Extract file ID from URL
        file_id = extract_google_file_id(file_url)
        if not file_id:
            return {
                "success": False,
                "error": "invalid_url",
                "error_msg": "Could not extract file ID from URL",
            }

        # Create Drive service
        drive_service = create_drive_service_from_encoded_creds(auth_secret)

        # Get file metadata
        file_metadata = (
            drive_service.files()
            .get(
                fileId=file_id,
                fields="id,name,mimeType,parents,driveId",
                supportsAllDrives=True,
            )
            .execute()
        )

        mime_type = file_metadata.get("mimeType", "")

        # Classify file type
        is_google_sheets = mime_type == "application/vnd.google-apps.spreadsheet"
        is_excel = mime_type in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
            "application/vnd.ms-excel",  # .xls
        ]
        is_supported_spreadsheet = is_google_sheets or is_excel

        return {
            "success": True,
            "id": file_metadata.get("id"),
            "name": file_metadata.get("name", "Unknown"),
            "mimeType": mime_type,
            "is_google_sheets": is_google_sheets,
            "is_excel": is_excel,
            "is_supported_spreadsheet": is_supported_spreadsheet,
            "parents": file_metadata.get("parents", []),
            "driveId": file_metadata.get("driveId"),
        }

    except HttpError as e:
        error_code = f"http_{e.resp.status}"
        error_msg = str(e)

        return {"success": False, "error": error_code, "error_msg": error_msg}

    except Exception as e:
        return {
            "success": False,
            "error": f"exception_{e.__class__.__name__}",
            "error_msg": str(e),
        }
