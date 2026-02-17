"""Compile a list of emails into a single Google Doc with images."""

from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

from auth import get_credentials
from gmail_service import Email


def _utf16_len(text: str) -> int:
    """Return the number of UTF-16 code units in *text*.

    The Google Docs API counts positions in UTF-16 code units, not Python
    code points.  For characters in the Basic Multilingual Plane (most Latin,
    Cyrillic, CJK, etc.) the two counts are equal, but surrogate pairs
    (emojis, some rare symbols) occupy 2 UTF-16 units while Python counts
    them as 1.
    """
    return len(text.encode("utf-16-le")) // 2


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

    Strategy: insert ALL text in a single request, then apply formatting in
    the same batch.  Images are uploaded to Drive and inserted in a second
    batch, processed from end-to-start so index shifts don't cascade.
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

    # ------------------------------------------------------------------
    # Phase 1 – Build the full text and record formatting ranges
    # ------------------------------------------------------------------
    full_text = ""
    utf16_offset = 0          # running offset in UTF-16 code units

    headings: list[tuple[int, int]] = []   # (start, end) for HEADING_1
    italics: list[tuple[int, int]] = []    # (start, end) for italic
    # (utf16_offset, list of EmailImage) – where to insert images later
    image_points: list[tuple[int, list]] = []

    for i, email in enumerate(emails):
        # --- Subject ---
        subject_text = email.subject + "\n"
        subj_start = utf16_offset
        subj_len = _utf16_len(subject_text)
        headings.append((subj_start, subj_start + subj_len))
        full_text += subject_text
        utf16_offset += subj_len

        # --- Preview / Snippet ---
        preview_text = f"Aperçu : {email.snippet}\n"
        prev_start = utf16_offset
        prev_len = _utf16_len(preview_text)
        # italic everything except the trailing newline
        italics.append((prev_start, prev_start + prev_len - 1))
        full_text += preview_text
        utf16_offset += prev_len

        # --- Separator ---
        separator = "━" * 50 + "\n"
        full_text += separator
        utf16_offset += _utf16_len(separator)

        # --- Body ---
        body = email.body_text.strip()
        if body:
            body_text = body + "\n"
            full_text += body_text
            utf16_offset += _utf16_len(body_text)

        # --- Track image insertion point ---
        active_images = [img for img in email.images if img.data]
        if active_images:
            image_points.append((utf16_offset, active_images))

        # --- Visual gap between emails ---
        if i < len(emails) - 1:
            gap = "\n\n"
            full_text += gap
            utf16_offset += _utf16_len(gap)

    # ------------------------------------------------------------------
    # Phase 2 – Insert text + apply formatting (single batchUpdate)
    # ------------------------------------------------------------------
    requests: list[dict] = []

    if full_text:
        requests.append(
            {"insertText": {"location": {"index": 1}, "text": full_text}}
        )

    # All offsets below are shifted by +1 (the doc body starts at index 1)
    for start, end in headings:
        requests.append(
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": 1 + start, "endIndex": 1 + end},
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                    "fields": "namedStyleType",
                }
            }
        )

    for start, end in italics:
        requests.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": 1 + start, "endIndex": 1 + end},
                    "textStyle": {"italic": True},
                    "fields": "italic",
                }
            }
        )

    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

    # ------------------------------------------------------------------
    # Phase 3 – Insert images (separate batch, end-to-start)
    # ------------------------------------------------------------------
    if image_points:
        img_requests: list[dict] = []

        # Process from last insertion point to first so earlier indices
        # are not affected by later insertions.
        for utf16_pos, images in reversed(image_points):
            doc_idx = 1 + utf16_pos
            # Within each point, insert images in reverse so they end up
            # in the original order (each insert pushes previous ones right).
            for img in reversed(images):
                image_url = _upload_image_to_drive(
                    drive_service, img.data, img.filename, img.mime_type
                )
                # Insert a newline first, then the image before it
                img_requests.append(
                    {"insertText": {"location": {"index": doc_idx}, "text": "\n"}}
                )
                img_requests.append(
                    {
                        "insertInlineImage": {
                            "location": {"index": doc_idx},
                            "uri": image_url,
                            "objectSize": {
                                "width": {"magnitude": 400, "unit": "PT"},
                            },
                        }
                    }
                )

        if img_requests:
            docs_service.documents().batchUpdate(
                documentId=doc_id, body={"requests": img_requests}
            ).execute()

    return doc_url
