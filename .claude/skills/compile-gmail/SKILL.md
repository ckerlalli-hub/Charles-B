---
name: compile-gmail
description: Compile les emails Gmail d'un label dans un Google Doc. Utiliser quand l'utilisateur veut compiler, rassembler, regrouper ou exporter des emails Gmail dans un document Google Doc.
argument-hint: "[label-gmail]"
disable-model-invocation: false
---

# Compiler des emails Gmail dans un Google Doc

Recupere les emails Gmail d'un label donne et les compile dans un Google Doc formate avec titres et separateurs.

## Parametres

| Parametre       | Source        | Defaut                | Description                          |
|-----------------|---------------|-----------------------|--------------------------------------|
| **Label Gmail** | `$ARGUMENTS`  | `Compilateur de mail` | Le nom du label Gmail a traiter      |
| **Nombre max**  | Demander      | `150`                 | Nombre maximum d'emails a recuperer  |
| **Titre du doc**| Demander      | Auto (avec date)      | Titre personnalise du Google Doc     |

- Si `$ARGUMENTS` est fourni, l'utiliser comme nom du label Gmail.
- Si aucun argument, demander a l'utilisateur ou utiliser le defaut.

## Verification des prerequis

Avant de lancer, verifier :

1. Que `credentials.json` existe :

```bash
cd /home/user/Charles-B && test -f credentials.json && echo "OK" || echo "MISSING"
```

Si manquant, informer l'utilisateur :
> Telechargez `credentials.json` depuis la Google Cloud Console (APIs & Services > Credentials > OAuth 2.0 Client ID) et placez-le a la racine du projet `/home/user/Charles-B/`.

2. Que les dependances Python sont installees :

```bash
cd /home/user/Charles-B && pip install -q -r requirements.txt 2>&1
```

## Execution

Lancer le script avec les parametres collectes :

```bash
cd /home/user/Charles-B && python main.py --label "${ARGUMENTS:-Compilateur de mail}" --max 150
```

Ajouter `--max <nombre>` si l'utilisateur a precise un nombre max.
Ajouter `--title "<titre>"` si l'utilisateur a precise un titre.

## Presentation du resultat

- Afficher le **lien du Google Doc** genere.
- Indiquer le **nombre d'emails** compiles.

## Gestion des erreurs

| Erreur                            | Solution                                                                 |
|-----------------------------------|--------------------------------------------------------------------------|
| `credentials.json introuvable`    | Telecharger depuis Google Cloud Console                                  |
| `Label 'xxx' introuvable`        | Verifier l'orthographe exacte dans Gmail (sensible a la casse)           |
| `Aucun mail trouve`              | Appliquer le label a des emails dans Gmail                               |
| `Token expired or revoked`       | Supprimer `token.json` et relancer                                       |
| `insufficient permission`        | Verifier que les 3 APIs sont activees : Gmail, Docs, Drive               |
