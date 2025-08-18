"""Google Sheets authentication utilities focused on gspread and base64 credentials.

This module provides simple authentication for Google Sheets using gspread
with base64 encoded service account credentials, enhanced with exponential backoff
for improved reliability against rate limits and temporary failures.
"""

import json
from base64 import b64decode
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build

from urarovite.core.exceptions import AuthenticationError
from urarovite.utils.google_api_backoff import with_auth_backoff

# Global gspread client cache
_gspread_client: Optional[gspread.Client] = None


def decode_service_account(encoded_creds: str) -> dict:
    """Decode base64 encoded service account credentials.

    Args:
        encoded_creds: Base64 encoded service account JSON

    Returns:
        Service account credentials dictionary

    Raises:
        AuthenticationError: If decoding fails
    """
    try:
        decoded_data = b64decode(encoded_creds).decode("utf-8")
        return json.loads(decoded_data)
    except Exception as e:
        raise AuthenticationError(
            f"Failed to decode service account credentials: {str(e)}"
        )


@with_auth_backoff
def _create_gspread_client(
    encoded_creds: str, subject: Optional[str] = None
) -> gspread.Client:
    """Create a gspread client with base64 encoded service account credentials.

    Args:
        encoded_creds: Base64 encoded service account credentials
        subject: Optional email for domain-wide delegation

    Returns:
        Authenticated gspread client

    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        # Decode the service account credentials
        service_account_info = decode_service_account(encoded_creds)

        # Create credentials with gspread's default scopes
        credentials = ServiceAccountCredentials.from_service_account_info(
            service_account_info, scopes=gspread.auth.DEFAULT_SCOPES
        )

        # Apply subject delegation if provided
        if subject and subject.strip():
            try:
                credentials = credentials.with_subject(subject.strip())
            except Exception as e:
                # Log warning but continue - not all service accounts support delegation
                import logging

                logging.warning(f"Subject delegation failed: {str(e)}")

        # Create and return the gspread client
        return gspread.Client(auth=credentials)

    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError(f"Failed to create gspread client: {str(e)}")


def get_gspread_client(
    encoded_creds: str, subject: Optional[str] = None, use_cache: bool = True
) -> gspread.Client:
    """Get a cached or new gspread client.

    Args:
        encoded_creds: Base64 encoded service account credentials
        subject: Optional email for domain-wide delegation
        use_cache: Whether to use cached client (default: True)

    Returns:
        Authenticated gspread client

    Raises:
        AuthenticationError: If authentication fails
    """
    global _gspread_client

    if not use_cache or _gspread_client is None:
        _gspread_client = _create_gspread_client(encoded_creds, subject)

    return _gspread_client


@with_auth_backoff
def create_sheets_service_from_encoded_creds(
    encoded_creds: str, subject: Optional[str] = None
):
    """Create a Google Sheets API service from base64 encoded credentials.

    This is a compatibility function for validators that still expect
    the Google Sheets API service instead of gspread client.

    Args:
        encoded_creds: Base64 encoded service account credentials
        subject: Optional email for domain-wide delegation

    Returns:
        Google Sheets API service instance

    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        # Decode the service account credentials
        service_account_info = decode_service_account(encoded_creds)

        # Create credentials with Google Sheets API scopes
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

        # Create and return the Google Sheets API service
        return build("sheets", "v4", credentials=credentials)

    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError(
            f"Failed to create Google Sheets API service: {str(e)}"
        )


def clear_client_cache() -> None:
    """Clear the cached gspread client.

    Useful for testing or when credentials change.
    """
    global _gspread_client
    _gspread_client = None
