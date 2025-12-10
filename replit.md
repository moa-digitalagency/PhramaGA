# Pharmacies du Gabon - Interactive Pharmacy Locator

## Overview

This is a Flask-based web application that provides an interactive map and directory of pharmacies across Gabon. The application displays 87 pharmacies and pharmaceutical depots across 9 cities, with special highlighting for 24/7 pharmacies (pharmacies de garde) and train station pharmacies. Features a modern mobile-first design with tab navigation and an admin panel for managing pharmacy data.

## User Preferences

Preferred communication style: Simple, everyday language (French).

## Recent Changes (December 2025)

- Added pharmacy verification system with is_verified field and visual badges
- Changed pharmacy icon to proper pharmacy cross symbol (circle with cross inside)
- Added verified pharmacies count in admin dashboard stats
- Added verification column in admin pharmacy table
- Added verification checkbox in pharmacy add/edit form
- Redesigned UI with mobile-first responsive design
- Added tab-based navigation (Pharmacies, Pharmacies de garde, Carte)
- Implemented admin authentication and dashboard
- Added CRUD operations for pharmacies with GPS coordinate editing
- Migrated from CSV to PostgreSQL database
- Added city filter pills in header
- Improved pharmacy cards with click-to-call functionality

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates served by Flask
- **CSS Framework**: Tailwind CSS via CDN for responsive styling
- **Mapping Library**: Leaflet.js with OpenStreetMap tiles for interactive pharmacy locations
- **JavaScript**: Vanilla JS (`static/js/app.js`) handles map, filtering, tabs, and modals
- **Design**: Mobile-first with bottom navigation bar for mobile, top tabs for desktop

### Backend Architecture
- **Framework**: Flask (Python) with Flask-Login for authentication
- **Database**: PostgreSQL with Flask-SQLAlchemy ORM
- **Authentication**: Session-based admin authentication with password hashing
- **API Pattern**: JSON endpoints for pharmacy data with filtering support

### Data Models

#### Admin
- id, username, password_hash
- Credentials configured via environment variables (ADMIN_USERNAME, ADMIN_PASSWORD)

#### Pharmacy
- id, code, nom, ville, quartier
- telephone, bp, horaires, services, proprietaire
- type_etablissement, is_garde, is_gare, is_verified
- latitude, longitude (GPS coordinates)
- location_validated, validated_at, validated_by_admin_id

## External Dependencies

### Frontend CDN Resources
- **Tailwind CSS**: `https://cdn.tailwindcss.com`
- **Leaflet CSS/JS**: `https://unpkg.com/leaflet@1.9.4`
- **Inter Font**: Google Fonts

### Python Dependencies
- Flask, Flask-SQLAlchemy, Flask-Login
- psycopg2-binary (PostgreSQL driver)
- Werkzeug (password hashing)

## API Endpoints

### Public
- `GET /` - Main page with pharmacy list and map
- `GET /api/pharmacies` - Returns pharmacy data (params: search, ville, garde, gare)
- `GET /api/stats` - Returns statistics

### Admin (requires authentication)
- `GET/POST /admin/login` - Admin login
- `GET /admin/logout` - Logout
- `GET /admin` - Dashboard with pharmacy list
- `GET/POST /admin/pharmacy/add` - Add new pharmacy
- `GET/POST /admin/pharmacy/<id>/edit` - Edit pharmacy
- `POST /admin/pharmacy/<id>/delete` - Delete pharmacy
- `POST /admin/pharmacy/<id>/toggle-garde` - Toggle garde status

## Features

### Public Interface
- Interactive map showing all pharmacies across Gabon
- Tab navigation: All pharmacies, Garde pharmacies (24h), Map view
- City filter pills for quick filtering
- Search by name, neighborhood, or services
- Color-coded markers: green (general), red (24h/24), blue (station), orange (depot)
- Click-to-call phone numbers
- Pharmacy detail modal with full information

### Admin Panel
- Secure login with password authentication
- Dashboard with statistics (total, garde, gare, with GPS)
- Add/edit/delete pharmacies
- Toggle garde status with one click
- Interactive map for setting GPS coordinates
- Search and filter in table view

## Initialization Scripts

### init_db.py
Creates all database tables (pharmacy, admin, location_submission, info_submission, pharmacy_view, suggestion).

```bash
python init_db.py
```

### init_demo.py
Loads pharmacy demo data from CSV file. Does NOT create admin user (admin is created from environment variables on app startup).

```bash
python init_demo.py
```

## Environment Variables

Required secrets:
- `ADMIN_USERNAME` - Admin login username
- `ADMIN_PASSWORD` - Admin login password
- `DATABASE_URL` - PostgreSQL connection string (auto-configured by Replit)
- `SESSION_SECRET` - Flask session secret key
