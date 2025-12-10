from flask import Blueprint, render_template, jsonify, request
from markupsafe import Markup
from services.pharmacy_service import PharmacyService
from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion, PharmacyProposal
from models.pharmacy import Pharmacy
from models.emergency_contact import EmergencyContact
from models.site_settings import PopupMessage, SiteSettings
from models.advertisement import Advertisement, AdSettings
from extensions import db

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    villes = PharmacyService.get_distinct_cities()
    total_pharmacies = Pharmacy.query.count()
    
    national_contacts = EmergencyContact.query.filter_by(is_national=True, is_active=True).order_by(EmergencyContact.ordering).all()
    city_contacts = EmergencyContact.query.filter_by(is_national=False, is_active=True).order_by(EmergencyContact.ordering).all()
    
    contacts_by_city = {}
    for contact in city_contacts:
        if contact.ville not in contacts_by_city:
            contacts_by_city[contact.ville] = []
        contacts_by_city[contact.ville].append(contact)
    
    header_code = SiteSettings.get('header_code', '')
    favicon_url = SiteSettings.get_favicon_url()
    logo_url = SiteSettings.get_logo_url()
    og_image_url = SiteSettings.get_og_image_url()
    site_name = SiteSettings.get('site_name', 'Pharmacies Gabon')
    og_title = SiteSettings.get('og_title', 'Pharmacies Gabon - Trouvez votre pharmacie')
    og_description = SiteSettings.get('og_description', '')
    
    return render_template('index.html', 
                          villes=villes, 
                          total_pharmacies=total_pharmacies,
                          national_contacts=national_contacts,
                          contacts_by_city=contacts_by_city,
                          header_code=Markup(header_code) if header_code else '',
                          favicon_url=favicon_url,
                          logo_url=logo_url,
                          og_image_url=og_image_url,
                          site_name=site_name,
                          og_title=og_title,
                          og_description=og_description)


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


@public_bp.route('/api/pharmacy-proposal', methods=['POST'])
def submit_pharmacy_proposal():
    data = request.get_json()
    
    nom = data.get('nom')
    ville = data.get('ville')
    
    if not nom or not ville:
        return jsonify({'success': False, 'error': 'Le nom et la ville sont obligatoires'}), 400
    
    proposal = PharmacyProposal(
        nom=nom,
        ville=ville,
        quartier=data.get('quartier', ''),
        telephone=data.get('telephone', ''),
        bp=data.get('bp', ''),
        horaires=data.get('horaires', ''),
        services=data.get('services', ''),
        proprietaire=data.get('proprietaire', ''),
        type_etablissement=data.get('type_etablissement', 'pharmacie_generale'),
        categorie_emplacement=data.get('categorie_emplacement', 'standard'),
        is_garde=data.get('is_garde', False),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        submitted_by_name=data.get('name', ''),
        submitted_by_email=data.get('email', ''),
        submitted_by_phone=data.get('phone', ''),
        comment=data.get('comment', '')
    )
    db.session.add(proposal)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Proposition de pharmacie envoyée avec succès'})


@public_bp.route('/api/popups')
def get_active_popups():
    popups = PopupMessage.query.filter_by(is_active=True).order_by(PopupMessage.ordering).all()
    return jsonify([p.to_dict() for p in popups])


@public_bp.route('/api/ads/settings')
def get_ad_settings():
    settings = AdSettings.get_settings()
    return jsonify(settings.to_dict())


@public_bp.route('/api/ads/random')
def get_random_ad():
    import random
    from datetime import datetime
    
    now = datetime.utcnow()
    active_ads = Advertisement.query.filter(
        Advertisement.is_active == True,
        db.or_(Advertisement.start_date == None, Advertisement.start_date <= now),
        db.or_(Advertisement.end_date == None, Advertisement.end_date >= now)
    ).all()
    
    if not active_ads:
        return jsonify(None)
    
    weighted_ads = []
    for ad in active_ads:
        weight = max(1, ad.priority + 1)
        weighted_ads.extend([ad] * weight)
    
    selected_ad = random.choice(weighted_ads)
    
    settings = AdSettings.get_settings()
    skip_delay = selected_ad.skip_delay if selected_ad.skip_delay > 0 else settings.default_skip_delay
    
    ad_data = selected_ad.to_dict()
    ad_data['skip_delay'] = skip_delay
    
    return jsonify(ad_data)


@public_bp.route('/api/ads/<int:id>/view', methods=['POST'])
def record_ad_view(id):
    ad = Advertisement.query.get_or_404(id)
    ad.view_count = (ad.view_count or 0) + 1
    db.session.commit()
    return jsonify({'success': True})


@public_bp.route('/api/ads/<int:id>/click', methods=['POST'])
def record_ad_click(id):
    ad = Advertisement.query.get_or_404(id)
    ad.click_count = (ad.click_count or 0) + 1
    db.session.commit()
    return jsonify({'success': True})
