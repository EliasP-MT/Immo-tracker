# 🏠 Immo Tracker

Suit automatiquement le prix du m² sur MeilleursAgents et envoie un rapport
par email avec une courbe tous les 3 mois. Fonctionne 100% via GitHub Actions —
pas besoin de serveur.

---

## Structure du projet

```
immo-tracker/
├── .github/workflows/tracker.yml   ← automatisation GitHub Actions
├── data/prices.csv                 ← historique des prix (géré auto)
├── scraper.py                      ← collecte le prix chaque semaine
├── report.py                       ← génère la courbe + envoie l'email
└── requirements.txt
```

---

## Installation (une seule fois)

### 1. Créer le repo GitHub

1. Va sur [github.com/new](https://github.com/new)
2. Nom : `immo-tracker`
3. Visibilité : **Private** (recommandé — tes données y seront stockées)
4. Clique **Create repository**

### 2. Pousser le projet depuis VS Code

Ouvre un terminal dans VS Code (`Ctrl+ù`) et tape :

```bash
cd chemin\vers\immo-tracker        # ex: cd C:\Users\TonNom\immo-tracker
git init
git add .
git commit -m "init: immo tracker"
git branch -M main
git remote add origin https://github.com/TON_PSEUDO/immo-tracker.git
git push -u origin main
```

### 3. Créer un mot de passe d'application Gmail

> Gmail ne permet pas d'utiliser ton vrai mot de passe depuis un script.
> Il faut créer un "mot de passe d'application" dédié.

1. Va sur [myaccount.google.com/security](https://myaccount.google.com/security)
2. Active la **validation en deux étapes** si ce n'est pas déjà fait
3. Cherche **"Mots de passe des applications"** (ou va sur
   [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords))
4. Crée un mot de passe → nom : `immo-tracker`
5. Copie le mot de passe généré (16 caractères, ex: `abcd efgh ijkl mnop`)

### 4. Ajouter les secrets GitHub

Dans ton repo GitHub :
`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Nom du secret    | Valeur                              |
|------------------|-------------------------------------|
| `GMAIL_USER`     | ton adresse Gmail (ex: toi@gmail.com) |
| `GMAIL_APP_PASS` | le mot de passe d'application (16 car.) |
| `EMAIL_TO`       | l'adresse email destinataire        |

### 5. Activer les permissions d'écriture pour GitHub Actions

Dans ton repo :
`Settings` → `Actions` → `General` → `Workflow permissions`
→ Sélectionne **"Read and write permissions"** → Save

---

## Utilisation

### Fonctionnement automatique

- **Chaque lundi à 8h** : le script scrape le prix et l'ajoute au CSV
- **Le 1er janvier, avril, juillet, octobre** : envoi de l'email avec la courbe

### Tester manuellement

Sur GitHub : `Actions` → `Immo Tracker` → `Run workflow`
→ Met `oui` dans le champ `force_report` pour déclencher aussi l'email.

### Voir l'historique des prix

Le fichier `data/prices.csv` dans ton repo contient tout l'historique.
Tu peux l'ouvrir dans Excel directement.

---

## En cas de problème

- **Le scraping échoue** : MeilleursAgents a peut-être changé sa structure HTML.
  Ouvre un ticket ou modifie le regex dans `scraper.py`.
- **L'email n'arrive pas** : vérifie les secrets GitHub + le mot de passe d'appli Gmail.
- **Logs** : va dans `Actions` → clique sur le dernier run → détaille chaque étape.
