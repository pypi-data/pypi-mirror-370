import io
import os
import re
from typing import TYPE_CHECKING, Optional, Tuple

# When type checking we want access to the concrete ``Resource`` class that
# ``googleapiclient.discovery.build`` returns. Importing it unconditionally
# would require ``googleapiclient`` to be available in every execution
# environment – something we cannot guarantee.  By guarding the import with
# ``TYPE_CHECKING`` we give static analysers (ruff, mypy, etc.) the
# information they need without introducing a hard runtime dependency.
# During static analysis we want to import ``Resource`` so that it is a known
# name for type checkers, but we don't require this import at runtime. Guard
# it with ``TYPE_CHECKING`` to avoid hard dependencies.
if TYPE_CHECKING:  # pragma: no cover
    from googleapiclient.discovery import Resource  # noqa: F401

# Always ensure that the symbol ``Resource`` exists at runtime to placate static
# analysers like ruff (F821) that inspect the AST without executing the code.
try:  # pragma: no cover – optional runtime import
    from googleapiclient.discovery import Resource  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – provide a stub fallback

    class Resource:  # noqa: D401
        """Stub replacement for ``googleapiclient.discovery.Resource``."""

        pass


from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from lumera import get_access_token

# =====================================================================================
# Configuration
# =====================================================================================

MIME_GOOGLE_SHEET = "application/vnd.google-apps.spreadsheet"
MIME_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# =====================================================================================
# Authentication & Service Initialization
# =====================================================================================


def get_google_credentials() -> Credentials:
    """
    Retrieves a Google OAuth token from Lumera and
    converts it into a Credentials object usable by googleapiclient.
    """
    print("Fetching Google access token from Lumera...")
    access_token = get_access_token("google")
    print("Access token received.")
    creds = Credentials(token=access_token)
    print("Credentials object created.")
    return creds


def get_sheets_service(credentials: Credentials) -> 'Resource':
    """Initializes and returns the Google Sheets API service."""
    print("[INFO] Google Sheets API service being initialized...")
    return build('sheets', 'v4', credentials=credentials)


def get_drive_service(credentials: Credentials) -> 'Resource':
    """Initializes and returns the Google Drive API service."""
    print("[INFO] Google Drive API service being initialized...")
    return build('drive', 'v3', credentials=credentials)


# =====================================================================================
# Google Sheets & Drive Utility Functions
# =====================================================================================


def get_spreadsheet_and_sheet_id(
    service: 'Resource', spreadsheet_url: str, tab_name: str
) -> Tuple[Optional[str], Optional[int]]:
    """
    Given a Google Sheets URL and a tab (sheet) name, returns a tuple:
    (spreadsheet_id, sheet_id)
    """
    spreadsheet_id = _extract_spreadsheet_id(spreadsheet_url)
    if not spreadsheet_id:
        return None, None

    sheet_id = _get_sheet_id_from_name(service, spreadsheet_id, tab_name)
    return spreadsheet_id, sheet_id


def _extract_spreadsheet_id(spreadsheet_url: str) -> Optional[str]:
    """Extracts the spreadsheet ID from a Google Sheets URL."""
    print(f"Extracting spreadsheet ID from URL: {spreadsheet_url}")
    pattern = r"/d/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, spreadsheet_url)
    if match:
        spreadsheet_id = match.group(1)
        print(f"Spreadsheet ID extracted: {spreadsheet_id}")
        return spreadsheet_id
    print("Could not extract Spreadsheet ID.")
    return None


def _get_sheet_id_from_name(
    service: 'Resource', spreadsheet_id: str, tab_name: str
) -> Optional[int]:
    """Uses the Google Sheets API to fetch the sheet ID corresponding to 'tab_name'."""
    print(f"Requesting sheet metadata for spreadsheet ID: {spreadsheet_id}")
    response = (
        service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id, fields="sheets.properties")
        .execute()
    )
    print("Metadata received. Searching for tab...")

    for sheet in response.get("sheets", []):
        properties = sheet.get("properties", {})
        if properties.get("title") == tab_name:
            sheet_id = properties.get("sheetId")
            print(f"Match found for tab '{tab_name}'. Sheet ID is {sheet_id}")
            return sheet_id
    print(f"No sheet found with tab name '{tab_name}'.")
    return None


def sheet_name_from_gid(service: 'Resource', spreadsheet_id: str, gid: int) -> Optional[str]:
    """Resolve a sheet's human-readable name (title) from its gid."""
    print(f"[INFO] Resolving sheet name from gid={gid} ...")
    meta = (
        service.spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id,
            includeGridData=False,
            fields="sheets(properties(sheetId,title))",
        )
        .execute()
    )

    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        if props.get("sheetId") == gid:
            title = props["title"]
            print(f"[INFO] Sheet gid={gid} corresponds to sheet name='{title}'.")
            return title
    print(f"No sheet found with gid={gid}")
    return None


def read_cell(service: 'Resource', spreadsheet_id: str, range_a1: str) -> Optional[str]:
    """Fetch a single cell value (as string); returns None if empty."""
    print(f"[DEBUG] Reading cell '{range_a1}' ...")
    resp = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_a1, majorDimension="ROWS")
        .execute()
    )

    values = resp.get("values", [])
    return values[0][0] if values and values[0] else None


# NOTE: The function performs I/O side-effects and does not return a value.
def download_file_direct(drive_service: 'Resource', file_id: str, dest_path: str) -> None:
    """
    Downloads a file directly from Google Drive using files().get_media
    without any format conversion.
    """
    print(f"[INFO] Initiating direct download for file ID: {file_id}")

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"[DEBUG] Download progress: {int(status.progress() * 100)}%")

    with open(dest_path, "wb") as f:
        f.write(fh.getvalue())
    print(f"[SUCCESS] File saved to: {dest_path}")


def upload_excel_as_google_sheet(
    drive_service: 'Resource', local_path: str, desired_name: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Uploads a local XLSX file to Google Drive, converting it to Google Sheets format.
    Returns the file ID and web link.
    """
    print(f"[INFO] Preparing to upload '{local_path}' as Google Sheet named '{desired_name}'")

    if not os.path.isfile(local_path):
        print(f"[ERROR] Local file not found at '{local_path}'. Aborting.")
        return None, None

    media = MediaFileUpload(local_path, mimetype=MIME_EXCEL, resumable=True)
    file_metadata = {"name": desired_name, "mimeType": MIME_GOOGLE_SHEET}

    print("[INFO] Initiating Google Drive upload & conversion...")
    request = drive_service.files().create(
        body=file_metadata, media_body=media, fields="id, webViewLink"
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[DEBUG] Upload progress: {int(status.progress() * 100)}%")

    file_id = response.get("id")
    web_view_link = response.get("webViewLink")
    print(f"[SUCCESS] Upload completed. File ID: {file_id}")
    return file_id, web_view_link


# Remove rows from a sheet.  All parameters are 1-based (both *start_row* and
# *end_row* are inclusive) mirroring the UI behaviour in Google Sheets.
def delete_rows_api_call(
    service: 'Resource',
    spreadsheet_id: str,
    sheet_gid: int,
    start_row: int,
    end_row: int,
) -> None:
    """Executes the API call to delete rows."""
    print(f"[ACTION] Deleting rows {start_row}-{end_row} (1-based inclusive)...")

    body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_gid,
                        "dimension": "ROWS",
                        "startIndex": start_row - 1,  # 0-based
                        "endIndex": end_row,  # end-exclusive
                    }
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    print("[SUCCESS] Rows deleted.")
