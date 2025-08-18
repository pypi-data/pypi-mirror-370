from typing import Optional

from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from urarovite.auth.google_sheets import decode_service_account
from urarovite.core.exceptions import AuthenticationError
from urarovite.utils.google_api_backoff import with_auth_backoff
from googleapiclient.discovery import build


@with_auth_backoff
def create_drive_service_from_encoded_creds(
    encoded_creds: str, subject: Optional[str] = None
):
    """Create a Google Drive API service from base64 encoded credentials.

    This is a compatibility function for validators that still expect
    the Google Drive API service instead of gspread client.

    Args:
        encoded_creds: Base64 encoded service account credentials
        subject: Optional email for domain-wide delegation

    Returns:
        Google Drive API service instance

    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        # Decode the service account credentials
        service_account_info = decode_service_account(encoded_creds)

        # Create credentials with Google Drive API scopes
        credentials = ServiceAccountCredentials.from_service_account_info(
            service_account_info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )

        # Apply subject delegation if provided
        if subject and subject.strip():
            try:
                credentials = credentials.with_subject(subject.strip())
            except Exception as e:
                import logging

                logging.warning(f"Subject delegation failed: {str(e)}")

        return build("drive", "v3", credentials=credentials)

    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError(
            f"Failed to create Google Drive API service: {str(e)}"
        )
