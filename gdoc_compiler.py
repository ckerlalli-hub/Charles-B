"""Compile a list of emails into a single Google Doc (text only)."""

import re
from datetime import datetime

from googleapiclient.discovery import build

from auth import get_credentials
from gmail_service import Email

# Characters outside the Basic Multilingual Plane (emojis, etc.)
_SURROGATE_RE = re.compile(r"[^\u0000-\uffff]")


def _sanitize(text: str) -> str:
    """Remove characters that would need surrogate pairs in UTF-16.

    This avoids index mismatches between Python len() and the Google
    Docs API (which counts UTF-16 code units).
    """
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
        title = f"Charles B \u2013 Compilation mails ({today})"

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
    # Phase 2 – Single insertText then formatting
    # ------------------------------------------------------------------
    requests: list[dict] = [
        {"insertText": {"location": {"index": 1}, "text": full_text}}
    ]

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

    print(f"  Insertion de {len(full_text)} caractères dans le document…")
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    return doc_url
