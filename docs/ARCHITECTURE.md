# UrgenceGabon.com - Technical Architecture

## Overview

UrgenceGabon.com is built on a Flask-based architecture with PostgreSQL as the data store. The application follows a modular structure with clear separation between routes, models, services, and utilities.

## System Architecture

```
+------------------------------------------------------------------+
|                         Client Layer                              |
|  +--------------+  +--------------+  +--------------------------+ |
|  |   Browser    |  |   Mobile     |  |    Admin Dashboard       | |
|  |  (Public)    |  |  (Future)    |  |    (Authenticated)       | |
|  +--------------+  +--------------+  +--------------------------+ |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                       Web Server Layer                            |
|  +--------------------------------------------------------------+ |
|  |              Gunicorn WSGI Server                             | |
|  |              (Port 5000, --reload)                            | |
|  +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                      Application Layer                            |
|  +------------------------------------------------------------+  |
|  |                    Flask Application                        |  |
|  |  +-------------+  +-------------+  +---------------------+  |  |
|  |  |   Routes    |  |  Services   |  |     Security        |  |  |
|  |  |  public.py  |  |  pharmacy   |  |   Flask-Login       |  |  |
|  |  |  admin.py   |  |  _service   |  |   auth.py           |  |  |
|  |  +-------------+  +-------------+  +---------------------+  |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                        Data Layer                                 |
|  +------------------------------------------------------------+  |
|  |                   SQLAlchemy ORM                            |  |
|  |  +-----------+ +-----------+ +-----------+ +-------------+  |  |
|  |  | Pharmacy  | |  Admin    | | Emergency | | Submissions |  |  |
|  |  |  Model    | |  Model    | | Contact   | |   Models    |  |  |
|  |  +-----------+ +-----------+ +-----------+ +-------------+  |  |
|  +------------------------------------------------------------+  |
|                              |                                    |
|                              v                                    |
|  +------------------------------------------------------------+  |
|  |                   PostgreSQL Database                       |  |
|  |            (Managed via DATABASE_URL)                       |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

## Directory Structure

```
urgence-gabon/
├── app.py                    # Flask app factory & configuration
├── main.py                   # Application entry point
├── extensions.py             # Flask extensions initialization
├── init_demo.py              # Demo data seeding script
├── init_db.py                # Database initialization
│
├── models/                   # SQLAlchemy Models
│   ├── __init__.py
│   ├── admin.py              # Admin user model
│   ├── pharmacy.py           # Pharmacy model
│   ├── emergency_contact.py  # Emergency contacts
│   ├── submission.py         # User submissions (4 types)
│   └── site_settings.py      # Site config & popups
│
├── routes/                   # Blueprint Routes
│   ├── __init__.py
│   ├── public.py             # Public API & pages
│   └── admin.py              # Admin dashboard & operations
│
├── services/                 # Business Logic
│   ├── __init__.py
│   └── pharmacy_service.py   # Pharmacy operations
│
├── security/                 # Authentication
│   ├── __init__.py
│   └── auth.py               # Flask-Login setup
│
├── templates/                # Jinja2 Templates
│   ├── index.html            # Main public page
│   └── admin/                # Admin templates
│       ├── dashboard.html
│       ├── login.html
│       ├── pharmacy_form.html
│       ├── emergency_contacts.html
│       ├── emergency_contact_form.html
│       ├── settings.html
│       ├── popups.html
│       └── popup_form.html
│
├── static/                   # Static Assets
│   ├── css/style.css
│   ├── js/app.js
│   ├── favicon.svg
│   └── uploads/              # User uploads
│       ├── settings/         # Logo, favicon, OG images
│       └── popups/           # Popup images
│
├── utils/                    # Utilities
│   ├── __init__.py
│   └── helpers.py            # Helper functions & city coords
│
└── docs/                     # Documentation
    ├── COMMERCIAL.md
    ├── API.md
    ├── ARCHITECTURE.md
    └── ADMIN_GUIDE.md
