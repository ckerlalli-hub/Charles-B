"""Fetch emails from Gmail with a specific label."""

import base64
import re
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup
from googleapiclient.discovery import build

from auth import get_credentials

LABEL_NAME = "Compilateur de mail"


@dataclass
class EmailImage:
    """An image embedded in or attached to an email."""

    filename: str
    mime_type: str
    data: bytes  # raw image bytes


@dataclass
class Email:
    """Parsed representation of a single email."""

    subject: str
    snippet: str  # Gmail's built-in preview text
    body_html: str
    body_text: str
    images: list[EmailImage] = field(default_factory=list)


def _get_gmail_service():
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


def _find_label_id(service, label_name: str) -> Optional[str]:
    """Find the label ID for a given label name."""
    results = service.users().labels().list(userId="me").execute()
    for label in results.get("labels", []):
        if label["name"] == label_name:
            return label["id"]
    return None


def _decode_base64url(data: str) -> bytes:
    """Decode base64url-encoded data (used by Gmail API)."""
    return base64.urlsafe_b64decode(data + "==")


def _extract_parts(payload: dict, email: Email):
    """Recursively walk MIME parts to extract text, HTML, and inline images."""
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data")
        if data:
            email.body_text += _decode_base64url(data).decode("utf-8", errors="replace")

    elif mime_type == "text/html":
        data = payload.get("body", {}).get("data")
        if data:
            email.body_html += _decode_base64url(data).decode("utf-8", errors="replace")

    elif mime_type.startswith("image/"):
        attachment_id = payload.get("body", {}).get("attachmentId")
        filename = payload.get("filename") or f"image.{mime_type.split('/')[-1]}"
        if attachment_id:
            email.images.append(
                EmailImage(
                    filename=filename,
                    mime_type=mime_type,
                    data=b"",  # will be fetched separately
                )
            )
            # Store attachment_id temporarily for later fetching
            email.images[-1]._attachment_id = attachment_id  # type: ignore[attr-defined]

    for part in payload.get("parts", []):
        _extract_parts(part, email)


def _fetch_attachment(service, message_id: str, attachment_id: str) -> bytes:
    """Download a single attachment by ID."""
    att = (
        service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()
    )
    return _decode_base64url(att["data"])


def _html_to_plain(html: str) -> str:
    """Convert HTML to readable plain text as a fallback."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def fetch_emails(label_name: str = LABEL_NAME, max_results: int = 50) -> list[Email]:
    """Return all emails under the given label, newest first."""
    service = _get_gmail_service()

    label_id = _find_label_id(service, label_name)
    if not label_id:
        raise ValueError(
            f"Label '{label_name}' introuvable dans votre boîte Gmail. "
            "Vérifiez que le label existe (sensible à la casse)."
        )

    # List message IDs matching the label
    message_ids: list[str] = []
    page_token = None
    while True:
        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                labelIds=[label_id],
                maxResults=min(max_results - len(message_ids), 100),
                pageToken=page_token,
            )
            .execute()
        )
        for msg in response.get("messages", []):
            message_ids.append(msg["id"])
            if len(message_ids) >= max_results:
                break
        page_token = response.get("nextPageToken")
        if not page_token or len(message_ids) >= max_results:
            break

    # Fetch full message details
    emails: list[Email] = []
    for msg_id in message_ids:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_id, format="full")
            .execute()
        )
        payload = msg.get("payload", {})
        headers = {h["name"]: h["value"] for h in payload.get("headers", [])}

        email = Email(
            subject=headers.get("Subject", "(sans sujet)"),
            snippet=msg.get("snippet", ""),
            body_html="",
            body_text="",
        )

        _extract_parts(payload, email)

        # Fetch actual image data for inline images
        for img in email.images:
            att_id = getattr(img, "_attachment_id", None)
            if att_id:
                img.data = _fetch_attachment(service, msg_id, att_id)

        # If we only got HTML, derive a plain-text version too
        if email.body_html and not email.body_text:
            email.body_text = _html_to_plain(email.body_html)

        emails.append(email)

    return emails
