# Archilog - Gestion de Cagnotte

Ce projet est une application de gestion de dépenses partagées ("qui doit combien à qui") développée pour le cours d'Architecture Logicielle. Elle met en œuvre une architecture logicielle robuste et modulaire en Python.

## Architecture du Projet

L'application respecte une architecture **n-tier** pour assurer la séparation des responsabilités :

* **Couche Présentation (Views)** :
    * **CLI** : Interface en ligne de commande développée avec `Click`.
    * **Web (GUI)** : Interface utilisateur développée avec `Flask` et les templates `Jinja2`.

* **Couche Domaine (Domain)** : Logique métier (calcul des remboursements, règles de validation) centralisée dans `functions.py`.

* **Couche Données (Data)** : Accès aux données via **SQLAlchemy Core** (sans ORM, comme requis).

* **Couche Stockage (Storage)** : Persistance dans une base de données **SQLite**.

## Technologies Utilisées

* **Langage** : Python 3.11+.
* **Web Framework** : Flask (Pattern Application Factory & Blueprints).
* **CLI Framework** : Click.
* **Base de données** : SQLite & SQLAlchemy Core.
* **Gestionnaire de projet** : `uv`.

## Installation

1. Assurez-vous d'avoir `uv` installé sur votre système.
2. Clonez le dépôt et installez les dépendances :

```powershell
uv sync
```

## Configuration

L'application utilise une configuration centralisée via une `dataclass`. Les paramètres sont récupérés depuis les variables d'environnement, permettant de séparer le code de la configuration technique.

| Variable | Description | Valeur par défaut |
| --- | --- | --- |
| `ARCHILOG_DATABASE_URL` | URL de connexion à la base SQL | `sqlite:///data.db` |
| `ARCHILOG_DEBUG` | Active le mode debug et l'écho SQL | `False` |
| `ARCHILOG_SECRET_KEY` | Clé pour la sécurité des sessions Flask | `dev_secret_key` |

## Utilisation

### Interface Web (Flask)

L'interface web est lancée via une Application Factory.

**Sur Windows (PowerShell) :**

```powershell
$env:FLASK_APP = "archilog.views:create_app"
$env:ARCHILOG_DEBUG = "True"
uv run flask run --debug
```

**Sur Linux/macOS :**

```bash
export FLASK_APP="archilog.views:create_app"
export ARCHILOG_DEBUG="True"
uv run flask run --debug
```

Accédez ensuite à l'adresse : `http://127.0.0.1:5000`.

### Interface Ligne de Commande (CLI)

L'interface CLI est accessible directement via la commande définie dans le `pyproject.toml` :

```powershell
# Créer une cagnotte
uv run archilog create --name "VACANCES"

# Afficher le bilan des remboursements
uv run archilog bilan --name "VACANCES"
```

## Structure des fichiers

```text
src/archilog/
├── app.py          # Factory de l'application Flask
├── config.py       # Configuration centralisée (os.getenv)
├── models.py       # Schémas SQL (SQLAlchemy Core)
├── functions.py    # Logique métier (Domain)
├── views.py        # Routeur Web (Blueprint)
├── __init__.py     # Point d'entrée CLI (Click)
└── templates/      # Templates Jinja2
```
