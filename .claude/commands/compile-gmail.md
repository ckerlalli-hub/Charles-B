# Compile Gmail emails into a Google Doc

Compile les emails Gmail d'un label donné dans un Google Doc.

## Instructions

1. Demande à l'utilisateur le **nom du label Gmail** à traiter (si non fourni via $ARGUMENTS).
2. Demande optionnellement le **nombre max d'emails** et le **titre du document**.
3. Exécute le script Python avec les paramètres fournis :

```bash
cd /home/user/Charles-B && python main.py --label "$LABEL" --max $MAX --title "$TITLE"
```

4. Affiche le lien du Google Doc généré à l'utilisateur.

## Paramètres

- `$ARGUMENTS` : le nom du label Gmail (ex: `/compile-gmail Newsletters`)
- Si aucun argument n'est fourni, utilise le label par défaut "Compilateur de mail"

## Exemple d'utilisation

```
/compile-gmail Newsletters
/compile-gmail "Rapports mensuels"
```

## Exécution

Lance la commande suivante dans le terminal :

```bash
cd /home/user/Charles-B && python main.py --label "${ARGUMENTS:-Compilateur de mail}"
```

Si l'utilisateur précise un nombre max ou un titre, ajoute les options `--max` et `--title` correspondantes.

Affiche ensuite le lien du Google Doc généré.
