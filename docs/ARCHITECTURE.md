# Architecture technique

Ce document explique comment le code est organisé et comment les différentes parties communiquent entre elles.

## Vue d'ensemble

L'application suit une architecture classique web :

```
Navigateur (HTML/CSS/JS)
        ↓
Serveur Gunicorn (port 5000)
        ↓
Application Flask
        ↓
Base PostgreSQL
```

Le frontend est servi directement par Flask via des templates Jinja2. Pas de framework JS lourd, juste du JavaScript modulaire pour les interactions.

## Structure des fichiers

```
pharmacies-gabon/
│
├── app.py                    # Configuration de Flask
├── main.py                   # Point d'entrée (importe app)
├── extensions.py             # Initialisation des extensions
│
├── models/                   # Définition des données
│   ├── admin.py              # Comptes administrateur
│   ├── pharmacy.py           # Pharmacies
│   ├── emergency_contact.py  # Numéros d'urgence
│   ├── submission.py         # Contributions utilisateurs
│   ├── site_settings.py      # Configuration du site
│   └── advertisement.py      # Publicités
│
├── routes/                   # Points d'accès HTTP
│   ├── public.py             # Pages et API publiques
│   └── admin/                # Administration (découpé en modules)
│       ├── auth.py           # Connexion/déconnexion
│       ├── dashboard.py      # Tableau de bord
│       ├── pharmacy.py       # CRUD pharmacies
│       ├── submissions.py    # Validation des soumissions
│       ├── emergency.py      # Contacts d'urgence
│       ├── settings.py       # Paramètres du site
│       └── ads.py            # Gestion des pubs
│
├── services/                 # Logique métier
│   └── pharmacy_service.py   # Opérations sur les pharmacies
│
├── security/                 # Authentification
│   └── auth.py               # Configuration Flask-Login
│
├── templates/                # Pages HTML (Jinja2)
│   ├── index.html            # Page principale
│   └── admin/                # Templates admin
│
├── static/                   # Fichiers statiques
│   ├── css/style.css
│   ├── js/                   # JavaScript modulaire
│   │   ├── config.js         # Constantes
│   │   ├── map.js            # Carte Leaflet
│   │   ├── pharmacy.js       # Affichage pharmacies
│   │   ├── forms.js          # Formulaires
│   │   ├── popups.js         # Fenêtres modales
│   │   ├── ads.js            # Système publicitaire
│   │   └── app.js            # Orchestrateur
│   ├── uploads/              # Fichiers uploadés
│   └── favicon.svg
│
├── utils/                    # Fonctions utilitaires
│   └── helpers.py            # Coordonnées GPS, helpers
│
└── docs/                     # Documentation
```

## Les modèles de données

### Admin

Les comptes pour accéder à l'administration.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| username | String | Nom d'utilisateur |
| password_hash | String | Mot de passe hashé |

### Pharmacy

Les pharmacies référencées sur le site.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| code | String | Code court (ex: LBV001) |
| nom | String | Nom de la pharmacie |
| ville | String | Ville |
| quartier | String | Quartier/adresse |
| telephone | String | Numéro(s) de téléphone |
| bp | String | Boîte postale |
| horaires | String | Horaires d'ouverture |
| services | String | Services proposés |
| proprietaire | String | Nom du propriétaire |
| type_etablissement | String | Type (générale, dépôt, hospitalière) |
| categorie_emplacement | String | Catégorie (centre-ville, gare, hôpital...) |
| is_garde | Boolean | En service de garde ? |
| garde_start_date | DateTime | Début de la garde |
| garde_end_date | DateTime | Fin de la garde |
| latitude | Float | Coordonnée GPS |
| longitude | Float | Coordonnée GPS |
| location_validated | Boolean | GPS vérifié par admin ? |
| is_verified | Boolean | Informations vérifiées ? |

### EmergencyContact

Les numéros d'urgence.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| ville | String | Ville (null si national) |
| service_type | String | Type (police, pompiers, hôpital...) |
| label | String | Nom affiché |
| phone_numbers | String | Numéro(s) |
| address | String | Adresse physique |
| notes | String | Informations complémentaires |
| is_national | Boolean | Service national ? |
| is_active | Boolean | Actif ? |
| ordering | Integer | Ordre d'affichage |

### Submissions

Quatre types de contributions utilisateurs :

**LocationSubmission** : Coordonnées GPS proposées
**InfoSubmission** : Correction d'information
**PharmacyProposal** : Nouvelle pharmacie suggérée
**Suggestion** : Commentaire ou idée

Toutes ont un statut (pending, approved, rejected) et des champs pour le suivi (date, admin qui a validé, etc.).

### Advertisement

Les publicités affichées aux visiteurs.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| title | String | Titre |
| description | Text | Texte descriptif |
| media_type | String | "image" ou "video" |
| image_filename | String | Nom du fichier image |
| video_url | String | URL de la vidéo |
| cta_text | String | Texte du bouton |
| cta_url | String | Lien du bouton |
| skip_delay | Integer | Délai avant "Passer" |
| is_active | Boolean | Active ? |
| priority | Integer | Priorité d'affichage |
| start_date | DateTime | Date de début |
| end_date | DateTime | Date de fin |
| view_count | Integer | Nombre de vues |
| click_count | Integer | Nombre de clics |

### AdSettings

Configuration globale des publicités (une seule ligne dans la table).

## Sécurité

**Mots de passe** : Hashés avec Werkzeug (algorithme par défaut)

**Sessions** : Gérées par Flask avec une clé secrète en variable d'environnement

**Protection CSRF** : Flask-WTF sur les formulaires

**Injections SQL** : Impossibles grâce à SQLAlchemy (requêtes préparées)

**XSS** : Fonction `escapeHtml` pour les contenus utilisateurs

**Uploads** : Extensions autorisées limitées, noms de fichiers sécurisés

**Accès admin** : Décorateur `@login_required` sur toutes les routes sensibles

## Configuration

Variables d'environnement requises :

| Variable | Description |
|----------|-------------|
| DATABASE_URL | URL de connexion PostgreSQL |
| SESSION_SECRET | Clé secrète Flask |
| ADMIN_USERNAME | Identifiant administrateur |
| ADMIN_PASSWORD | Mot de passe administrateur |

## Démarrage

**Développement :**
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

**Production :**
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

## Coordonnées GPS des villes

Les centres-villes sont prédéfinis pour le positionnement initial des nouvelles pharmacies :

| Ville | Latitude | Longitude |
|-------|----------|-----------|
| Libreville | 0.4162 | 9.4673 |
| Port-Gentil | -0.7193 | 8.7815 |
| Franceville | -1.6333 | 13.5833 |
| Oyem | 1.6167 | 11.5833 |
| Mouila | -1.8667 | 11.0500 |
| Makokou | 0.5667 | 12.8667 |
| Koulamoutou | -1.1333 | 12.4833 |
| Moanda | -1.5500 | 13.2000 |
| Ntom | 2.0000 | 11.0000 |

## Types et catégories

**Types d'établissement :**
- pharmacie_generale : Pharmacie standard
- depot_pharmaceutique : Dépôt de médicaments
- pharmacie_hospitaliere : Pharmacie d'hôpital

**Catégories d'emplacement :**
- standard, centre_ville, zone_residentielle
- gare, hopital, aeroport, centre_commercial, marche

**Types de services d'urgence :**
- police, pompiers, ambulance, hopital, clinique, sos_medecins, protection_civile, autre
