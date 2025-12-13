# Pharmacies du Gabon - Interactive Pharmacy Locator

## Overview

This is a Flask-based web application that provides an interactive map and directory of pharmacies across Gabon. The application displays 87 pharmacies and pharmaceutical depots across 9 cities, with special highlighting for 24/7 pharmacies (pharmacies de garde) and train station pharmacies. Features a modern mobile-first design with tab navigation and an admin panel for managing pharmacy data.

## User Preferences

Preferred communication style: Simple, everyday language (French).

## Recent Changes (December 2025)

### Code Quality Refactoring
- Split `static/js/app.js` (1631 lines) into 7 modular files for better maintainability
- Split `routes/admin.py` (973 lines) into 8 modular files under `routes/admin/`
- Added error handling with `.catch()` to all async fetch operations
- Replaced innerHTML with DOM creation methods where possible for XSS prevention
- Added `escapeHtml` utility function for user-generated content

### Previous Changes
- Implemented comprehensive advertising system with non-abusive display controls:
  - Advertisement model with media upload (images) or video links (YouTube/Facebook/Vimeo)
  - Multiple trigger types: time-based, page navigation, refresh count, or combined
  - Configurable skip countdown timer (default 5 seconds)
  - Session-based limits (max ads per session, cooldowns after skip/click)
  - Device targeting (mobile/desktop toggle)
  - Priority weighting for ad rotation
  - View and click tracking with statistics
  - Admin panel for managing ads and global settings
- Enhanced admin statistics dashboard with Chart.js visualizations:
  - Views over last 7 days (bar chart) and 30 days (line chart)
  - Pharmacies distribution by city (doughnut chart)
  - Views by city (pie chart)
  - Pharmacies by type (horizontal bar chart)
  - Today/week/month view counters
  - Submission tracking for locations, infos, suggestions, and proposals
- Optimized database queries using GROUP BY aggregations for performance (single queries instead of N-count loops)
- Converted all image settings to file upload only (no URLs) - logo, favicon, OpenGraph image, and popup images now use file uploads exclusively
- Added helper methods in SiteSettings for generating image URLs from uploaded filenames
- Fixed admin duplicate key error - now updates existing admin instead of creating duplicates
- Replaced "horaire" with timezone setting (fuseau horaire) using dropdown selector
- Popup images now uploaded securely with sanitized filenames (stored in static/uploads/popups/)
- Added header code block in settings for custom scripts/analytics injection
- Centered popup content for better visual display
- Added admin settings panel for site configuration (app name, logo, favicon, SEO/OpenGraph metadata, default hours)
- Implemented popup system with image upload, title, description, and warning block (red border)
- Added welcome popup with French text about platform development and user contributions
- Phone numbers made clickable with popup selector for multiple numbers (separated by / or -)
- Created comprehensive README.md with project description, features, and init_demo instructions
- Added pharmacy categorization system (gare, hopital, aeroport, marche, depot, centre_commercial, generale)
- "De garde" is now a state (checkbox) separate from category
- Added GPS coordinate capture with geolocation button and manual entry
- Added Bowl of Hygieia favicon (pharmacy symbol) across all pages
- Complete admin section redesign with modern glass-effect login, gradient sidebar, and improved forms
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
- **JavaScript**: Modular vanilla JS architecture:
  - `static/js/config.js` - Constants (city centers, colors, type definitions)
  - `static/js/map.js` - Map initialization and display functions
  - `static/js/pharmacy.js` - Pharmacy card and detail functions
  - `static/js/forms.js` - Form handling (location, info, suggestions)
  - `static/js/popups.js` - Popup system (phone, welcome, messages)
  - `static/js/ads.js` - Advertisement display system
  - `static/js/app.js` - Main orchestrator (~200 lines)
- **Design**: Mobile-first with bottom navigation bar for mobile, top tabs for desktop

### Backend Architecture
- **Framework**: Flask (Python) with Flask-Login for authentication
- **Database**: PostgreSQL with Flask-SQLAlchemy ORM
- **Authentication**: Session-based admin authentication with password hashing
- **API Pattern**: JSON endpoints for pharmacy data with filtering support
- **Routes**: Modular blueprint structure:
  - `routes/public.py` - Public-facing routes
  - `routes/admin/` - Admin routes package:
    - `__init__.py` - Blueprint and shared utilities
    - `auth.py` - Login/logout routes
    - `dashboard.py` - Admin dashboard
    - `pharmacy.py` - Pharmacy CRUD operations
    - `submissions.py` - Submission approvals
    - `emergency.py` - Emergency contacts management
    - `settings.py` - Site settings and popups
    - `ads.py` - Advertisement management

### Data Models

#### Admin
- id, username, password_hash
- Credentials configured via environment variables (ADMIN_USERNAME, ADMIN_PASSWORD)

#### Pharmacy
- id, code, nom, ville, quartier
- telephone, bp, horaires, services, proprietaire
- type_etablissement, categorie, is_garde, is_gare, is_verified
- categorie values: generale, gare, hopital, aeroport, centre_commercial, marche, depot
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

## Documentation

Full documentation is available in the `/docs` folder:
- [docs/COMMERCIAL.md](docs/COMMERCIAL.md) - Commercial overview in English
- [docs/API.md](docs/API.md) - Complete API reference
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture and data models
- [docs/ADMIN_GUIDE.md](docs/ADMIN_GUIDE.md) - Admin panel user guide

## Environment Variables

Required secrets:
- `ADMIN_USERNAME` - Admin login username
- `ADMIN_PASSWORD` - Admin login password
- `DATABASE_URL` - PostgreSQL connection string (auto-configured by Replit)
- `SESSION_SECRET` - Flask session secret key
