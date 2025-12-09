from flask import Blueprint, render_template, jsonify, request
from services.pharmacy_service import PharmacyService
from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion
from models.pharmacy import Pharmacy
from extensions import db

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


@public_bp.route('/api/pharmacy/<int:id>/view', methods=['POST'])
def record_view(id):
    pharmacy = Pharmacy.query.get_or_404(id)
    view = PharmacyView(pharmacy_id=pharmacy.id)
    db.session.add(view)
    db.session.commit()
    return jsonify({'success': True})


@public_bp.route('/api/pharmacy/<int:id>/submit-location', methods=['POST'])
def submit_location(id):
    pharmacy = Pharmacy.query.get_or_404(id)
    data = request.get_json()
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if latitude is None or longitude is None:
        return jsonify({'success': False, 'error': 'Coordonnées manquantes'}), 400
    
    submission = LocationSubmission(
        pharmacy_id=pharmacy.id,
        latitude=float(latitude),
        longitude=float(longitude),
        submitted_by_name=data.get('name', ''),
        submitted_by_phone=data.get('phone', ''),
        comment=data.get('comment', '')
    )
    db.session.add(submission)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Localisation soumise avec succès'})


@public_bp.route('/api/pharmacy/<int:id>/submit-info', methods=['POST'])
def submit_info(id):
    pharmacy = Pharmacy.query.get_or_404(id)
    data = request.get_json()
    
    field_name = data.get('field_name')
    proposed_value = data.get('proposed_value')
    
    if not field_name or not proposed_value:
        return jsonify({'success': False, 'error': 'Informations manquantes'}), 400
    
    current_value = getattr(pharmacy, field_name, '') or ''
    
    submission = InfoSubmission(
        pharmacy_id=pharmacy.id,
        field_name=field_name,
        current_value=str(current_value),
        proposed_value=proposed_value,
        submitted_by_name=data.get('name', ''),
        submitted_by_phone=data.get('phone', ''),
        comment=data.get('comment', '')
    )
    db.session.add(submission)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Information soumise avec succès'})


@public_bp.route('/api/suggestions', methods=['POST'])
def submit_suggestion():
    data = request.get_json()
    
    category = data.get('category')
    subject = data.get('subject')
    message = data.get('message')
    
    if not category or not subject or not message:
        return jsonify({'success': False, 'error': 'Veuillez remplir tous les champs obligatoires'}), 400
    
    suggestion = Suggestion(
        category=category,
        subject=subject,
        message=message,
        submitted_by_name=data.get('name', ''),
        submitted_by_email=data.get('email', ''),
        submitted_by_phone=data.get('phone', '')
    )
    db.session.add(suggestion)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Suggestion envoyée avec succès'})
