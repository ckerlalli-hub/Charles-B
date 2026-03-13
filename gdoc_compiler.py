"""Compile a list of emails into a single Google Doc (text only)."""

import re
from datetime import datetime

from googleapiclient.discovery import build

from auth import get_credentials
from gmail_service import Email

# Characters outside the Basic Multilingual Plane (emojis, etc.)
_SURROGATE_RE = re.compile(r"[^\u0000-\uffff]")


def _sanitize(text: str) -> str:
    """Normalise text so Python len() matches Google Docs index counting.

    - Normalises \\r\\n / \\r line endings to \\n (Docs API does this silently).
    - Removes characters outside the BMP (surrogate pairs in UTF-16).
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return _SURROGATE_RE.sub("", text)


def compile_to_gdoc(emails: list[Email], title: str | None = None) -> str:
    """Create a Google Doc containing all emails and return the document URL.

    Inserts ALL text in one request, then applies formatting — no images,
    no page breaks, no index drift.
    """
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)

    if title is None:
        today = datetime.now().strftime("%Y-%m-%d")
        title = f"Compilateur de mail \u2013 Compilation mails ({today})"

    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    # ------------------------------------------------------------------
    # Phase 1 – Build the full plain-text content and track ranges
    # ------------------------------------------------------------------
    full_text = ""
    offset = 0  # running character offset (BMP only, so == UTF-16 units)

    headings: list[tuple[int, int]] = []  # (start, end) for HEADING_1

    for i, email in enumerate(emails):
        # Subject
        subject = _sanitize(email.subject) + "\n"
        headings.append((offset, offset + len(subject)))
        full_text += subject
        offset += len(subject)

        # Body
        body = _sanitize(email.body_text).strip()
        if body:
            body_line = body + "\n"
            full_text += body_line
            offset += len(body_line)

        # Separator between emails
        if i < len(emails) - 1:
            sep = "\n" + "\u2501" * 50 + "\n\n"
            full_text += sep
            offset += len(sep)

    if not full_text:
        return doc_url

    # ------------------------------------------------------------------
    # Phase 2 – Insert text, then apply formatting in a second call
    # ------------------------------------------------------------------
    print(f"  Insertion de {len(full_text)} caractères dans le document…")
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [
            {"insertText": {"location": {"index": 1}, "text": full_text}}
        ]},
    ).execute()

    # Read back the actual document length so we never style past the end
    updated_doc = docs_service.documents().get(documentId=doc_id).execute()
    doc_end = updated_doc["body"]["content"][-1]["endIndex"]

    fmt_requests: list[dict] = []
    for start, end in headings:
        abs_start = 1 + start
        abs_end = 1 + end
        if abs_end > doc_end:
            # Skip headings that would exceed the actual document length
            continue
        fmt_requests.append(
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": abs_start, "endIndex": abs_end},
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                    "fields": "namedStyleType",
                }
            }
        )

    if fmt_requests:
        print(f"  Application du formatage ({len(fmt_requests)} titres)…")
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": fmt_requests}
        ).execute()

    return doc_url