```

## Data Models

### Entity Relationship Diagram

```
+------------------+       +----------------------+
|      Admin       |       |      Pharmacy        |
+------------------+       +----------------------+
| id (PK)          |       | id (PK)              |
| username         |       | code (unique)        |
| password_hash    |<------| validated_by_admin_id|
+------------------+       | nom                  |
         |                 | ville                |
         |                 | quartier             |
         |                 | telephone            |
         |                 | bp                   |
         |                 | horaires             |
         |                 | services             |
         |                 | proprietaire         |
         |                 | type_etablissement   |
         |                 | categorie_emplacement|
         |                 | is_garde             |
         |                 | garde_start_date     |
         |                 | garde_end_date       |
         |                 | latitude             |
         |                 | longitude            |
         |                 | location_validated   |
         |                 | is_verified          |
         |                 | created_at           |
         |                 | updated_at           |
         |                 +----------------------+
         |                           |
         |                           |
         |    +----------------------+------------------------+
         |    |                      |                        |
         |    v                      v                        v
+---------------------+  +---------------------+  +---------------------+
| LocationSubmission  |  |   InfoSubmission    |  |   PharmacyView      |
+---------------------+  +---------------------+  +---------------------+
| id (PK)             |  | id (PK)             |  | id (PK)             |
| pharmacy_id (FK)    |  | pharmacy_id (FK)    |  | pharmacy_id (FK)    |
| latitude            |  | field_name          |  | viewed_at           |
| longitude           |  | current_value       |  +---------------------+
| submitted_by_name   |  | proposed_value      |
| submitted_by_phone  |  | submitted_by_name   |
| comment             |  | submitted_by_phone  |
| status              |  | comment             |
| created_at          |  | status              |
| reviewed_at         |  | created_at          |
| reviewed_by_admin_id|  | reviewed_at         |
+---------------------+  | reviewed_by_admin_id|
                         +---------------------+

+---------------------+  +---------------------+
|    Suggestion       |  |  PharmacyProposal   |
+---------------------+  +---------------------+
| id (PK)             |  | id (PK)             |
| category            |  | nom                 |
| subject             |  | ville               |
| message             |  | quartier            |
| submitted_by_name   |  | telephone           |
| submitted_by_email  |  | ... (pharmacy data) |
| submitted_by_phone  |  | submitted_by_name   |
| status              |  | submitted_by_email  |
| admin_response      |  | submitted_by_phone  |
| created_at          |  | comment             |
| reviewed_at         |  | status              |
| reviewed_by_admin_id|  | created_at          |
+---------------------+  | reviewed_at         |
                         | reviewed_by_admin_id|
                         +---------------------+

+---------------------+  +---------------------+
|  EmergencyContact   |  |    SiteSettings     |
+---------------------+  +---------------------+
| id (PK)             |  | id (PK)             |
| ville               |  | key (unique)        |
| service_type        |  | value               |
| label               |  | updated_at          |
| phone_numbers       |  +---------------------+
| address             |
| notes               |  +---------------------+
| is_national         |  |    PopupMessage     |
| is_active           |  +---------------------+
| ordering            |  | id (PK)             |
| created_at          |  | title               |
| updated_at          |  | description         |
+---------------------+  | warning_text        |
                         | image_url           |
                         | image_filename      |
                         | is_active           |
                         | show_once           |
                         | ordering            |
                         | created_at          |
                         | updated_at          |
                         +---------------------+
