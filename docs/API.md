# UrgenceGabon.com - API Documentation

## Overview

The UrgenceGabon.com API provides programmatic access to pharmacy data, statistics, advertisements, and submission endpoints. All public endpoints return JSON responses.

**Base URL**: `https://your-domain.com`

## Authentication

Public API endpoints do not require authentication. Admin endpoints require session-based authentication through the `/admin/login` route.

## Public API Endpoints

### 1. Get Pharmacies

Retrieve a list of pharmacies with optional filtering.

**Endpoint**: `GET /api/pharmacies`

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | No | Search term for name, neighborhood, or services |
| `ville` | string | No | Filter by city name |
| `garde` | string | No | Set to `true` to show only on-duty pharmacies |
| `gare` | string | No | Set to `true` to show only pharmacies near train station |

**Example Request**:
```http
GET /api/pharmacies?ville=Libreville&garde=true
```

**Response**:
```json
[
  {
    "id": 1,
    "code": "LBV001",
    "nom": "Grande Pharmacie des Forestiers",
    "ville": "Libreville",
    "quartier": "Galerie de Mbolo",
    "telephone": "011 72 23 52",
    "bp": "2",
    "horaires": "Lun-Sam: 8h-19h30, Dim: 8h-18h",
    "services": "Parapharmacie, Conseil pharmaceutique",
    "proprietaire": "",
    "type_etablissement": "pharmacie_generale",
    "categorie_emplacement": "centre_commercial",
    "is_garde": false,
    "lat": 0.4162,
    "lng": 9.4673,
    "location_validated": false,
    "is_verified": false,
    "garde_end_date": null
  }
]
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique pharmacy identifier |
| `code` | string | Pharmacy code |
| `nom` | string | Pharmacy name |
| `ville` | string | City |
| `quartier` | string | Neighborhood/district |
| `telephone` | string | Phone number(s) |
| `bp` | string | Postal box number |
| `horaires` | string | Operating hours |
| `services` | string | Services offered |
| `proprietaire` | string | Owner name |
| `type_etablissement` | string | Establishment type |
| `categorie_emplacement` | string | Location category |
| `is_garde` | boolean | Currently on emergency duty |
| `lat` | float | Latitude coordinate |
| `lng` | float | Longitude coordinate |
| `location_validated` | boolean | Location verified by admin |
| `is_verified` | boolean | Information verified |
| `garde_end_date` | string/null | End date of duty period (ISO format) |

---

### 2. Get Statistics

Retrieve platform statistics.

**Endpoint**: `GET /api/stats`

**Response**:
```json
{
  "total": 87,
  "pharmacies_garde": 15,
  "pharmacies_gare": 1,
  "locations_validated": 10,
  "par_ville": {
    "Libreville": 70,
    "Port-Gentil": 8,
    "Franceville": 2,
    "Oyem": 1
  }
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total number of pharmacies |
| `pharmacies_garde` | integer | Pharmacies currently on duty |
| `pharmacies_gare` | integer | Pharmacies near train station |
| `locations_validated` | integer | Verified GPS locations |
| `par_ville` | object | Pharmacy count by city |

---

### 3. Get Active Popups

Retrieve currently active popup messages.

**Endpoint**: `GET /api/popups`

**Response**:
```json
[
  {
    "id": 1,
    "title": "Bienvenue sur UrgenceGabon.com",
    "description": "Decouvrez la premiere plateforme...",
    "warning_text": "Le projet est encore en construction...",
    "image_url": "",
    "is_active": true,
    "show_once": true,
    "ordering": 0
  }
]
```

---

### 4. Record Pharmacy View

Record a view/click on a pharmacy (for analytics).

**Endpoint**: `POST /api/pharmacy/<id>/view`

**URL Parameters**:
- `id` (integer): Pharmacy ID

**Response**:
```json
{
  "success": true
}
```

---

### 5. Submit Location Correction

Submit GPS coordinates for a pharmacy location.

**Endpoint**: `POST /api/pharmacy/<id>/submit-location`

**URL Parameters**:
- `id` (integer): Pharmacy ID

**Request Body**:
```json
{
  "latitude": 0.4162,
  "longitude": 9.4673,
  "name": "Jean Dupont",
  "phone": "+241 06 00 00 00",
  "comment": "Coordonnees precises du batiment"
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `latitude` | float | Yes | GPS latitude |
| `longitude` | float | Yes | GPS longitude |
| `name` | string | No | Submitter's name |
| `phone` | string | No | Submitter's phone |
| `comment` | string | No | Additional comments |

**Response**:
```json
{
  "success": true,
  "message": "Localisation soumise avec succes"
}
```

**Error Response** (400):
```json
{
  "success": false,
  "error": "Coordonnees manquantes"
}
```

---

### 6. Submit Information Correction

Submit a correction for pharmacy information.

**Endpoint**: `POST /api/pharmacy/<id>/submit-info`

**URL Parameters**:
- `id` (integer): Pharmacy ID

**Request Body**:
```json
{
  "field_name": "telephone",
  "proposed_value": "011 72 00 00",
  "name": "Marie Martin",
  "phone": "+241 06 00 00 00",
  "comment": "Nouveau numero depuis janvier 2024"
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `field_name` | string | Yes | Field to update (telephone, horaires, etc.) |
| `proposed_value` | string | Yes | New proposed value |
| `name` | string | No | Submitter's name |
| `phone` | string | No | Submitter's phone |
| `comment` | string | No | Additional comments |

**Valid Field Names**:
- `telephone`
- `horaires`
- `services`
- `quartier`
- `bp`
- `proprietaire`

**Response**:
```json
{
  "success": true,
  "message": "Information soumise avec succes"
}
```

---

### 7. Submit Suggestion

Submit a general suggestion or feedback.

**Endpoint**: `POST /api/suggestions`

**Request Body**:
```json
{
  "category": "amelioration",
  "subject": "Ajout de fonctionnalite",
  "message": "Il serait utile d'avoir une fonction de recherche par medicament...",
  "name": "Pierre Obame",
  "email": "pierre@example.com",
  "phone": "+241 06 00 00 00"
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | string | Yes | Suggestion category |
| `subject` | string | Yes | Subject line |
| `message` | string | Yes | Detailed message |
| `name` | string | No | Submitter's name |
| `email` | string | No | Submitter's email |
| `phone` | string | No | Submitter's phone |

**Response**:
```json
{
  "success": true,
  "message": "Suggestion envoyee avec succes"
}
```

---

### 8. Submit New Pharmacy Proposal

Propose a new pharmacy to be added to the database.

**Endpoint**: `POST /api/pharmacy-proposal`

**Request Body**:
```json
{
  "nom": "Pharmacie du Soleil",
  "ville": "Libreville",
  "quartier": "Akebe",
  "telephone": "011 72 00 00",
  "bp": "1234",
  "horaires": "8h-20h",
  "services": "Service courant",
  "proprietaire": "Dr. Nzamba",
  "type_etablissement": "pharmacie_generale",
  "categorie_emplacement": "zone_residentielle",
  "is_garde": false,
  "latitude": 0.4200,
  "longitude": 9.4700,
  "name": "Jean Obiang",
  "email": "jean@example.com",
  "phone": "+241 06 00 00 00",
  "comment": "Pharmacie ouverte recemment"
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `nom` | string | Yes | Pharmacy name |
| `ville` | string | Yes | City |
| `quartier` | string | No | Neighborhood |
| `telephone` | string | No | Phone number |
| `bp` | string | No | Postal box |
| `horaires` | string | No | Operating hours |
| `services` | string | No | Services offered |
| `proprietaire` | string | No | Owner name |
| `type_etablissement` | string | No | Establishment type |
| `categorie_emplacement` | string | No | Location category |
| `is_garde` | boolean | No | On-duty status |
| `latitude` | float | No | GPS latitude |
| `longitude` | float | No | GPS longitude |
| `name` | string | No | Submitter's name |
| `email` | string | No | Submitter's email |
| `phone` | string | No | Submitter's phone |
| `comment` | string | No | Additional comments |

**Establishment Types**:
- `pharmacie_generale` - General Pharmacy
- `depot_pharmaceutique` - Pharmaceutical Depot
- `pharmacie_hospitaliere` - Hospital Pharmacy

**Location Categories**:
- `standard` - Standard location
- `gare` - Near train station
- `hopital` - Near hospital
- `aeroport` - Near airport
- `centre_commercial` - Shopping center
- `marche` - Near market
- `centre_ville` - City center
- `zone_residentielle` - Residential area

**Response**:
```json
{
  "success": true,
  "message": "Proposition de pharmacie envoyee avec succes"
}
```

---

## Advertisement API Endpoints

### 9. Get Ad Settings

Retrieve global advertisement settings.

**Endpoint**: `GET /api/ads/settings`

**Response**:
```json
{
  "ads_enabled": true,
  "trigger_type": "time",
  "time_delay": 60,
  "time_repeat": true,
  "time_interval": 300,
  "page_count": 3,
  "refresh_show": false,
  "refresh_count": 1,
  "default_skip_delay": 5,
  "max_ads_per_session": 10,
  "cooldown_after_skip": 60,
  "cooldown_after_click": 300,
  "show_on_mobile": true,
  "show_on_desktop": true
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `ads_enabled` | boolean | Whether ads are globally enabled |
| `trigger_type` | string | Trigger type: "time", "page_count", or "refresh" |
| `time_delay` | integer | Seconds before first ad (time trigger) |
| `time_repeat` | boolean | Whether to show repeated ads |
| `time_interval` | integer | Seconds between repeated ads |
| `page_count` | integer | Pages before ad shows (page_count trigger) |
| `refresh_show` | boolean | Show ad on page refresh |
| `refresh_count` | integer | Refreshes before ad shows |
| `default_skip_delay` | integer | Default skip button delay (seconds) |
| `max_ads_per_session` | integer | Maximum ads per user session |
| `cooldown_after_skip` | integer | Pause after user skips (seconds) |
| `cooldown_after_click` | integer | Pause after user clicks CTA (seconds) |
| `show_on_mobile` | boolean | Display ads on mobile devices |
| `show_on_desktop` | boolean | Display ads on desktop |

---

### 10. Get Random Ad

Retrieve a random active advertisement based on priority weighting.

**Endpoint**: `GET /api/ads/random`

**Response** (when ads available):
```json
{
  "id": 1,
  "title": "Special Offer",
  "description": "Visit our partner pharmacy for 20% discount",
  "media_type": "image",
  "image_url": "/static/uploads/ads/abc123.jpg",
  "video_url": "",
  "cta_text": "En savoir plus",
  "cta_url": "https://example.com/offer",
  "skip_delay": 5,
  "is_active": true,
  "priority": 10
}
```

**Response** (when no ads available):
```json
null
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Advertisement ID |
| `title` | string | Ad headline |
| `description` | string | Ad body text |
| `media_type` | string | "image" or "video" |
| `image_url` | string/null | URL to ad image |
| `video_url` | string | Video embed URL (YouTube, etc.) |
| `cta_text` | string | Call-to-action button text |
| `cta_url` | string | CTA destination URL |
| `skip_delay` | integer | Seconds before skip button activates |
| `is_active` | boolean | Ad active status |
| `priority` | integer | Display priority weight |

---

### 11. Record Ad View

Record when an advertisement is displayed to a user.

**Endpoint**: `POST /api/ads/<id>/view`

**URL Parameters**:
- `id` (integer): Advertisement ID

**Response**:
```json
{
  "success": true
}
```

---

### 12. Record Ad Click

Record when a user clicks an advertisement's CTA button.

**Endpoint**: `POST /api/ads/<id>/click`

**URL Parameters**:
- `id` (integer): Advertisement ID

**Response**:
```json
{
  "success": true
}
```

---

## Admin API Endpoints

All admin endpoints require authentication. Access is session-based after logging in at `/admin/login`.

### Authentication

**Login**: `POST /admin/login`

Form data:
- `username`: Admin username
- `password`: Admin password

**Logout**: `GET /admin/logout`

### Pharmacy Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/` | Admin dashboard |
| GET/POST | `/admin/pharmacy/add` | Add new pharmacy |
| GET/POST | `/admin/pharmacy/<id>/edit` | Edit pharmacy |
| POST | `/admin/pharmacy/<id>/delete` | Delete pharmacy |
| POST | `/admin/pharmacy/<id>/toggle-garde` | Toggle duty status |
| POST | `/admin/pharmacy/<id>/validate-location` | Validate GPS location |
| POST | `/admin/pharmacy/<id>/invalidate-location` | Invalidate GPS location |
| POST | `/admin/pharmacy/<id>/update-coordinates` | Update GPS coordinates |
| POST | `/admin/pharmacy/<id>/set-garde` | Set duty period with dates |

### Submission Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/location-submission/<id>/approve` | Approve location submission |
| POST | `/admin/location-submission/<id>/reject` | Reject location submission |
| POST | `/admin/info-submission/<id>/approve` | Approve info submission |
| POST | `/admin/info-submission/<id>/reject` | Reject info submission |
| POST | `/admin/suggestion/<id>/respond` | Respond to suggestion |
| POST | `/admin/suggestion/<id>/archive` | Archive suggestion |
| POST | `/admin/pharmacy-proposal/<id>/approve` | Approve pharmacy proposal |
| POST | `/admin/pharmacy-proposal/<id>/reject` | Reject pharmacy proposal |

### Emergency Contacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/emergency-contacts` | List all contacts |
| GET/POST | `/admin/emergency-contact/add` | Add new contact |
| GET/POST | `/admin/emergency-contact/<id>/edit` | Edit contact |
| POST | `/admin/emergency-contact/<id>/delete` | Delete contact |

### Site Settings & Popups

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/admin/settings` | Site settings |
| GET | `/admin/popups` | List popups |
| GET/POST | `/admin/popup/add` | Add popup |
| GET/POST | `/admin/popup/<id>/edit` | Edit popup |
| POST | `/admin/popup/<id>/toggle` | Toggle popup active status |
| POST | `/admin/popup/<id>/delete` | Delete popup |

### Advertisement Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/ads` | List all advertisements |
| GET/POST | `/admin/ad/add` | Add new advertisement |
| GET/POST | `/admin/ad/<id>/edit` | Edit advertisement |
| POST | `/admin/ad/<id>/delete` | Delete advertisement |
| GET/POST | `/admin/ads/settings` | Global ad settings |

---

## Error Handling

All API endpoints return standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Missing or invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 401 | Unauthorized - Authentication required |
| 500 | Internal Server Error |

Error responses follow this format:
```json
{
  "success": false,
  "error": "Error message description"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. Please use the API responsibly.

---

## CORS

The API does not currently enable CORS for external domains. All requests should originate from the same domain.
