"""Google API authentication module using OAuth2."""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes needed: read Gmail, create Docs, upload to Drive
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"


def get_credentials() -> Credentials:
    """Return valid Google OAuth2 credentials.

    On first run, opens a browser for the OAuth consent flow and saves
    the token locally. On subsequent runs, reuses / refreshes the token.
    """
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"'{CREDENTIALS_PATH}' introuvable. "
                    "Téléchargez-le depuis la Google Cloud Console "
                    "(APIs & Services > Credentials > OAuth 2.0 Client ID)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return creds
