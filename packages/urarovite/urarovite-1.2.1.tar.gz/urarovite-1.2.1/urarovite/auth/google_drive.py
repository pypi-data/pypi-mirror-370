"""Google Drive API authentication utilities.

This module provides authentication for Google Drive API access using both
OAuth credentials (for interactive use) and service account credentials
(for batch processing systems like Uvarolite).
"""

import json
from typing import Any, Optional

from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from urarovite.auth.google_sheets import decode_service_account
from urarovite.core.exceptions import AuthenticationError
from urarovite.utils.google_api_backoff import with_auth_backoff
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def create_drive_service(auth_secret: dict[str, Any]) -> Any:
    """Create a Google Drive API service instance from auth credentials.

    Args:
        auth_secret: Authentication credentials. Can be either:
            - Service account JSON (dict with 'type': 'service_account')
            - OAuth credentials (dict with token info)

    Returns:
        Google Drive API service object

    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        # Determine credential type and create appropriate credentials
        if auth_secret.get("type") == "service_account":
            # Service account credentials (preferred for batch processing)
            credentials = ServiceAccountCredentials.from_service_account_info(
                auth_secret, scopes=SCOPES
            )
        else:
            # Assume OAuth credentials
            credentials = Credentials.from_authorized_user_info(auth_secret, SCOPES)

        # Create and return the service
        return build("drive", "v3", credentials=credentials)

    except Exception as e:
        raise AuthenticationError(f"Failed to create Google Drive service: {str(e)}")


@with_auth_backoff
def create_drive_service_from_encoded_creds(
    encoded_creds: str, subject: Optional[str] = None
) -> Any:
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
            scopes=SCOPES,
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


def get_auth_secret_from_json(service_account_file: str) -> dict[str, Any]:
    """Get authentication secret from a file.

    Args:
        service_account_file: Path to the authentication secret file

    Returns:
        Authentication secret dictionary
    """
    with open(service_account_file, "r") as f:
        return json.load(f)