```

## Key Components

### 1. Application Factory (app.py)

The Flask application is configured with:
- ProxyFix middleware for reverse proxy support
- SQLAlchemy database connection
- Session management with secure secret key
- Database table creation on startup

```python
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
```

### 2. Route Blueprints

**Public Blueprint** (`routes/public.py`):
- Handles all public-facing routes
- API endpoints for pharmacy data
- Community submission endpoints

**Admin Blueprint** (`routes/admin.py`):
- Protected by `@login_required` decorator
- CRUD operations for all entities
- Dashboard with analytics
- Submission review workflow

### 3. Service Layer (services/pharmacy_service.py)

Encapsulates business logic for pharmacy operations:
- `get_all_pharmacies()` - Filtered pharmacy queries
- `get_pharmacy_by_id()` - Single pharmacy fetch
- `create_pharmacy()` - New pharmacy creation
- `update_pharmacy()` - Pharmacy updates
- `delete_pharmacy()` - Pharmacy deletion
- `toggle_garde()` - Toggle duty status
- `validate_location()` - GPS validation
- `get_stats()` - Platform statistics

### 4. Authentication (security/auth.py)

Flask-Login integration:
- User loader for Admin model
- Session-based authentication
- Password hashing with werkzeug

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SESSION_SECRET` | Flask session secret key | Yes |
| `ADMIN_USERNAME` | Initial admin username | Yes |
| `ADMIN_PASSWORD` | Initial admin password | Yes |
| `PGHOST` | Database host | Auto |
| `PGPORT` | Database port | Auto |
| `PGUSER` | Database user | Auto |
| `PGPASSWORD` | Database password | Auto |
| `PGDATABASE` | Database name | Auto |

## Data Types & Enumerations

### Establishment Types
```python
ETABLISSEMENT_TYPES = [
    ('pharmacie_generale', 'Pharmacie générale'),
    ('depot_pharmaceutique', 'Dépôt pharmaceutique'),
    ('pharmacie_hospitaliere', 'Pharmacie hospitalière'),
]
```

### Location Categories
```python
LOCATION_CATEGORIES = [
    ('standard', 'Emplacement standard'),
    ('gare', 'Proche de la gare'),
    ('hopital', 'Proche de l\'hôpital'),
    ('aeroport', 'Proche de l\'aéroport'),
    ('centre_commercial', 'Centre commercial'),
    ('marche', 'Proche du marché'),
    ('centre_ville', 'Centre-ville'),
    ('zone_residentielle', 'Zone résidentielle'),
]
```

### Emergency Service Types
```python
EMERGENCY_SERVICE_TYPES = [
    ('police', 'Police'),
    ('pompiers', 'Pompiers'),
    ('ambulance', 'Ambulance / SAMU'),
    ('hopital', 'Hôpital'),
    ('clinique', 'Clinique'),
    ('sos_medecins', 'SOS Médecins'),
    ('protection_civile', 'Protection Civile'),
    ('autre', 'Autre'),
]
```

### Submission Statuses
- `pending` - Awaiting review
- `approved` - Accepted and applied
- `rejected` - Declined
- `resolved` - Responded to (suggestions)
- `archived` - Archived (suggestions)

## City Coordinates

Pre-configured GPS coordinates for major cities:

```python
CITY_COORDINATES = {
    "Libreville": {"lat": 0.4162, "lng": 9.4673},
    "Port-Gentil": {"lat": -0.7193, "lng": 8.7815},
    "Franceville": {"lat": -1.6333, "lng": 13.5833},
    "Oyem": {"lat": 1.6167, "lng": 11.5833},
    "Mouila": {"lat": -1.8667, "lng": 11.0500},
    "Makokou": {"lat": 0.5667, "lng": 12.8667},
    "Koulamoutou": {"lat": -1.1333, "lng": 12.4833},
    "Moanda": {"lat": -1.5500, "lng": 13.2000},
    "Ntom": {"lat": 2.0000, "lng": 11.0000},
}
```

## Security Considerations

1. **Password Hashing**: werkzeug.security with default algorithm
2. **Session Management**: Secure session secret from environment
3. **CSRF Protection**: Form-based submissions with session validation
4. **SQL Injection**: SQLAlchemy ORM prevents injection
5. **File Upload Safety**: Allowed extensions whitelist, secure filenames
6. **Admin Access**: Route-level authentication with @login_required

## Deployment

### Production Configuration

```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

### Development Configuration

```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Performance Optimizations

1. **Database Connection Pooling**: SQLAlchemy engine options
2. **Query Optimization**: Indexed columns, limited result sets
3. **Static Asset Caching**: Browser caching headers
4. **Lazy Loading**: Relationships loaded on demand
