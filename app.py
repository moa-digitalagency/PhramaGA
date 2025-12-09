from flask import Flask, render_template, jsonify, request
import csv
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

CITY_COORDINATES = {
    "Libreville": {"lat": 0.4162, "lng": 9.4673},
    "Port-Gentil": {"lat": -0.7193, "lng": 8.7815},
    "Franceville": {"lat": -1.6333, "lng": 13.5833},
    "Moanda": {"lat": -1.5333, "lng": 13.2000},
    "Makokou": {"lat": 0.5667, "lng": 12.8500},
    "Oyem": {"lat": 1.6000, "lng": 11.5833},
    "Mouila": {"lat": -1.8667, "lng": 11.0500},
    "Koulamoutou": {"lat": -1.1333, "lng": 12.4667},
    "Ntom": {"lat": 0.3667, "lng": 9.7667}
}

QUARTIER_OFFSETS = {}

def load_pharmacies():
    pharmacies = []
    csv_path = os.path.join('attached_assets', 'pharmacies_gabon_exhaustive_1765303770607.csv')
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if not row['id']:
                continue
            
            ville = row['ville']
            quartier = row['quartier']
            
            base_coords = CITY_COORDINATES.get(ville, {"lat": 0.4162, "lng": 9.4673})
            
            offset_key = f"{ville}_{quartier}"
            if offset_key not in QUARTIER_OFFSETS:
                QUARTIER_OFFSETS[offset_key] = len(QUARTIER_OFFSETS)
            
            offset_idx = QUARTIER_OFFSETS[offset_key] + idx
            lat_offset = (offset_idx % 50) * 0.002 - 0.05
            lng_offset = (offset_idx // 50 % 50) * 0.002 - 0.05
            
            is_garde = 'garde' in row['type_etablissement'].lower() or '24h' in row['horaires']
            is_gare = 'gare' in row['quartier'].lower() or 'gare' in row['nom'].lower()
            
            pharmacy = {
                'id': row['id'],
                'nom': row['nom'],
                'ville': ville,
                'quartier': quartier,
                'telephone': row['telephone'],
                'bp': row['bp'],
                'horaires': row['horaires'],
                'services': row['services'],
                'proprietaire': row['proprietaire'],
                'type_etablissement': row['type_etablissement'],
                'lat': base_coords['lat'] + lat_offset,
                'lng': base_coords['lng'] + lng_offset,
                'is_garde': is_garde,
                'is_gare': is_gare
            }
            pharmacies.append(pharmacy)
    
    return pharmacies

PHARMACIES = load_pharmacies()

@app.route('/')
def index():
    villes = sorted(list(set(p['ville'] for p in PHARMACIES)))
    types = sorted(list(set(p['type_etablissement'] for p in PHARMACIES if p['type_etablissement'])))
    return render_template('index.html', villes=villes, types=types)

@app.route('/api/pharmacies')
def get_pharmacies():
    search = request.args.get('search', '').lower()
    ville = request.args.get('ville', '')
    type_etablissement = request.args.get('type', '')
    garde_only = request.args.get('garde', '') == 'true'
    gare_only = request.args.get('gare', '') == 'true'
    
    filtered = PHARMACIES
    
    if search:
        filtered = [p for p in filtered if 
                   search in p['nom'].lower() or 
                   search in p['quartier'].lower() or
                   search in (p['services'] or '').lower()]
    
    if ville:
        filtered = [p for p in filtered if p['ville'] == ville]
    
    if type_etablissement:
        filtered = [p for p in filtered if p['type_etablissement'] == type_etablissement]
    
    if garde_only:
        filtered = [p for p in filtered if p['is_garde']]
    
    if gare_only:
        filtered = [p for p in filtered if p['is_gare']]
    
    return jsonify(filtered)

@app.route('/api/stats')
def get_stats():
    stats = {
        'total': len(PHARMACIES),
        'par_ville': {},
        'pharmacies_garde': sum(1 for p in PHARMACIES if p['is_garde']),
        'pharmacies_gare': sum(1 for p in PHARMACIES if p['is_gare'])
    }
    
    for p in PHARMACIES:
        ville = p['ville']
        if ville not in stats['par_ville']:
            stats['par_ville'][ville] = 0
        stats['par_ville'][ville] += 1
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
