#!/usr/bin/env python3
"""Gmail → Google Doc compiler.

Fetches all emails labelled "Charles B" from Gmail and compiles them
into a single Google Doc (title, preview, body, images).
"""

import argparse
import sys

from gmail_service import fetch_emails
from gdoc_compiler import compile_to_gdoc


def main():
    parser = argparse.ArgumentParser(
        description="Compile les mails Gmail labelisés 'Charles B' dans un Google Doc."
    )
    parser.add_argument(
        "--label",
        default="Charles B",
        help="Nom du label Gmail à filtrer (défaut : 'Charles B').",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=150,
        dest="max_results",
        help="Nombre maximum de mails à récupérer (défaut : 50).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Titre du Google Doc généré (défaut : auto avec la date du jour).",
    )
    args = parser.parse_args()

    print(f"Récupération des mails avec le label « {args.label} »…")
    emails = fetch_emails(label_name=args.label, max_results=args.max_results)

    if not emails:
        print("Aucun mail trouvé avec ce label.")
        sys.exit(0)

    print(f"{len(emails)} mail(s) trouvé(s). Compilation dans un Google Doc…")

    doc_url = compile_to_gdoc(emails, title=args.title)

    print(f"Terminé ! Votre document est disponible ici :\n  {doc_url}")


if __name__ == "__main__":
    main()
