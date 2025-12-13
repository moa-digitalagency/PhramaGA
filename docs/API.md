# Documentation de l'API

Cette API permet d'accéder aux données des pharmacies et des services d'urgence au Gabon. Toutes les réponses sont au format JSON.

## Accès

**URL de base :** `https://votre-domaine.com`

Les endpoints publics sont accessibles sans authentification. Les endpoints admin nécessitent une connexion préalable via `/admin/login`.

---

## Endpoints publics

### Liste des pharmacies

Récupère la liste des pharmacies avec possibilité de filtrer.

**Requête :** `GET /api/pharmacies`

**Paramètres (optionnels) :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| search | string | Recherche dans le nom, quartier ou services |
| ville | string | Filtrer par ville |
| garde | string | "true" pour les pharmacies de garde uniquement |

**Exemple :**
```
GET /api/pharmacies?ville=Libreville&garde=true
```

**Réponse :**
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

---

### Statistiques

Récupère les statistiques générales de la plateforme.

**Requête :** `GET /api/stats`

**Réponse :**
```json
{
  "total": 89,
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

---

### Contacts d'urgence

Récupère la liste des numéros d'urgence.

**Requête :** `GET /api/emergency-contacts`

**Paramètres (optionnels) :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| ville | string | Filtrer par ville |

**Réponse :**
```json
[
  {
    "id": 1,
    "ville": null,
    "service_type": "police",
    "label": "Police Secours (National)",
    "phone_numbers": "1730 / 177",
    "address": "",
    "notes": "Numéro national d'urgence police",
    "is_national": true
  }
]
```

---

### Popups actifs

Récupère les messages popup à afficher.

**Requête :** `GET /api/popups`

**Réponse :**
```json
[
  {
    "id": 1,
    "title": "Bienvenue sur UrgenceGabon.com",
    "description": "Découvrez la première plateforme...",
    "warning_text": "Le projet est encore en construction...",
    "image_url": "",
    "is_active": true,
    "show_once": true,
    "ordering": 0
  }
]
```

---

### Enregistrer une consultation

Comptabilise une vue sur une pharmacie (pour les statistiques).

**Requête :** `POST /api/pharmacy/<id>/view`

**Réponse :**
```json
{
  "success": true
}
```

---

### Soumettre une localisation GPS

Propose des coordonnées pour une pharmacie.

**Requête :** `POST /api/pharmacy/<id>/submit-location`

**Corps de la requête :**
```json
{
  "latitude": 0.4162,
  "longitude": 9.4673,
  "name": "Jean Dupont",
  "phone": "+241 06 00 00 00",
  "comment": "Coordonnées exactes du bâtiment"
}
```

**Champs :**

| Champ | Obligatoire | Description |
|-------|-------------|-------------|
| latitude | oui | Latitude GPS |
| longitude | oui | Longitude GPS |
| name | non | Nom du contributeur |
| phone | non | Téléphone du contributeur |
| comment | non | Commentaire |

**Réponse :**
```json
{
  "success": true,
  "message": "Localisation soumise avec succès"
}
```

---

### Soumettre une correction

Propose une modification d'information.

**Requête :** `POST /api/pharmacy/<id>/submit-info`

**Corps de la requête :**
```json
{
  "field_name": "telephone",
  "proposed_value": "011 72 00 00",
  "name": "Marie Martin",
  "phone": "+241 06 00 00 00",
  "comment": "Nouveau numéro depuis janvier 2024"
}
```

**Champs modifiables :** telephone, horaires, services, quartier, bp, proprietaire

**Réponse :**
```json
{
  "success": true,
  "message": "Information soumise avec succès"
}
```

---

### Envoyer une suggestion

Envoie un commentaire ou une idée.

**Requête :** `POST /api/suggestions`

**Corps de la requête :**
```json
{
  "category": "amelioration",
  "subject": "Ajout de fonctionnalité",
  "message": "Il serait utile d'avoir une fonction de recherche par médicament...",
  "name": "Pierre Obame",
  "email": "pierre@exemple.com",
  "phone": "+241 06 00 00 00"
}
```

**Réponse :**
```json
{
  "success": true,
  "message": "Suggestion envoyée avec succès"
}
```

---

### Proposer une pharmacie

Suggère l'ajout d'une nouvelle pharmacie.

**Requête :** `POST /api/pharmacy-proposal`

**Corps de la requête :**
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
  "email": "jean@exemple.com",
  "phone": "+241 06 00 00 00",
  "comment": "Pharmacie ouverte récemment"
}
```

