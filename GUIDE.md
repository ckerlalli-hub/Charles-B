# Guide complet : Compiler des emails Gmail dans un Google Doc

Ce guide vous accompagne pas-a-pas pour installer et utiliser l'outil **Charles-B**, qui recupere automatiquement les emails d'un label Gmail et les compile dans un Google Doc sur votre Drive.

---

## Table des matieres

1. [Ce que fait l'outil](#1--ce-que-fait-loutil)
2. [Pre-requis](#2--pre-requis)
3. [Creer un projet Google Cloud](#3--creer-un-projet-google-cloud)
4. [Activer les APIs necessaires](#4--activer-les-apis-necessaires)
5. [Creer les identifiants OAuth 2.0](#5--creer-les-identifiants-oauth-20)
6. [Installer le projet sur votre machine](#6--installer-le-projet-sur-votre-machine)
7. [Preparer votre boite Gmail](#7--preparer-votre-boite-gmail)
8. [Lancer le programme](#8--lancer-le-programme)
9. [Options avancees](#9--options-avancees)
10. [Comprendre le Google Doc genere](#10--comprendre-le-google-doc-genere)
11. [Depannage](#11--depannage)
12. [Questions frequentes](#12--questions-frequentes)

---

## 1 — Ce que fait l'outil

L'outil :
1. Se connecte a votre compte Gmail via l'API Google
2. Recupere tous les emails portant un **label** de votre choix
3. Cree un **Google Doc** sur votre Drive
4. Y insere le contenu de chaque email : sujet (en titre), corps du texte
5. Vous donne le **lien direct** vers le document

Resultat : un document unique, proprement formate, contenant tous vos emails.

---

## 2 — Pre-requis

Avant de commencer, assurez-vous d'avoir :

- [ ] Un **compte Google** (Gmail)
- [ ] **Python 3.10 ou superieur** installe sur votre machine
- [ ] **Git** installe (pour cloner le projet)
- [ ] Un acces a Internet

### Verifier votre version de Python

Ouvrez un terminal (ou l'Invite de commandes / PowerShell sous Windows) et tapez :

```bash
python --version
```

Vous devez voir `Python 3.10.x` ou superieur. Si ce n'est pas le cas, telechargez Python depuis [python.org](https://www.python.org/downloads/).

> **Windows** : lors de l'installation de Python, cochez la case **"Add Python to PATH"**.

---

## 3 — Creer un projet Google Cloud

L'outil utilise les APIs officielles de Google. Il faut creer un projet gratuit sur Google Cloud pour obtenir les autorisations.

### Etape par etape :

1. Rendez-vous sur **[Google Cloud Console](https://console.cloud.google.com/)**
2. Connectez-vous avec votre compte Google
3. En haut de la page, cliquez sur le **selecteur de projet** (a cote du logo Google Cloud)
4. Cliquez sur **"Nouveau projet"**
5. Donnez-lui un nom (par exemple : `Gmail-Compiler`)
6. Cliquez sur **"Creer"**
7. Attendez quelques secondes, puis selectionnez votre nouveau projet

---

## 4 — Activer les APIs necessaires

Le programme a besoin de 3 APIs Google. Il faut les activer une par une.

### Etape par etape :

1. Dans le menu lateral gauche, allez dans **"APIs et services" > "Bibliotheque"**
   (ou cherchez "API Library" dans la barre de recherche)

2. **Gmail API** :
   - Cherchez `Gmail API` dans la barre de recherche
   - Cliquez dessus
   - Cliquez sur **"Activer"**

3. **Google Docs API** :
   - Cherchez `Google Docs API`
   - Cliquez dessus
   - Cliquez sur **"Activer"**

4. **Google Drive API** :
   - Cherchez `Google Drive API`
   - Cliquez dessus
   - Cliquez sur **"Activer"**

> **Astuce** : si le bouton indique "Gerer" au lieu de "Activer", c'est que l'API est deja activee.

---

## 5 — Creer les identifiants OAuth 2.0

C'est l'etape la plus importante : elle permet au programme de se connecter a votre compte Google de maniere securisee.

### 5.1 — Configurer l'ecran de consentement OAuth

1. Allez dans **"APIs et services" > "Ecran de consentement OAuth"**
2. Selectionnez **"Externe"** comme type d'utilisateur
3. Cliquez sur **"Creer"**
4. Remplissez les champs obligatoires :
   - **Nom de l'application** : `Gmail Compiler` (ou ce que vous voulez)
   - **Adresse e-mail d'assistance** : votre adresse Gmail
   - **Adresses e-mail du developpeur** : votre adresse Gmail
5. Cliquez sur **"Enregistrer et continuer"**
6. A l'etape **"Champs d'application"** (Scopes), cliquez sur **"Enregistrer et continuer"** sans rien ajouter
7. A l'etape **"Utilisateurs de test"**, cliquez sur **"Ajouter des utilisateurs"** et ajoutez **votre propre adresse Gmail**
8. Cliquez sur **"Enregistrer et continuer"**

> **Important** : tant que l'application est en mode "Test", seuls les utilisateurs de test que vous avez ajoutes peuvent l'utiliser. C'est normal et suffisant pour un usage personnel.

### 5.2 — Creer le Client ID OAuth

1. Allez dans **"APIs et services" > "Identifiants"** (ou "Credentials")
2. Cliquez sur **"+ Creer des identifiants"** en haut
3. Selectionnez **"ID client OAuth"**
4. **Type d'application** : selectionnez **"Application de bureau"** (Desktop app)
5. **Nom** : `Gmail Compiler Desktop` (ou ce que vous voulez)
6. Cliquez sur **"Creer"**

### 5.3 — Telecharger le fichier credentials.json

1. Une fenetre apparait avec votre Client ID. Cliquez sur **"Telecharger le fichier JSON"**
2. Un fichier est telecharge (son nom ressemble a `client_secret_XXXXX.json`)
3. **Renommez ce fichier en `credentials.json`**
4. Gardez-le de cote, vous le placerez dans le dossier du projet a l'etape suivante

---

## 6 — Installer le projet sur votre machine

### 6.1 — Cloner le projet

Ouvrez un terminal et tapez :

```bash
git clone https://github.com/VOTRE-UTILISATEUR/Charles-B.git
cd Charles-B
```

> Remplacez `VOTRE-UTILISATEUR` par le nom d'utilisateur GitHub ou l'URL qui vous a ete communiquee.

### 6.2 — Placer le fichier credentials.json

Copiez le fichier `credentials.json` (telecharge a l'etape 5.3) **a la racine du dossier du projet** :

```
Charles-B/
├── auth.py
├── gmail_service.py
├── gdoc_compiler.py
├── main.py
├── requirements.txt
├── credentials.json     <-- ICI
└── ...
```

- **Windows** : copiez-collez le fichier dans le dossier `Charles-B`
- **Mac/Linux** : `cp ~/Downloads/credentials.json ./credentials.json`

### 6.3 — Installer les dependances Python

Toujours dans le dossier du projet :

```bash
pip install -r requirements.txt
```

Cela installe les bibliotheques necessaires :
- `google-api-python-client` — SDK Google APIs
- `google-auth-httplib2` — Transport HTTP pour l'authentification
- `google-auth-oauthlib` — Gestion du flux OAuth2
- `beautifulsoup4` — Extraction du texte depuis le HTML des emails

> **Astuce** : si vous avez plusieurs versions de Python, utilisez `pip3` au lieu de `pip`.

---

## 7 — Preparer votre boite Gmail

Le programme filtre les emails par **label Gmail**. Vous devez donc avoir un label applique aux emails que vous souhaitez compiler.

### Creer un label (si necessaire) :

1. Ouvrez **[Gmail](https://mail.google.com)**
2. Dans le menu lateral gauche, cliquez sur **"Plus"** puis **"Creer un libelle"**
3. Entrez le nom souhaite (par exemple : `Newsletters`, `Rapports`, `Charles B`)
4. Cliquez sur **"Creer"**

### Appliquer le label a des emails :

1. Selectionnez les emails souhaites (cases a cocher)
2. Cliquez sur l'icone **"Libelles"** (l'etiquette en haut)
3. Cochez le label que vous venez de creer
4. Cliquez sur **"Appliquer"**

> **Note** : le nom du label est **sensible a la casse**. `Newsletter` et `newsletter` sont deux labels differents. Notez bien l'orthographe exacte.

---

## 8 — Lancer le programme

### 8.1 — Premiere execution (authentification)

Dans le terminal, depuis le dossier du projet :

```bash
python main.py --label "NOM_DE_VOTRE_LABEL"
```

Remplacez `NOM_DE_VOTRE_LABEL` par le nom exact de votre label Gmail.

**Ce qui va se passer :**

1. Votre **navigateur s'ouvre** automatiquement sur une page Google
2. Selectionnez votre **compte Google**
3. Un avertissement s'affiche ("Cette application n'est pas validee") — c'est normal
4. Cliquez sur **"Continuer"** (ou "Advanced" > "Go to Gmail Compiler")
5. **Acceptez les 3 permissions demandees** :
   - Lecture de vos emails Gmail
   - Creation de documents Google Docs
   - Gestion de fichiers sur Google Drive
6. La fenetre se ferme, le programme continue dans le terminal

Un fichier `token.json` est cree automatiquement. **Lors des prochaines executions, le navigateur ne s'ouvrira plus.**

### 8.2 — Resultats

Le terminal affiche la progression :

```
Recuperation des mails avec le label « Mon Label »…
42 mail(s) trouve(s). Compilation dans un Google Doc…
  Insertion de 28543 caracteres dans le document…
  Application du formatage (42 titres)…
Termine ! Votre document est disponible ici :
  https://docs.google.com/document/d/XXXXXXXXX/edit
```

**Cliquez sur le lien** pour ouvrir votre Google Doc !

---

## 9 — Options avancees

### Parametres disponibles

| Parametre   | Description                               | Valeur par defaut                        |
|-------------|-------------------------------------------|------------------------------------------|
| `--label`   | Nom du label Gmail a filtrer              | `Charles B`                              |
| `--max`     | Nombre maximum d'emails a recuperer       | `150`                                    |
| `--title`   | Titre personnalise pour le Google Doc     | Auto : `Charles B – Compilation mails (YYYY-MM-DD)` |

### Exemples d'utilisation

```bash
# Compiler les emails du label "Newsletters" (max 150)
python main.py --label "Newsletters"

# Compiler seulement les 20 derniers emails
python main.py --label "Rapports" --max 20

# Donner un titre personnalise au document
python main.py --label "Projets" --title "Recap projet Mars 2026"

# Combiner toutes les options
python main.py --label "Clients" --max 50 --title "Historique clients"
```

---

## 10 — Comprendre le Google Doc genere

Le document cree contient, pour chaque email :

```
┌─────────────────────────────────────────────┐
│  Sujet de l'email          ← Titre (H1)    │
│                                             │
│  Corps complet du texte    ← Texte normal   │
│  de l'email...                              │
│                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━  ← Separateur    │
│                                             │
│  Sujet de l'email suivant  ← Titre (H1)    │
│  ...                                        │
└─────────────────────────────────────────────┘
```

- Les **sujets** sont formates en **Titre 1** (Heading 1) pour une navigation facile
- Un **separateur** visuel separe chaque email
- Les emails sont dans l'ordre de Gmail (les plus recents en premier)

---

## 11 — Depannage

### "credentials.json introuvable"

```
FileNotFoundError: 'credentials.json' introuvable.
```

**Solution** : le fichier `credentials.json` n'est pas dans le dossier du projet. Retournez a l'[etape 5.3](#53--telecharger-le-fichier-credentialsjson) et placez le fichier au bon endroit.

---

### "Label 'xxx' introuvable dans votre boite Gmail"

```
ValueError: Label 'xxx' introuvable dans votre boite Gmail.
```

**Solution** : le nom du label n'est pas correct. Verifiez dans Gmail :
- L'orthographe exacte (majuscules/minuscules comptent)
- Que le label existe bien
- Utilisez les guillemets si le nom contient des espaces : `--label "Mon Label"`

---

### "Aucun mail trouve avec ce label"

**Solution** : le label existe mais aucun email ne le porte. Appliquez le label a des emails dans Gmail (voir [etape 7](#7--preparer-votre-boite-gmail)).

---

### "Cette application n'est pas validee" (ecran Google)

C'est **normal**. Votre application est en mode "Test". Cliquez sur "Continuer" ou "Advanced" > "Go to Gmail Compiler (unsafe)".

---

### Erreur "Token has been expired or revoked"

**Solution** : supprimez le fichier `token.json` et relancez le programme :

```bash
# Windows
del token.json

# Mac / Linux
rm token.json
```

Puis relancez `python main.py`. Le navigateur s'ouvrira a nouveau pour une nouvelle authentification.

---

### Erreur "insufficient permission" ou "Access Not Configured"

**Solution** : une ou plusieurs APIs ne sont pas activees. Retournez a l'[etape 4](#4--activer-les-apis-necessaires) et verifiez que les 3 APIs sont bien activees :
- Gmail API
- Google Docs API
- Google Drive API

---

### pip / python non reconnu

- **Windows** : utilisez `py` au lieu de `python`, ou reinstallez Python en cochant "Add to PATH"
- **Mac** : utilisez `python3` et `pip3`
- **Linux** : `sudo apt install python3 python3-pip` (Ubuntu/Debian)

---

## 12 — Questions frequentes

**Q : Est-ce gratuit ?**
> Oui. Les APIs Google utilisees sont gratuites dans les limites d'usage quotidiennes (largement suffisantes pour un usage normal).

**Q : Mes emails sont-ils envoyes quelque part ?**
> Non. Le programme tourne **sur votre machine** et accede directement a votre compte Google. Aucune donnee ne transite par un serveur tiers.

**Q : Puis-je utiliser cet outil pour n'importe quel label ?**
> Oui. Utilisez l'option `--label "Nom du label"` pour specifier le label souhaite.

**Q : Le programme modifie-t-il mes emails ?**
> Non. Le programme a uniquement un acces en **lecture** a Gmail (`gmail.readonly`). Il ne peut ni modifier, ni supprimer, ni envoyer d'emails.

**Q : Ou est cree le Google Doc ?**
> Dans le Google Drive du compte Google utilise pour l'authentification, a la racine (dossier "Mon Drive").

**Q : Puis-je relancer le programme plusieurs fois ?**
> Oui. Chaque execution cree un **nouveau** Google Doc. Les documents precedents ne sont pas modifies.

**Q : Dois-je refaire la procedure Google Cloud a chaque fois ?**
> Non. La configuration Google Cloud et le fichier `credentials.json` ne sont a faire **qu'une seule fois**. Idem pour `token.json` qui est genere automatiquement a la premiere execution.

---

## Recapitulatif rapide

```
1. Creer un projet Google Cloud
2. Activer 3 APIs (Gmail, Docs, Drive)
3. Creer un identifiant OAuth 2.0 (Desktop)
4. Telecharger credentials.json dans le dossier du projet
5. pip install -r requirements.txt
6. python main.py --label "Mon Label"
7. Autoriser l'acces dans le navigateur (1ere fois seulement)
8. Ouvrir le lien du Google Doc genere
```

---

*Guide cree pour le projet Charles-B — Gmail to Google Doc Compiler*
