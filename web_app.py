#!/usr/bin/env python3
"""Web interface for the Gmail → Google Doc compiler."""

import os
import threading

from flask import Flask, render_template, request, jsonify, session
from gmail_service import fetch_emails
from gdoc_compiler import compile_to_gdoc
from auth import get_credentials, SCOPES, CREDENTIALS_PATH, TOKEN_PATH

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Track compilation progress per session
_progress: dict[str, dict] = {}


def _get_labels() -> list[str]:
    """Fetch all Gmail labels for the authenticated user."""
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])
    # Filter to user-created labels (exclude system labels like INBOX, SENT, etc.)
    user_labels = [
        lbl["name"]
        for lbl in labels
        if lbl.get("type") == "user"
    ]
    return sorted(user_labels)


@app.route("/")
def index():
    """Main page with the compilation form."""
    authenticated = os.path.exists(TOKEN_PATH)
    labels = []
    if authenticated:
        try:
            labels = _get_labels()
        except Exception:
            authenticated = False
    return render_template("index.html", authenticated=authenticated, labels=labels)


@app.route("/compile", methods=["POST"])
def compile_emails():
    """Run the compilation and return the Google Doc URL."""
    label = request.form.get("label", "Compilateur de mail")
    max_results = int(request.form.get("max_results", 150))
    title = request.form.get("title", "").strip() or None

    try:
        emails = fetch_emails(label_name=label, max_results=max_results)
        if not emails:
            return jsonify({"error": f"Aucun email trouvé avec le label « {label} »."}), 404

        doc_url = compile_to_gdoc(emails, title=title)
        return jsonify({
            "success": True,
            "doc_url": doc_url,
            "email_count": len(emails),
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Erreur inattendue : {e}"}), 500


if __name__ == "__main__":
    print("Ouverture de l'application web sur http://localhost:5000")
    print("Appuyez sur Ctrl+C pour arrêter.")
    app.run(debug=True, port=5000)
