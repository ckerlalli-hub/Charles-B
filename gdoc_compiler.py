"""Compile a list of emails into a single Google Doc with images."""

from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

from auth import get_credentials
from gmail_service import Email


def _upload_image_to_drive(drive_service, image_data: bytes, filename: str, mime_type: str) -> str:
    """Upload an image to Google Drive and return its public URL."""
    media = MediaInMemoryUpload(image_data, mimetype=mime_type, resumable=False)
    file_metadata = {"name": filename}
    uploaded = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    file_id = uploaded["id"]

    # Make the image readable by anyone with the link (required for Docs embedding)
    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"


def compile_to_gdoc(emails: list[Email], title: str | None = None) -> str:
    """Create a Google Doc containing all emails and return the document URL.

    Structure per email:
      - Heading 1: subject
      - Italic paragraph: preview (snippet)
      - Horizontal rule
      - Body text (plain text, paragraphs preserved)
      - Inline images inserted after the body
      - Page break between emails
    """
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    if title is None:
        today = datetime.now().strftime("%Y-%m-%d")
        title = f"Charles B – Compilation mails ({today})"

    # Create an empty document
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    # Build a list of requests to populate the document.
    # Google Docs API inserts are index-based; we build them in reverse order
    # so the first email ends up at the top.
    requests: list[dict] = []

    # We track the current insertion index (starts at 1, right after the doc start).
    idx = 1

    for i, email in enumerate(emails):
        start = idx

        # --- Subject (Heading 1) ---
        subject_text = email.subject + "\n"
        requests.append({"insertText": {"location": {"index": idx}, "text": subject_text}})
        requests.append(
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": idx, "endIndex": idx + len(subject_text)},
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                    "fields": "namedStyleType",
                }
            }
        )
        idx += len(subject_text)

        # --- Preview / Snippet (italic) ---
        preview_text = f"Aperçu : {email.snippet}\n"
        requests.append({"insertText": {"location": {"index": idx}, "text": preview_text}})
        requests.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": idx, "endIndex": idx + len(preview_text) - 1},
                    "textStyle": {"italic": True},
                    "fields": "italic",
                }
            }
        )
        idx += len(preview_text)

        # --- Horizontal rule ---
        requests.append({"insertText": {"location": {"index": idx}, "text": "\n"}})
        idx += 1
        requests.append({"insertSectionBreak": {"location": {"index": idx - 1}, "sectionType": "CONTINUOUS"}})

        # --- Body text ---
        body = email.body_text.strip()
        if body:
            body_text = body + "\n"
            requests.append({"insertText": {"location": {"index": idx}, "text": body_text}})
            requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": idx, "endIndex": idx + len(body_text)},
                        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                        "fields": "namedStyleType",
                    }
                }
            )
            idx += len(body_text)

        # --- Inline images ---
        for img in email.images:
            if not img.data:
                continue
            image_url = _upload_image_to_drive(
                drive_service, img.data, img.filename, img.mime_type
            )
            requests.append(
                {
                    "insertInlineImage": {
                        "location": {"index": idx},
                        "uri": image_url,
                        "objectSize": {
                            "width": {"magnitude": 400, "unit": "PT"},
                        },
                    }
                }
            )
            # An inline image occupies 1 index position
            idx += 1
            requests.append({"insertText": {"location": {"index": idx}, "text": "\n"}})
            idx += 1

        # --- Page break between emails (except after the last one) ---
        if i < len(emails) - 1:
            requests.append({"insertPageBreak": {"location": {"index": idx}}})
            idx += 2  # page break + newline

    # Send all requests in one batch
    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

    return doc_url
