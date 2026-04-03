import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            "credentials.json not found. Download your OAuth 2.0 Desktop App credentials "
            "from Google Cloud Console and place the file in the project root."
        )
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def build_sheet(title: str, categories: dict) -> str:
    creds = get_credentials()
    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    tab_names = list(categories.keys())

    # Create spreadsheet with the first tab already named correctly
    spreadsheet_body = {
        "properties": {"title": title},
        "sheets": [{"properties": {"title": tab_names[0]}}],
    }
    resp = sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
    spreadsheet_id = resp["spreadsheetId"]

    # Add the remaining 3 tabs
    add_requests = [
        {"addSheet": {"properties": {"title": name}}}
        for name in tab_names[1:]
    ]
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": add_requests},
    ).execute()

    # Write header + data rows to each tab
    for tab_name in tab_names:
        rows = categories[tab_name]
        values = [["Name", "Phone", "Hours"]] + [
            [r["name"], r["phone"], r["hours"]] for r in rows
        ]
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{tab_name}'!A1",
            valueInputOption="RAW",
            body={"values": values},
        ).execute()

    # Make the sheet publicly viewable (anyone with link)
    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
    ).execute()

    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
