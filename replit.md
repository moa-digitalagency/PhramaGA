# Pharmacies Gabon - Notes techniques

Ce fichier contient les informations utiles pour travailler sur le projet.

## Description rapide

Une application web pour trouver des pharmacies au Gabon. Elle affiche 89 pharmacies réparties dans 9 villes, avec indication des pharmacies de garde (ouvertes 24h/24). Interface responsive pensée pour mobile avec onglets de navigation.

## Préférences de développement

- Communication en français, langage simple
- Code commenté quand nécessaire
- Tests manuels avant de valider

## Historique des modifications

**Décembre 2025**

Refactoring du code pour une meilleure maintenabilité :
- Le fichier JS principal (1600+ lignes) a été découpé en 7 modules
- Les routes admin (970+ lignes) sont maintenant dans 8 fichiers séparés
- Ajout de gestion d'erreurs sur tous les appels asynchrones
- Protection XSS avec fonction `escapeHtml`

Fonctionnalités précédentes :
- Système publicitaire configurable (images ou vidéos, plusieurs déclencheurs, limites par session)
- Statistiques avec graphiques Chart.js (vues, répartition par ville et type)
- Upload de fichiers pour logo, favicon et images (plus d'URLs externes)
- Correction du bug de duplication admin
- Fuseau horaire configurable
- Popups personnalisables avec images
- Numéros de téléphone cliquables
- Catégorisation des pharmacies (gare, hôpital, aéroport, etc.)
- Système de vérification GPS
- Design mobile-first

## Architecture

**Frontend :**
- Templates Jinja2
- Tailwind CSS (CDN)
- Leaflet.js pour les cartes
- JavaScript modulaire :
  - `config.js` : constantes et configuration
  - `map.js` : gestion de la carte
  - `pharmacy.js` : affichage des pharmacies
  - `forms.js` : formulaires de soumission
  - `popups.js` : fenêtres modales
  - `ads.js` : système publicitaire
  - `app.js` : orchestrateur principal

**Backend :**
- Flask avec Flask-Login
- PostgreSQL via SQLAlchemy
- Authentification par session
- Routes en blueprints :
  - `routes/public.py` : accès public
  - `routes/admin/` : administration (auth, dashboard, pharmacy, submissions, emergency, settings, ads)

## Modèles de données

**Admin** : id, username, password_hash

**Pharmacy** : id, code, nom, ville, quartier, telephone, bp, horaires, services, proprietaire, type_etablissement, categorie_emplacement, is_garde, is_verified, latitude, longitude, location_validated

**EmergencyContact** : ville, service_type, label, phone_numbers, address, notes, is_national, ordering

**Submission types** : LocationSubmission, InfoSubmission, PharmacyProposal, Suggestion

**Advertisement** : title, description, media_type, image/video, cta_text, cta_url, skip_delay, priority, dates, view/click counts

## Dépendances externes

CDN :
- Tailwind CSS
- Leaflet.js 1.9.4
- Google Fonts (Inter)
- Chart.js

Python :
- Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- psycopg2-binary
- gunicorn
- werkzeug

## Points d'accès API

**Public :**
- `GET /` : page principale
- `GET /api/pharmacies` : liste (filtres: search, ville, garde)
- `GET /api/stats` : statistiques
- `GET /api/popups` : popups actifs
- `GET /api/emergency-contacts` : contacts d'urgence
- `POST /api/pharmacy/<id>/view` : enregistrer une vue
- `POST /api/pharmacy/<id>/submit-location` : soumettre GPS
- `POST /api/pharmacy/<id>/submit-info` : soumettre correction
- `POST /api/suggestions` : envoyer suggestion
- `POST /api/pharmacy-proposal` : proposer pharmacie

**Admin (authentification requise) :**
- `/admin/login`, `/admin/logout`
- `/admin` : tableau de bord
- `/admin/pharmacy/add`, `/admin/pharmacy/<id>/edit`, `/admin/pharmacy/<id>/delete`
- `/admin/pharmacy/<id>/toggle-garde`
- Gestion des soumissions, contacts d'urgence, paramètres, publicités

## Scripts d'initialisation

`init_db.py` : crée les tables de la base

`init_demo.py` : charge les données de démonstration (pharmacies, contacts, popup)

```bash
python init_demo.py        # charge les données
python init_demo.py --force  # efface et recharge
```

## Variables d'environnement

Obligatoires :
- `DATABASE_URL` : connexion PostgreSQL
- `SESSION_SECRET` : clé de session Flask
- `ADMIN_USERNAME` : identifiant admin
- `ADMIN_PASSWORD` : mot de passe admin

Automatiques (Replit) :
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