**Réponse :**
```json
{
  "success": true,
  "message": "Proposition de pharmacie envoyée avec succès"
}
```

---

## Endpoints publicitaires

### Configuration des publicités

Récupère les paramètres globaux des pubs.

**Requête :** `GET /api/ads/settings`

**Réponse :**
```json
{
  "ads_enabled": true,
  "trigger_type": "time",
  "time_delay": 60,
  "time_repeat": true,
  "time_interval": 300,
  "default_skip_delay": 5,
  "max_ads_per_session": 10,
  "show_on_mobile": true,
  "show_on_desktop": true
}
```

---

### Obtenir une publicité

Récupère une publicité aléatoire (pondérée par priorité).

**Requête :** `GET /api/ads/random`

**Réponse (si disponible) :**
```json
{
  "id": 1,
  "title": "Offre spéciale",
  "description": "Visitez notre partenaire...",
  "media_type": "image",
  "image_url": "/static/uploads/ads/abc123.jpg",
  "video_url": "",
  "cta_text": "En savoir plus",
  "cta_url": "https://exemple.com/offre",
  "skip_delay": 5,
  "is_active": true,
  "priority": 10
}
```

**Réponse (si aucune pub disponible) :**
```json
null
```

---

### Enregistrer une vue de pub

**Requête :** `POST /api/ads/<id>/view`

### Enregistrer un clic de pub

**Requête :** `POST /api/ads/<id>/click`

---

## Endpoints admin

Tous ces endpoints nécessitent une authentification préalable.

### Authentification

**Connexion :** `POST /admin/login` (formulaire avec username et password)

**Déconnexion :** `GET /admin/logout`

### Pharmacies

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | /admin/ | Tableau de bord |
| GET/POST | /admin/pharmacy/add | Ajouter |
| GET/POST | /admin/pharmacy/<id>/edit | Modifier |
| POST | /admin/pharmacy/<id>/delete | Supprimer |
| POST | /admin/pharmacy/<id>/toggle-garde | Activer/désactiver garde |

### Soumissions

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | /admin/location-submission/<id>/approve | Approuver localisation |
| POST | /admin/location-submission/<id>/reject | Refuser localisation |
| POST | /admin/info-submission/<id>/approve | Approuver correction |
| POST | /admin/info-submission/<id>/reject | Refuser correction |
| POST | /admin/suggestion/<id>/respond | Répondre à suggestion |
| POST | /admin/pharmacy-proposal/<id>/approve | Approuver proposition |
| POST | /admin/pharmacy-proposal/<id>/reject | Refuser proposition |

### Contacts d'urgence

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | /admin/emergency-contacts | Liste |
| GET/POST | /admin/emergency-contact/add | Ajouter |
| GET/POST | /admin/emergency-contact/<id>/edit | Modifier |
| POST | /admin/emergency-contact/<id>/delete | Supprimer |

### Paramètres et popups

| Méthode | URL | Description |
|---------|-----|-------------|
| GET/POST | /admin/settings | Paramètres du site |
| GET | /admin/popups | Liste des popups |
| GET/POST | /admin/popup/add | Ajouter popup |
| GET/POST | /admin/popup/<id>/edit | Modifier popup |
| POST | /admin/popup/<id>/delete | Supprimer popup |

### Publicités

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | /admin/ads | Liste des pubs |
| GET/POST | /admin/ad/add | Ajouter pub |
| GET/POST | /admin/ad/<id>/edit | Modifier pub |
| POST | /admin/ad/<id>/delete | Supprimer pub |
| GET/POST | /admin/ads/settings | Configuration globale |

---

## Gestion des erreurs

Toutes les erreurs suivent ce format :

```json
{
  "success": false,
  "error": "Description de l'erreur"
}
```

Codes HTTP utilisés :
- 200 : Succès
- 400 : Paramètres manquants ou invalides
- 401 : Authentification requise
- 404 : Ressource introuvable
- 500 : Erreur serveur
