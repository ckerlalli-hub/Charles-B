#!/usr/bin/env python3
"""Generate the Word (.docx) guide for Charles-B Gmail → Google Doc Compiler."""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE


def add_heading(doc, text, level=1):
    return doc.add_heading(text, level=level)


def add_para(doc, text, bold=False, italic=False, style=None):
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    return p


def add_code_block(doc, text):
    """Add a code block with monospace font and gray background."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(30, 30, 30)
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(text, style="List Bullet")
    if level > 0:
        p.paragraph_format.left_indent = Inches(0.5 * (level + 1))
    return p


def add_numbered(doc, text, level=0):
    p = doc.add_paragraph(text, style="List Number")
    if level > 0:
        p.paragraph_format.left_indent = Inches(0.5 * (level + 1))
    return p


def add_note(doc, text):
    p = doc.add_paragraph()
    run = p.add_run("Note : ")
    run.bold = True
    run.font.color.rgb = RGBColor(0, 100, 180)
    run2 = p.add_run(text)
    run2.italic = True
    return p


def add_separator(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("─" * 60)
    run.font.color.rgb = RGBColor(180, 180, 180)


def build_document():
    doc = Document()

    # --- Title page ---
    title = doc.add_heading("Guide complet : Compilateur Gmail → Google Doc", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("Projet Charles-B")
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(80, 80, 80)

    desc = doc.add_paragraph()
    desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = desc.add_run(
        "Ce guide vous accompagne pas-a-pas pour installer et utiliser l'outil Charles-B,\n"
        "qui recupere automatiquement les emails d'un label Gmail\n"
        "et les compile dans un Google Doc sur votre Drive."
    )
    run.font.size = Pt(11)
    run.italic = True

    doc.add_page_break()

    # --- Table des matieres ---
    add_heading(doc, "Table des matieres", level=1)
    toc_items = [
        "1. Ce que fait l'outil",
        "2. Pre-requis",
        "3. Creer un projet Google Cloud",
        "4. Activer les APIs necessaires",
        "5. Creer les identifiants OAuth 2.0",
        "6. Recuperer le projet sur votre PC",
        "7. Preparer votre boite Gmail",
        "8. Lancer le programme",
        "9. Modifier le label et le nom du document",
        "10. Comprendre le Google Doc genere",
        "11. Depannage",
        "12. Questions frequentes",
    ]
    for item in toc_items:
        doc.add_paragraph(item, style="List Number")

    doc.add_page_break()

    # ===== SECTION 1 =====
    add_heading(doc, "1 — Ce que fait l'outil", level=1)
    add_para(doc, "L'outil Charles-B :")
    add_numbered(doc, "Se connecte a votre compte Gmail via l'API Google")
    add_numbered(doc, "Recupere tous les emails portant un label de votre choix")
    add_numbered(doc, "Cree un Google Doc sur votre Drive")
    add_numbered(doc, "Y insere le contenu de chaque email : sujet (en titre), corps du texte")
    add_numbered(doc, "Vous donne le lien direct vers le document")
    add_para(doc,
        "Resultat : un document unique, proprement formate, contenant tous vos emails.",
        italic=True,
    )

    add_separator(doc)

    # ===== SECTION 2 =====
    add_heading(doc, "2 — Pre-requis", level=1)
    add_para(doc, "Avant de commencer, assurez-vous d'avoir :")
    add_bullet(doc, "Un compte Google (Gmail)")
    add_bullet(doc, "Python 3.10 ou superieur installe sur votre machine")
    add_bullet(doc, "Git installe (optionnel, pour cloner le projet — sinon le ZIP suffit)")
    add_bullet(doc, "Un acces a Internet")

    add_heading(doc, "Verifier votre version de Python", level=2)
    add_para(doc, "Ouvrez l'Invite de commandes Windows (cmd) ou PowerShell et tapez :")
    add_code_block(doc, "python --version")
    add_para(doc,
        "Vous devez voir Python 3.10.x ou superieur. Si ce n'est pas le cas, "
        "telechargez Python depuis python.org/downloads."
    )
    add_note(doc,
        "Windows : lors de l'installation de Python, cochez la case « Add Python to PATH »."
    )

    add_separator(doc)

    # ===== SECTION 3 =====
    add_heading(doc, "3 — Creer un projet Google Cloud", level=1)
    add_para(doc,
        "L'outil utilise les APIs officielles de Google. Il faut creer un projet "
        "gratuit sur Google Cloud pour obtenir les autorisations."
    )
    add_heading(doc, "Etape par etape :", level=2)
    add_numbered(doc, "Rendez-vous sur https://console.cloud.google.com/")
    add_numbered(doc, "Connectez-vous avec votre compte Google")
    add_numbered(doc,
        "En haut de la page, cliquez sur le selecteur de projet (a cote du logo Google Cloud)"
    )
    add_numbered(doc, 'Cliquez sur « Nouveau projet »')
    add_numbered(doc, "Donnez-lui un nom (par exemple : Gmail-Compiler)")
    add_numbered(doc, 'Cliquez sur « Creer »')
    add_numbered(doc, "Attendez quelques secondes, puis selectionnez votre nouveau projet")

    add_separator(doc)

    # ===== SECTION 4 =====
    add_heading(doc, "4 — Activer les APIs necessaires", level=1)
    add_para(doc,
        "Le programme a besoin de 3 APIs Google. Il faut les activer une par une."
    )
    add_heading(doc, "Etape par etape :", level=2)
    add_numbered(doc,
        'Dans le menu lateral gauche, allez dans « APIs et services » > « Bibliotheque »'
    )

    add_para(doc, "Gmail API :", bold=True)
    add_bullet(doc, "Cherchez « Gmail API » dans la barre de recherche")
    add_bullet(doc, "Cliquez dessus puis cliquez sur « Activer »")

    add_para(doc, "Google Docs API :", bold=True)
    add_bullet(doc, "Cherchez « Google Docs API »")
    add_bullet(doc, "Cliquez dessus puis cliquez sur « Activer »")

    add_para(doc, "Google Drive API :", bold=True)
    add_bullet(doc, "Cherchez « Google Drive API »")
    add_bullet(doc, "Cliquez dessus puis cliquez sur « Activer »")

    add_note(doc,
        "Si le bouton indique « Gerer » au lieu de « Activer », c'est que l'API est deja activee."
    )

    add_separator(doc)

    # ===== SECTION 5 =====
    add_heading(doc, "5 — Creer les identifiants OAuth 2.0", level=1)
    add_para(doc,
        "C'est l'etape la plus importante : elle permet au programme de se connecter "
        "a votre compte Google de maniere securisee."
    )

    add_heading(doc, "5.1 — Configurer l'ecran de consentement OAuth", level=2)
    add_numbered(doc, '« APIs et services » > « Ecran de consentement OAuth »')
    add_numbered(doc, 'Selectionnez « Externe » comme type d\'utilisateur')
    add_numbered(doc, 'Cliquez sur « Creer »')
    add_numbered(doc, "Remplissez les champs obligatoires :")
    add_bullet(doc, "Nom de l'application : Gmail Compiler (ou ce que vous voulez)", level=1)
    add_bullet(doc, "Adresse e-mail d'assistance : votre adresse Gmail", level=1)
    add_bullet(doc, "Adresses e-mail du developpeur : votre adresse Gmail", level=1)
    add_numbered(doc, '« Enregistrer et continuer »')
    add_numbered(doc,
        'A l\'etape « Champs d\'application » (Scopes) : '
        '« Enregistrer et continuer » sans rien ajouter'
    )
    add_numbered(doc,
        'A l\'etape « Utilisateurs de test » : « Ajouter des utilisateurs » '
        'et ajoutez votre propre adresse Gmail'
    )
    add_numbered(doc, '« Enregistrer et continuer »')

    add_note(doc,
        "Tant que l'application est en mode « Test », seuls les utilisateurs de test "
        "que vous avez ajoutes peuvent l'utiliser. C'est normal et suffisant pour un usage personnel."
    )

    add_heading(doc, "5.2 — Creer le Client ID OAuth", level=2)
    add_numbered(doc, '« APIs et services » > « Identifiants » (ou Credentials)')
    add_numbered(doc, '« + Creer des identifiants » en haut')
    add_numbered(doc, '« ID client OAuth »')
    add_numbered(doc, 'Type d\'application : « Application de bureau » (Desktop app)')
    add_numbered(doc, "Nom : Gmail Compiler Desktop")
    add_numbered(doc, '« Creer »')

    add_heading(doc, "5.3 — Telecharger le fichier credentials.json", level=2)
    add_numbered(doc,
        "Une fenetre apparait avec votre Client ID. "
        'Cliquez sur « Telecharger le fichier JSON »'
    )
    add_numbered(doc,
        "Un fichier est telecharge (son nom ressemble a client_secret_XXXXX.json)"
    )
    add_numbered(doc, "Renommez ce fichier en credentials.json")
    add_numbered(doc, "Gardez-le de cote, vous le placerez dans le dossier du projet a l'etape suivante")

    add_separator(doc)

    # ===== SECTION 6 =====
    add_heading(doc, "6 — Recuperer le projet sur votre PC", level=1)
    add_para(doc,
        "Le projet est heberge sur GitHub a l'adresse suivante :"
    )
    add_para(doc, "https://github.com/ckerlalli-hub/Charles-B", bold=True)
    add_para(doc,
        "Vous n'avez pas besoin de creer votre propre compte GitHub ni votre propre depot. "
        "Il suffit de telecharger le projet une seule fois.",
        italic=True,
    )

    add_heading(doc, "Option A — Telecharger le ZIP (le plus simple, sans Git)", level=2)
    add_numbered(doc, "Rendez-vous sur https://github.com/ckerlalli-hub/Charles-B")
    add_numbered(doc, 'Cliquez sur le bouton vert « <> Code »')
    add_numbered(doc, 'Cliquez sur « Download ZIP »')
    add_numbered(doc,
        "Decompressez le fichier ZIP sur votre ordinateur "
        "(par exemple dans le dossier Documents ou sur le Bureau)"
    )
    add_numbered(doc,
        "Vous obtenez un dossier « Charles-B-main ». "
        "Renommez-le en « Charles-B » si vous le souhaitez."
    )

    add_heading(doc, "Option B — Cloner avec Git (si Git est installe)", level=2)
    add_para(doc, "Ouvrez l'Invite de commandes (Windows + R → cmd → Entree) :")
    add_code_block(doc, "cd %USERPROFILE%\\Desktop")
    add_code_block(doc, "git clone https://github.com/ckerlalli-hub/Charles-B.git")
    add_code_block(doc, "cd Charles-B")
    add_note(doc,
        "Avantage de Git : vous pourrez mettre a jour le projet plus tard "
        "avec un simple « git pull »."
    )

    add_heading(doc, "6.4 — Placer le fichier credentials.json", level=2)
    add_para(doc,
        "Copiez le fichier credentials.json (telecharge a l'etape 5.3) "
        "dans le dossier Charles-B."
    )
    add_para(doc, "Vous pouvez le faire via l'Explorateur de fichiers (glisser-deposer) "
        "ou avec la commande :")
    add_code_block(doc, "copy %USERPROFILE%\\Downloads\\credentials.json .")
    add_para(doc, "Structure attendue :", bold=True)
    add_code_block(doc,
        "Charles-B/\n"
        "├── auth.py\n"
        "├── gmail_service.py\n"
        "├── gdoc_compiler.py\n"
        "├── main.py\n"
        "├── requirements.txt\n"
        "├── credentials.json     ← VOTRE FICHIER ICI\n"
        "└── ..."
    )

    add_heading(doc, "6.5 — Installer les dependances Python", level=2)
    add_para(doc, "Toujours dans le dossier du projet, tapez :")
    add_code_block(doc, "pip install -r requirements.txt")
    add_para(doc, "Cela installe les bibliotheques necessaires :")
    add_bullet(doc, "google-api-python-client — SDK Google APIs")
    add_bullet(doc, "google-auth-httplib2 — Transport HTTP pour l'authentification")
    add_bullet(doc, "google-auth-oauthlib — Gestion du flux OAuth2")
    add_bullet(doc, "beautifulsoup4 — Extraction du texte depuis le HTML des emails")

    add_note(doc, "Si vous avez plusieurs versions de Python, utilisez pip3 au lieu de pip.")

    add_separator(doc)

    # ===== SECTION 7 =====
    add_heading(doc, "7 — Preparer votre boite Gmail", level=1)
    add_para(doc,
        "Le programme filtre les emails par label Gmail. Vous devez donc avoir un label "
        "applique aux emails que vous souhaitez compiler."
    )

    add_heading(doc, "Creer un label (si necessaire)", level=2)
    add_numbered(doc, "Ouvrez Gmail (https://mail.google.com)")
    add_numbered(doc, 'Dans le menu lateral gauche, cliquez sur « Plus » puis « Creer un libelle »')
    add_numbered(doc,
        "Entrez le nom souhaite (par exemple : Newsletters, Rapports, Compilateur de mail)"
    )
    add_numbered(doc, '« Creer »')

    add_heading(doc, "Appliquer le label a des emails", level=2)
    add_numbered(doc, "Selectionnez les emails souhaites (cases a cocher)")
    add_numbered(doc, 'Cliquez sur l\'icone « Libelles » (l\'etiquette en haut)')
    add_numbered(doc, "Cochez le label que vous venez de creer")
    add_numbered(doc, '« Appliquer »')

    add_note(doc,
        "Le nom du label est sensible a la casse. « Newsletter » et « newsletter » "
        "sont deux labels differents. Notez bien l'orthographe exacte."
    )

    add_separator(doc)

    # ===== SECTION 8 =====
    add_heading(doc, "8 — Lancer le programme", level=1)

    add_heading(doc, "8.1 — Premiere execution (authentification)", level=2)
    add_para(doc, "Dans l'invite de commandes, depuis le dossier du projet :")
    add_code_block(doc, 'python main.py --label "NOM_DE_VOTRE_LABEL"')
    add_para(doc, "Remplacez NOM_DE_VOTRE_LABEL par le nom exact de votre label Gmail.")

    add_para(doc, "Ce qui va se passer :", bold=True)
    add_numbered(doc, "Votre navigateur s'ouvre automatiquement sur une page Google")
    add_numbered(doc, "Selectionnez votre compte Google")
    add_numbered(doc,
        "Un avertissement s'affiche (« Cette application n'est pas validee ») — c'est normal"
    )
    add_numbered(doc,
        '« Continuer » (ou « Advanced » > « Go to Gmail Compiler »)'
    )
    add_numbered(doc, "Acceptez les 3 permissions demandees :")
    add_bullet(doc, "Lecture de vos emails Gmail", level=1)
    add_bullet(doc, "Creation de documents Google Docs", level=1)
    add_bullet(doc, "Gestion de fichiers sur Google Drive", level=1)
    add_numbered(doc, "La fenetre se ferme, le programme continue dans le terminal")

    add_para(doc,
        "Un fichier token.json est cree automatiquement. "
        "Lors des prochaines executions, le navigateur ne s'ouvrira plus.",
        italic=True,
    )

    add_heading(doc, "8.2 — Resultats", level=2)
    add_para(doc, "Le terminal affiche la progression :")
    add_code_block(doc,
        'Recuperation des mails avec le label « Mon Label »…\n'
        '42 mail(s) trouve(s). Compilation dans un Google Doc…\n'
        '  Insertion de 28543 caracteres dans le document…\n'
        '  Application du formatage (42 titres)…\n'
        'Termine ! Votre document est disponible ici :\n'
        '  https://docs.google.com/document/d/XXXXXXXXX/edit'
    )
    add_para(doc, "Cliquez sur le lien pour ouvrir votre Google Doc !", bold=True)

    add_separator(doc)

    # ===== SECTION 9 =====
    add_heading(doc, "9 — Modifier le label a traiter et le nom du document", level=1)
    add_para(doc,
        "Vous n'avez pas besoin de modifier le code source pour changer le label "
        "ou le titre du document. Tout se fait via les options de la ligne de commande."
    )

    add_heading(doc, "Changer le label Gmail a traiter", level=2)
    add_para(doc, "Utilisez l'option --label suivi du nom exact du label :")
    add_code_block(doc, 'python main.py --label "Newsletters"')
    add_code_block(doc, 'python main.py --label "Rapports mensuels"')
    add_code_block(doc, 'python main.py --label "Clients VIP"')
    add_note(doc,
        "Le nom du label doit correspondre exactement a celui dans Gmail "
        "(majuscules, minuscules, accents, espaces). Mettez-le entre guillemets "
        "s'il contient des espaces."
    )
    add_para(doc,
        "Le label par defaut (si vous ne specifiez pas --label) est « Compilateur de mail ».",
        italic=True,
    )

    add_heading(doc, "Changer le titre du Google Doc genere", level=2)
    add_para(doc, "Utilisez l'option --title suivi du titre souhaite :")
    add_code_block(doc, 'python main.py --title "Recap mails Mars 2026"')
    add_code_block(doc, 'python main.py --label "Projets" --title "Historique projets"')
    add_para(doc,
        "Si vous ne specifiez pas --title, le document sera nomme automatiquement : "
        "« Compilateur de mail – Compilation mails (AAAA-MM-JJ) » avec la date du jour.",
        italic=True,
    )

    add_heading(doc, "Limiter le nombre d'emails", level=2)
    add_para(doc, "Utilisez l'option --max :")
    add_code_block(doc, "python main.py --max 20")

    add_heading(doc, "Combiner toutes les options", level=2)
    add_code_block(doc, 'python main.py --label "Clients" --max 50 --title "Historique clients"')

    add_heading(doc, "Recapitulatif des options", level=2)

    # Build table
    table = doc.add_table(rows=4, cols=3, style="Light Grid Accent 1")
    headers = ["Option", "Description", "Valeur par defaut"]
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h
    rows_data = [
        ["--label", "Nom du label Gmail a filtrer", "Compilateur de mail"],
        ["--max", "Nombre maximum d'emails", "150"],
        ["--title", "Titre du Google Doc", "Auto (avec la date)"],
    ]
    for r, data in enumerate(rows_data, start=1):
        for c, val in enumerate(data):
            table.rows[r].cells[c].text = val

    add_separator(doc)

    # ===== SECTION 10 =====
    add_heading(doc, "10 — Comprendre le Google Doc genere", level=1)
    add_para(doc, "Le document cree contient, pour chaque email :")
    add_bullet(doc, "Sujet de l'email → formate en Titre 1 (Heading 1)")
    add_bullet(doc, "Corps complet du texte de l'email")
    add_bullet(doc, "Un separateur visuel entre chaque email")
    add_para(doc,
        "Les sujets sont en Titre 1 pour permettre une navigation facile via "
        "le plan du document (menu Outils > Plan dans Google Docs). "
        "Les emails sont dans l'ordre de Gmail (les plus recents en premier).",
    )

    add_separator(doc)

    # ===== SECTION 11 =====
    add_heading(doc, "11 — Depannage", level=1)

    # --- 11.1 ---
    add_heading(doc, '« credentials.json introuvable »', level=2)
    add_code_block(doc, "FileNotFoundError: 'credentials.json' introuvable.")
    add_para(doc,
        "Solution : le fichier credentials.json n'est pas dans le dossier du projet. "
        "Retournez a l'etape 5.3 et placez le fichier au bon endroit.",
        bold=True,
    )

    # --- 11.2 ---
    add_heading(doc, "« Label 'xxx' introuvable dans votre boite Gmail »", level=2)
    add_code_block(doc, "ValueError: Label 'xxx' introuvable dans votre boite Gmail.")
    add_para(doc, "Solution :", bold=True)
    add_bullet(doc, "Verifiez l'orthographe exacte (majuscules/minuscules comptent)")
    add_bullet(doc, "Verifiez que le label existe dans Gmail")
    add_bullet(doc, 'Utilisez les guillemets : --label "Mon Label"')

    # --- 11.3 ---
    add_heading(doc, "« Aucun mail trouve avec ce label »", level=2)
    add_para(doc,
        "Le label existe mais aucun email ne le porte. "
        "Appliquez le label a des emails dans Gmail (voir section 7)."
    )

    # --- 11.4 ---
    add_heading(doc, "« Cette application n'est pas validee » (ecran Google)", level=2)
    add_para(doc,
        "C'est normal. Votre application est en mode « Test ». "
        'Cliquez sur « Continuer » ou « Advanced » > « Go to Gmail Compiler (unsafe) ».'
    )

    # --- 11.5 SUPPRESSION TOKEN.JSON ---
    add_heading(doc, "Erreur « Token has been expired or revoked »", level=2)
    add_para(doc,
        "Cette erreur survient lorsque le jeton d'authentification stocke dans "
        "le fichier token.json n'est plus valide (expire, revoque, ou corrompu)."
    )
    add_para(doc, "Procedure pour supprimer le fichier token.json :", bold=True)

    add_numbered(doc, "Ouvrez l'Invite de commandes Windows (Windows + R → cmd → Entree)")
    add_numbered(doc, "Naviguez vers le dossier du projet :")
    add_code_block(doc, "cd %USERPROFILE%\\Desktop\\Charles-B")
    add_numbered(doc, "Supprimez le fichier token.json :")
    add_para(doc, "Avec la commande Windows :", bold=True)
    add_code_block(doc, "del token.json")
    add_para(doc, "Ou sur Mac / Linux :", bold=True)
    add_code_block(doc, "rm token.json")
    add_numbered(doc,
        "Vous pouvez aussi supprimer le fichier manuellement : "
        "ouvrez le dossier Charles-B dans l'Explorateur de fichiers, "
        "faites un clic droit sur token.json et selectionnez « Supprimer »."
    )
    add_numbered(doc, "Relancez le programme :")
    add_code_block(doc, 'python main.py --label "NOM_DE_VOTRE_LABEL"')
    add_numbered(doc,
        "Le navigateur s'ouvrira a nouveau pour une nouvelle authentification. "
        "Suivez les etapes de la section 8.1."
    )

    add_note(doc,
        "Apres cette operation, un nouveau fichier token.json sera cree automatiquement. "
        "Vous n'avez rien d'autre a faire."
    )

    # --- 11.6 ---
    add_heading(doc, "Erreur « insufficient permission » ou « Access Not Configured »", level=2)
    add_para(doc,
        "Une ou plusieurs APIs ne sont pas activees. "
        "Retournez a la section 4 et verifiez que les 3 APIs sont bien activees :"
    )
    add_bullet(doc, "Gmail API")
    add_bullet(doc, "Google Docs API")
    add_bullet(doc, "Google Drive API")

    # --- 11.7 ---
    add_heading(doc, "pip / python non reconnu", level=2)
    add_bullet(doc, "Windows : utilisez py au lieu de python, ou reinstallez Python en cochant « Add to PATH »")
    add_bullet(doc, "Mac : utilisez python3 et pip3")
    add_bullet(doc, "Linux : sudo apt install python3 python3-pip (Ubuntu/Debian)")

    # --- 11.8 General token.json ---
    add_heading(doc, "En cas de probleme general d'authentification", level=2)
    add_para(doc,
        "Si vous rencontrez tout type d'erreur liee a l'authentification Google, "
        "la premiere chose a essayer est de supprimer le fichier token.json et de "
        "relancer le programme. Cette manipulation force une nouvelle authentification "
        "et resout la majorite des problemes.",
        bold=True,
    )
    add_code_block(doc,
        "REM --- Supprimer token.json et relancer ---\n"
        "del token.json\n"
        'python main.py --label "Mon Label"'
    )

    add_separator(doc)

    # ===== SECTION 12 =====
    add_heading(doc, "12 — Questions frequentes", level=1)

    faqs = [
        ("Est-ce gratuit ?",
         "Oui. Les APIs Google utilisees sont gratuites dans les limites d'usage "
         "quotidiennes (largement suffisantes pour un usage normal)."),
        ("Mes emails sont-ils envoyes quelque part ?",
         "Non. Le programme tourne sur votre machine et accede directement a votre "
         "compte Google. Aucune donnee ne transite par un serveur tiers."),
        ("Puis-je utiliser cet outil pour n'importe quel label ?",
         'Oui. Utilisez l\'option --label "Nom du label" pour specifier le label souhaite.'),
        ("Le programme modifie-t-il mes emails ?",
         "Non. Le programme a uniquement un acces en lecture a Gmail (gmail.readonly). "
         "Il ne peut ni modifier, ni supprimer, ni envoyer d'emails."),
        ("Ou est cree le Google Doc ?",
         "Dans le Google Drive du compte Google utilise pour l'authentification, "
         'a la racine (dossier "Mon Drive").'),
        ("Puis-je relancer le programme plusieurs fois ?",
         "Oui. Chaque execution cree un nouveau Google Doc. "
         "Les documents precedents ne sont pas modifies."),
        ("Dois-je refaire la procedure Google Cloud a chaque fois ?",
         "Non. La configuration Google Cloud et le fichier credentials.json ne sont "
         "a faire qu'une seule fois. Idem pour token.json qui est genere automatiquement "
         "a la premiere execution."),
        ("Puis-je utiliser le meme script pour un autre compte Gmail ?",
         "Oui. Dupliquez le dossier du projet, supprimez le fichier token.json dans "
         "la copie, puis lancez le programme. Le navigateur s'ouvrira et vous pourrez "
         "vous connecter avec l'autre compte Gmail. Le fichier credentials.json peut "
         "rester le meme (il identifie l'application, pas le compte utilisateur)."),
    ]

    for q, a in faqs:
        p = doc.add_paragraph()
        run_q = p.add_run(f"Q : {q}")
        run_q.bold = True
        p2 = doc.add_paragraph()
        p2.paragraph_format.left_indent = Inches(0.3)
        run_a = p2.add_run(a)
        run_a.italic = True

    add_separator(doc)

    # ===== RECAP =====
    add_heading(doc, "Recapitulatif rapide", level=1)
    add_code_block(doc,
        "1. Creer un projet Google Cloud\n"
        "2. Activer 3 APIs (Gmail, Docs, Drive)\n"
        "3. Creer un identifiant OAuth 2.0 (Desktop)\n"
        "4. Telecharger credentials.json dans le dossier du projet\n"
        "5. pip install -r requirements.txt\n"
        '6. python main.py --label "Mon Label"\n'
        "7. Autoriser l'acces dans le navigateur (1ere fois seulement)\n"
        "8. Ouvrir le lien du Google Doc genere"
    )

    # Footer
    doc.add_paragraph()
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Guide cree pour le projet Charles-B — Gmail to Google Doc Compiler")
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(150, 150, 150)

    return doc


if __name__ == "__main__":
    doc = build_document()
    output_path = "Guide_Charles-B_Gmail_Compiler.docx"
    doc.save(output_path)
    print(f"Document genere : {output_path}")
