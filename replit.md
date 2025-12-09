# Pharmacies du Gabon - Interactive Pharmacy Locator

## Overview

This is a Flask-based web application that provides an interactive map and directory of pharmacies across Gabon. The application displays 87 pharmacies and pharmaceutical depots across 9 cities, with special highlighting for 24/7 pharmacies and emergency (garde) services. Users can search, filter by city, and view pharmacy details including contact information, hours, and services offered.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates served by Flask
- **CSS Framework**: Tailwind CSS via CDN for responsive styling
- **Mapping Library**: Leaflet.js with OpenStreetMap tiles for interactive pharmacy locations
- **JavaScript**: Vanilla JS (`static/js/app.js`) handles map initialization, marker management, filtering, and search functionality

### Backend Architecture
- **Framework**: Flask (Python) serving as a lightweight web server
- **Data Source**: CSV file (`attached_assets/pharmacies_gabon_exhaustive_1765303770607.csv`) containing pharmacy records
- **Coordinate System**: City-based coordinates with calculated offsets for individual pharmacies within neighborhoods (quartiers)
- **API Pattern**: JSON endpoints for pharmacy data retrieval with filtering support

### Data Model
Each pharmacy record includes:
- Identification (id, name)
- Location (city/ville, neighborhood/quartier, coordinates)
- Contact (phone, postal box)
- Services (type, hours, owner)
- Status flags (is_garde for 24/7, is_gare for station-adjacent)

### Coordinate Generation Strategy
Since exact GPS coordinates aren't available for all pharmacies, the system:
1. Uses predefined city center coordinates
2. Generates unique offsets based on neighborhood and pharmacy index
3. Distributes markers to avoid overlap while maintaining city grouping

## External Dependencies

### Frontend CDN Resources
- **Tailwind CSS**: `https://cdn.tailwindcss.com` - Utility-first CSS framework
- **Leaflet CSS/JS**: `https://unpkg.com/leaflet@1.9.4` - Interactive mapping library

### Map Tile Provider
- **OpenStreetMap**: Tile layer for map visualization (free, no API key required)

### Data Storage
- **CSV File**: Local file-based storage for pharmacy data (no database currently configured)
- The application reads from `attached_assets/pharmacies_gabon_exhaustive_1765303770607.csv` at runtime

### Python Dependencies
- **Flask**: Web framework for routing and template rendering
- Standard library modules: `csv`, `os` for file operations

## API Endpoints

- `GET /` - Main page with map and pharmacy list
- `GET /api/pharmacies` - Returns pharmacy data (supports query params: search, ville, type, garde, gare)
- `GET /api/stats` - Returns statistics about pharmacies

## Features

- Interactive map showing all 87 pharmacies across Gabon
- Search by name, neighborhood, or services
- Filter by city and establishment type
- Quick filters for 24/7 pharmacies (garde) and train station pharmacies
- Color-coded markers: green (general), red (24h/24), blue (station), orange (depot)
- Click-to-focus list items that center the map on the selected pharmacy
- Statistics panel showing totals and filtered results
