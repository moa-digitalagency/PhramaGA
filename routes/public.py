from flask import Blueprint, render_template, jsonify, request
from services.pharmacy_service import PharmacyService

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    villes = PharmacyService.get_distinct_cities()
    return render_template('index.html', villes=villes)


@public_bp.route('/api/pharmacies')
def get_pharmacies():
    search = request.args.get('search', '').lower()
    ville = request.args.get('ville', '')
    garde_only = request.args.get('garde', '') == 'true'
    gare_only = request.args.get('gare', '') == 'true'
    
    pharmacies = PharmacyService.get_all_pharmacies(
        search=search,
        ville=ville,
        garde_only=garde_only,
        gare_only=gare_only
    )
    
    return jsonify([p.to_dict() for p in pharmacies])


@public_bp.route('/api/stats')
def get_stats():
    return jsonify(PharmacyService.get_stats())
