# Pharmacies Gabon

Plateforme complète de référencement des pharmacies au Gabon. Trouvez facilement les pharmacies de garde, les contacts d'urgence et les établissements pharmaceutiques dans toutes les villes gabonaises.

## Fonctionnalités

### Pour les utilisateurs
- **Recherche de pharmacies** : Trouvez une pharmacie par nom, ville ou quartier
- **Pharmacies de garde** : Identifiez rapidement les pharmacies ouvertes 24h/24
- **Carte interactive** : Localisez les pharmacies sur une carte OpenStreetMap
- **Contacts d'urgence** : Accédez aux numéros d'urgence nationaux et par ville (police, pompiers, hôpitaux)
- **Numéros cliquables** : Appelez directement en cliquant sur les numéros de téléphone
- **Contribution communautaire** : Proposez des corrections, ajoutez des localisations GPS ou suggérez de nouvelles pharmacies

### Pour les administrateurs
- **Tableau de bord** : Vue d'ensemble des pharmacies, statistiques et contributions en attente
- **Gestion des pharmacies** : Ajouter, modifier, supprimer des établissements
- **Système de garde** : Activer/désactiver le statut de garde avec dates
- **Validation GPS** : Approuver les localisations soumises par les utilisateurs
- **Contacts d'urgence** : Gérer les numéros d'urgence par ville
- **Popups** : Créer des messages popup pour les visiteurs (avec bloc d'avertissement)
- **Paramètres du site** : Configurer le nom, logo, favicon, SEO/OpenGraph

## Technologies

- **Backend** : Python 3.11, Flask, SQLAlchemy
- **Base de données** : PostgreSQL
- **Frontend** : HTML5, Tailwind CSS, JavaScript
- **Carte** : Leaflet.js avec OpenStreetMap
- **Authentification** : Flask-Login

## Documentation

Toute la documentation est disponible dans le dossier `/docs` :

- [Documentation Commerciale (EN)](docs/COMMERCIAL.md) - Présentation commerciale en anglais
- [Documentation API](docs/API.md) - Référence complète de l'API
- [Architecture Technique](docs/ARCHITECTURE.md) - Architecture et modèles de données
- [Guide Administrateur](docs/ADMIN_GUIDE.md) - Guide du panneau d'administration

## Installation

### Prérequis
- Python 3.11+
- PostgreSQL
- pip

### Configuration

1. Clonez le repository :
```bash
git clone <repository-url>
cd pharmacies-gabon
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez les variables d'environnement :
```bash
export DATABASE_URL="postgresql://your_user:your_password@your_host/your_database"
export SESSION_SECRET="your-secure-secret-key"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="your-secure-password"
```

> **Note**: Remplacez les valeurs ci-dessus par vos propres informations de connexion sécurisées.

4. Initialisez la base de données avec les données de démonstration :
```bash
python init_demo.py
```

Pour réinitialiser les données (supprime et recrée) :
```bash
python init_demo.py --force
```

5. Lancez l'application :
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Structure du projet

```
├── app.py                  # Configuration Flask et initialisation
├── main.py                 # Point d'entrée de l'application
├── extensions.py           # Extensions Flask (db, login_manager)
├── init_demo.py            # Script d'initialisation des données de démonstration
├── models/
│   ├── pharmacy.py         # Modèle Pharmacie
│   ├── admin.py            # Modèle Administrateur
│   ├── emergency_contact.py # Modèle Contacts d'urgence
│   ├── site_settings.py    # Modèle Paramètres et Popups
│   └── submission.py       # Modèles de soumissions utilisateurs
├── routes/
│   ├── public.py           # Routes publiques (API et pages)
│   └── admin.py            # Routes d'administration
├── services/
│   └── pharmacy_service.py # Logique métier des pharmacies
├── security/
│   └── auth.py             # Authentification et gestion des admins
├── templates/
│   ├── index.html          # Page principale
│   └── admin/              # Templates d'administration
├── static/
│   ├── js/app.js           # JavaScript principal
│   ├── favicon.svg         # Favicon
│   └── ...
├── utils/
│   └── helpers.py          # Fonctions utilitaires et coordonnées GPS
└── docs/                   # Documentation
    ├── COMMERCIAL.md       # Documentation commerciale (EN)
    ├── API.md              # Documentation API
    ├── ARCHITECTURE.md     # Architecture technique
    └── ADMIN_GUIDE.md      # Guide administrateur
```

## Données de démonstration

Le script `init_demo.py` charge :
- **87 pharmacies** réparties dans toutes les villes du Gabon
- **18 contacts d'urgence** (nationaux et par ville)
- **1 popup de bienvenue** avec message d'avertissement
- **1 compte administrateur** depuis les variables d'environnement

### Villes couvertes
- Libreville (capitale)
- Port-Gentil
- Franceville
- Oyem
- Mouila
- Moanda
- Makokou
- Koulamoutou
- Ntom

## Administration

### Accès
- URL : `/admin`
- Identifiants : Configurés via les secrets `ADMIN_USERNAME` et `ADMIN_PASSWORD`

### Fonctionnalités admin
1. **Tableau de bord** : Statistiques et aperçu global
2. **Pharmacies** : CRUD complet avec gestion de garde
3. **Localisations** : Validation des positions GPS soumises
4. **Corrections** : Approbation des modifications d'informations
5. **Suggestions** : Réponse aux suggestions des utilisateurs
6. **Nouvelles pharmacies** : Validation des propositions
7. **Contacts d'urgence** : Gestion des numéros d'urgence
8. **Popups** : Création et gestion des messages popup
9. **Paramètres** : Configuration du site et SEO

## API

Voir la [documentation API complète](docs/API.md) pour tous les détails.

### Endpoints publics
- `GET /api/pharmacies` : Liste des pharmacies (avec filtres)
- `GET /api/stats` : Statistiques générales
- `GET /api/popups` : Popups actifs
- `POST /api/pharmacy/<id>/view` : Enregistrer une consultation
- `POST /api/pharmacy/<id>/submit-location` : Soumettre une localisation
- `POST /api/pharmacy/<id>/submit-info` : Soumettre une correction
- `POST /api/suggestions` : Envoyer une suggestion
- `POST /api/pharmacy-proposal` : Proposer une nouvelle pharmacie

## Contribution

Les contributions sont les bienvenues ! Vous pouvez :
1. Ajouter des pharmacies manquantes via l'interface
2. Corriger les informations inexactes
3. Soumettre des localisations GPS précises
4. Signaler des bugs ou proposer des améliorations

## Licence

Ce projet est sous licence MIT.

## Contact

Pour toute question ou suggestion, utilisez la boîte à suggestions intégrée à l'application.
