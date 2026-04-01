# Compile Gmail emails into a Google Doc

Compile les emails Gmail d'un label donné dans un Google Doc formaté.

## Déclenchement

Cette skill se déclenche quand l'utilisateur demande de :
- Compiler, rassembler ou regrouper des emails Gmail
- Créer un Google Doc à partir d'emails
- Exporter des emails d'un label Gmail

## Instructions

### 1. Collecter les paramètres

Récupère les informations suivantes auprès de l'utilisateur (ou depuis `$ARGUMENTS`) :

| Paramètre       | Obligatoire | Défaut                    | Description                          |
|------------------|-------------|---------------------------|--------------------------------------|
| **Label Gmail**  | Non         | `Compilateur de mail`     | Le nom du label Gmail à traiter      |
| **Nombre max**   | Non         | `150`                     | Nombre maximum d'emails à récupérer  |
| **Titre du doc** | Non         | Auto (avec date du jour)  | Titre personnalisé du Google Doc     |

- Si `$ARGUMENTS` est fourni, l'utiliser comme nom du label Gmail.
- Si aucun argument n'est fourni, demander à l'utilisateur quel label utiliser, ou utiliser le défaut.

### 2. Vérifier les prérequis

Avant de lancer la compilation, vérifie que :

```bash
cd /home/user/Charles-B && test -f credentials.json && echo "OK" || echo "MISSING"
```

- Si `credentials.json` est manquant, informe l'utilisateur qu'il doit le télécharger depuis la Google Cloud Console (APIs & Services > Credentials > OAuth 2.0 Client ID) et le placer à la racine du projet.
- Vérifie aussi que les dépendances sont installées :

```bash
cd /home/user/Charles-B && pip install -q -r requirements.txt 2>&1
```

### 3. Lancer la compilation

Exécute le script Python avec les paramètres collectés :

```bash
cd /home/user/Charles-B && python main.py --label "${ARGUMENTS:-Compilateur de mail}" --max 150
```

Si l'utilisateur a précisé un nombre max d'emails, ajoute `--max <nombre>`.
Si l'utilisateur a précisé un titre, ajoute `--title "<titre>"`.

### 4. Présenter le résultat

- Affiche le **lien du Google Doc** généré à l'utilisateur.
- Indique le nombre d'emails compilés.
- Si une erreur survient, aide l'utilisateur à la résoudre :
  - **"Label introuvable"** → vérifier l'orthographe exacte (sensible à la casse) dans Gmail
  - **"Token expired"** → supprimer `token.json` et relancer
  - **"credentials.json introuvable"** → voir étape 2
  - **"insufficient permission"** → vérifier que les 3 APIs sont activées (Gmail, Docs, Drive)

## Exemples d'utilisation

```
/compile-gmail
/compile-gmail Newsletters
/compile-gmail "Rapports mensuels"
```
