# Compilateur de mail – Gmail → Google Doc Compiler

Récupère les mails Gmail ayant le label **« Compilateur de mail »** et compile leur contenu (titre, aperçu, corps, images) dans un Google Doc sur votre Drive.

## Prérequis

- Python 3.10+
- Un projet Google Cloud avec les APIs suivantes activées :
  - **Gmail API**
  - **Google Docs API**
  - **Google Drive API**

## Installation

```bash
pip install -r requirements.txt
```

## Configuration Google Cloud

1. Rendez-vous sur [Google Cloud Console](https://console.cloud.google.com/).
2. Créez un projet (ou sélectionnez-en un existant).
3. Activez les APIs : **Gmail API**, **Google Docs API**, **Google Drive API**.
4. Allez dans **APIs & Services → Credentials**.
5. Créez un **OAuth 2.0 Client ID** de type **Desktop application**.
6. Téléchargez le fichier JSON et placez-le à la racine du projet sous le nom **`credentials.json`**.

## Utilisation

```bash
python main.py
```

Au premier lancement, un navigateur s'ouvrira pour vous authentifier avec votre compte Google. Le token sera sauvegardé dans `token.json` pour les exécutions suivantes.

### Options

| Option      | Description                                     | Défaut        |
|-------------|-------------------------------------------------|---------------|
| `--label`   | Nom du label Gmail à filtrer                    | `Compilateur de mail`   |
| `--max`     | Nombre maximum de mails à récupérer             | `50`          |
| `--title`   | Titre personnalisé pour le Google Doc           | Auto (+ date) |

### Exemples

```bash
# Utilisation par défaut
python main.py

# Limiter à 10 mails
python main.py --max 10

# Utiliser un autre label
python main.py --label "Mon Autre Label"

# Titre personnalisé
python main.py --title "Recap mails février 2026"
```

## Structure du projet

```
├── auth.py             # Authentification OAuth2 Google
├── gmail_service.py    # Récupération des mails via Gmail API
├── gdoc_compiler.py    # Création du Google Doc via Docs API + Drive API
├── main.py             # Point d'entrée CLI
├── requirements.txt    # Dépendances Python
└── credentials.json    # (à fournir) Vos identifiants OAuth2
```

## Google Doc généré

Pour chaque mail, le document contient :
- **Titre** (Heading 1) : le sujet du mail
- **Aperçu** (italique) : le snippet/preview Gmail
- **Corps** : le texte complet du mail
- **Images** : les images embarquées dans le mail
- Saut de page entre chaque mail
