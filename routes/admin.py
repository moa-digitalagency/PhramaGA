import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models.admin import Admin
from models.pharmacy import Pharmacy
from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion, PharmacyProposal
from models.emergency_contact import EmergencyContact, EMERGENCY_SERVICE_TYPES
from models.site_settings import SiteSettings, PopupMessage
from services.pharmacy_service import PharmacyService
from utils.helpers import safe_float, CITY_COORDINATES
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_settings_upload_path():
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'settings')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def safe_delete_settings_upload(filename):
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        return
    upload_dir = get_settings_upload_path()
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin.admin_dashboard'))
        flash('Identifiants incorrects', 'error')
    
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('public.index'))


@admin_bp.route('/')
@login_required
def admin_dashboard():
    pharmacies = Pharmacy.query.order_by(Pharmacy.ville, Pharmacy.nom).all()
    
    pending_locations = LocationSubmission.query.filter_by(status='pending').order_by(LocationSubmission.created_at.desc()).all()
    pending_infos = InfoSubmission.query.filter_by(status='pending').order_by(InfoSubmission.created_at.desc()).all()
    pending_suggestions = Suggestion.query.filter_by(status='pending').order_by(Suggestion.created_at.desc()).all()
    pending_proposals = PharmacyProposal.query.filter_by(status='pending').order_by(PharmacyProposal.created_at.desc()).all()
    
    top_pharmacies = db.session.query(
        Pharmacy.id, Pharmacy.nom, Pharmacy.ville,
        func.count(PharmacyView.id).label('view_count')
    ).outerjoin(PharmacyView).group_by(Pharmacy.id).order_by(func.count(PharmacyView.id).desc()).limit(10).all()
    
    recent_pharmacies = Pharmacy.query.order_by(Pharmacy.updated_at.desc()).limit(5).all()
    
    total_views = db.session.query(func.count(PharmacyView.id)).scalar() or 0
    
    views_by_city_query = db.session.query(
        Pharmacy.ville,
        func.count(PharmacyView.id).label('view_count')
    ).join(PharmacyView, Pharmacy.id == PharmacyView.pharmacy_id).group_by(Pharmacy.ville).order_by(func.count(PharmacyView.id).desc()).all()
    views_by_city = [{'ville': row.ville, 'view_count': row.view_count} for row in views_by_city_query]
    
    pharmacies_by_city_query = db.session.query(
        Pharmacy.ville,
        func.count(Pharmacy.id).label('count')
    ).group_by(Pharmacy.ville).order_by(func.count(Pharmacy.id).desc()).all()
    pharmacies_by_city = [{'ville': row.ville, 'count': row.count} for row in pharmacies_by_city_query]
    
    pharmacies_by_type_query = db.session.query(
        Pharmacy.type_etablissement,
        func.count(Pharmacy.id).label('count')
    ).group_by(Pharmacy.type_etablissement).all()
    pharmacies_by_type = [{'type': row.type_etablissement, 'count': row.count} for row in pharmacies_by_type_query]
    
    today = datetime.utcnow().date()
    day_names = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    
    start_7_days = datetime.combine(today - timedelta(days=6), datetime.min.time())
    views_7_days_query = db.session.query(
        func.date(PharmacyView.viewed_at).label('view_date'),
        func.count(PharmacyView.id).label('count')
    ).filter(PharmacyView.viewed_at >= start_7_days).group_by(func.date(PharmacyView.viewed_at)).all()
    views_7_days_dict = {str(row.view_date): row.count for row in views_7_days_query}
    
    views_last_7_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        views_last_7_days.append({
            'date': day.strftime('%d/%m'),
            'day_name': day_names[day.weekday()],
            'count': views_7_days_dict.get(str(day), 0)
        })
    
    start_30_days = datetime.combine(today - timedelta(days=29), datetime.min.time())
    views_30_days_query = db.session.query(
        func.date(PharmacyView.viewed_at).label('view_date'),
        func.count(PharmacyView.id).label('count')
    ).filter(PharmacyView.viewed_at >= start_30_days).group_by(func.date(PharmacyView.viewed_at)).all()
    views_30_days_dict = {str(row.view_date): row.count for row in views_30_days_query}
    
    views_last_30_days = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        views_last_30_days.append({
            'date': day.strftime('%d/%m'),
            'count': views_30_days_dict.get(str(day), 0)
        })
    
    location_counts = db.session.query(
        LocationSubmission.status,
        func.count(LocationSubmission.id)
    ).group_by(LocationSubmission.status).all()
    location_stats = {status: count for status, count in location_counts}
    total_locations = sum(location_stats.values())
    approved_locations = location_stats.get('approved', 0)
    
    info_counts = db.session.query(
        InfoSubmission.status,
        func.count(InfoSubmission.id)
    ).group_by(InfoSubmission.status).all()
    info_stats = {status: count for status, count in info_counts}
    total_infos = sum(info_stats.values())
    approved_infos = info_stats.get('approved', 0)
    
    total_suggestions = Suggestion.query.count()
    
    proposal_counts = db.session.query(
        PharmacyProposal.status,
        func.count(PharmacyProposal.id)
    ).group_by(PharmacyProposal.status).all()
    proposal_stats = {status: count for status, count in proposal_counts}
    total_proposals = sum(proposal_stats.values())
    approved_proposals = proposal_stats.get('approved', 0)
    
    today_start = datetime.combine(today, datetime.min.time())
    week_start = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
    month_start = datetime.combine(today.replace(day=1), datetime.min.time())
    
    period_views = db.session.query(
        func.sum(func.cast(PharmacyView.viewed_at >= today_start, db.Integer)).label('today'),
        func.sum(func.cast(PharmacyView.viewed_at >= week_start, db.Integer)).label('week'),
        func.sum(func.cast(PharmacyView.viewed_at >= month_start, db.Integer)).label('month')
    ).first()
    
    views_today = period_views.today or 0 if period_views else 0
    views_this_week = period_views.week or 0 if period_views else 0
    views_this_month = period_views.month or 0 if period_views else 0
    
    return render_template('admin/dashboard.html', 
        pharmacies=pharmacies,
        pending_locations=pending_locations,
        pending_infos=pending_infos,
        pending_suggestions=pending_suggestions,
        pending_proposals=pending_proposals,
        top_pharmacies=top_pharmacies,
        recent_pharmacies=recent_pharmacies,
        total_views=total_views,
        views_by_city=views_by_city,
        pharmacies_by_city=pharmacies_by_city,
        pharmacies_by_type=pharmacies_by_type,
        views_last_7_days=views_last_7_days,
        views_last_30_days=views_last_30_days,
        total_locations=total_locations,
        approved_locations=approved_locations,
        total_infos=total_infos,
        approved_infos=approved_infos,
        total_suggestions=total_suggestions,
        total_proposals=total_proposals,
        approved_proposals=approved_proposals,
        views_today=views_today,
        views_this_week=views_this_week,
        views_this_month=views_this_month
    )


@admin_bp.route('/pharmacy/add', methods=['GET', 'POST'])
@login_required
def admin_add_pharmacy():
    if request.method == 'POST':
        data = {
            'code': request.form.get('code'),
            'nom': request.form.get('nom'),
            'ville': request.form.get('ville'),
            'quartier': request.form.get('quartier'),
            'telephone': request.form.get('telephone'),
            'bp': request.form.get('bp'),
            'horaires': request.form.get('horaires'),
            'services': request.form.get('services'),
            'proprietaire': request.form.get('proprietaire'),
            'type_etablissement': request.form.get('type_etablissement'),
            'categorie_emplacement': request.form.get('categorie_emplacement'),
            'is_garde': request.form.get('is_garde') == 'on',
            'is_gare': request.form.get('is_gare') == 'on',
            'is_verified': request.form.get('is_verified') == 'on',
            'latitude': safe_float(request.form.get('latitude')),
            'longitude': safe_float(request.form.get('longitude')),
            'location_validated': request.form.get('location_validated') == 'on'
        }
        PharmacyService.create_pharmacy(data)
        flash('Pharmacie ajoutée avec succès', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/pharmacy_form.html', pharmacy=None, cities=list(CITY_COORDINATES.keys()))


@admin_bp.route('/pharmacy/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_pharmacy(id):
    pharmacy = PharmacyService.get_pharmacy_by_id(id)
    
    if request.method == 'POST':
        data = {
            'code': request.form.get('code'),
            'nom': request.form.get('nom'),
            'ville': request.form.get('ville'),
            'quartier': request.form.get('quartier'),
            'telephone': request.form.get('telephone'),
            'bp': request.form.get('bp'),
            'horaires': request.form.get('horaires'),
            'services': request.form.get('services'),
            'proprietaire': request.form.get('proprietaire'),
            'type_etablissement': request.form.get('type_etablissement'),
            'categorie_emplacement': request.form.get('categorie_emplacement'),
            'is_garde': request.form.get('is_garde') == 'on',
            'is_gare': request.form.get('is_gare') == 'on',
            'is_verified': request.form.get('is_verified') == 'on',
            'latitude': safe_float(request.form.get('latitude')),
            'longitude': safe_float(request.form.get('longitude'))
        }
        PharmacyService.update_pharmacy(pharmacy, data)
        flash('Pharmacie mise à jour avec succès', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/pharmacy_form.html', pharmacy=pharmacy, cities=list(CITY_COORDINATES.keys()))


@admin_bp.route('/pharmacy/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_pharmacy(id):
    pharmacy = PharmacyService.get_pharmacy_by_id(id)
    PharmacyService.delete_pharmacy(pharmacy)
    flash('Pharmacie supprimée', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/pharmacy/<int:id>/toggle-garde', methods=['POST'])
@login_required
def admin_toggle_garde(id):
    pharmacy = PharmacyService.get_pharmacy_by_id(id)
    is_garde = PharmacyService.toggle_garde(pharmacy)
    return jsonify({'success': True, 'is_garde': is_garde})


@admin_bp.route('/pharmacy/<int:id>/validate-location', methods=['POST'])
@login_required
def admin_validate_location(id):
    pharmacy = PharmacyService.get_pharmacy_by_id(id)
    PharmacyService.validate_location(pharmacy, current_user.id)
    return jsonify({'success': True, 'location_validated': True})


@admin_bp.route('/pharmacy/<int:id>/invalidate-location', methods=['POST'])
@login_required
def admin_invalidate_location(id):
    pharmacy = PharmacyService.get_pharmacy_by_id(id)
    PharmacyService.invalidate_location(pharmacy)
    return jsonify({'success': True, 'location_validated': False})


@admin_bp.route('/pharmacy/<int:id>/update-coordinates', methods=['POST'])
@login_required
def admin_update_coordinates(id):
    pharmacy = PharmacyService.get_pharmacy_by_id(id)
    data = request.get_json()
    latitude = safe_float(data.get('latitude'))
    longitude = safe_float(data.get('longitude'))
    
    if latitude is not None and longitude is not None:
        PharmacyService.update_coordinates(pharmacy, latitude, longitude)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Coordonnées invalides'}), 400


@admin_bp.route('/pharmacy/<int:id>/set-garde', methods=['POST'])
@login_required
def admin_set_garde(id):
    pharmacy = PharmacyService.get_pharmacy_by_id(id)
    data = request.get_json()
    
    start_date_str = data.get('start_date')
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = start_date + timedelta(days=7)
        
        pharmacy.is_garde = True
        pharmacy.garde_start_date = start_date
        pharmacy.garde_end_date = end_date
    else:
        pharmacy.is_garde = False
        pharmacy.garde_start_date = None
        pharmacy.garde_end_date = None
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'is_garde': pharmacy.is_garde,
        'garde_end_date': pharmacy.garde_end_date.isoformat() if pharmacy.garde_end_date else None
    })


@admin_bp.route('/location-submission/<int:id>/approve', methods=['POST'])
@login_required
def approve_location_submission(id):
    submission = LocationSubmission.query.get_or_404(id)
    pharmacy = submission.pharmacy
    
    pharmacy.latitude = submission.latitude
    pharmacy.longitude = submission.longitude
    pharmacy.location_validated = True
    pharmacy.validated_at = datetime.utcnow()
    pharmacy.validated_by_admin_id = current_user.id
    
    submission.status = 'approved'
    submission.reviewed_at = datetime.utcnow()
    submission.reviewed_by_admin_id = current_user.id
    
    db.session.commit()
    
    return jsonify({'success': True})


@admin_bp.route('/location-submission/<int:id>/reject', methods=['POST'])
@login_required
def reject_location_submission(id):
    submission = LocationSubmission.query.get_or_404(id)
    
    submission.status = 'rejected'
    submission.reviewed_at = datetime.utcnow()
    submission.reviewed_by_admin_id = current_user.id
    
    db.session.commit()
    
    return jsonify({'success': True})


@admin_bp.route('/info-submission/<int:id>/approve', methods=['POST'])
@login_required
def approve_info_submission(id):
    submission = InfoSubmission.query.get_or_404(id)
    pharmacy = submission.pharmacy
    
    if hasattr(pharmacy, submission.field_name):
        setattr(pharmacy, submission.field_name, submission.proposed_value)
    
    submission.status = 'approved'
    submission.reviewed_at = datetime.utcnow()
    submission.reviewed_by_admin_id = current_user.id
    
    db.session.commit()
    
    return jsonify({'success': True})


@admin_bp.route('/info-submission/<int:id>/reject', methods=['POST'])
@login_required
def reject_info_submission(id):
    submission = InfoSubmission.query.get_or_404(id)
    
    submission.status = 'rejected'
    submission.reviewed_at = datetime.utcnow()
    submission.reviewed_by_admin_id = current_user.id
    
    db.session.commit()
    
    return jsonify({'success': True})


@admin_bp.route('/suggestion/<int:id>/respond', methods=['POST'])
@login_required
def respond_suggestion(id):
    suggestion = Suggestion.query.get_or_404(id)
    data = request.get_json()
    
    suggestion.admin_response = data.get('response', '')
    suggestion.status = 'resolved'
    suggestion.reviewed_at = datetime.utcnow()
    suggestion.reviewed_by_admin_id = current_user.id
    
    db.session.commit()
    
    return jsonify({'success': True})


@admin_bp.route('/suggestion/<int:id>/archive', methods=['POST'])
@login_required
def archive_suggestion(id):
    suggestion = Suggestion.query.get_or_404(id)
    
    suggestion.status = 'archived'
    suggestion.reviewed_at = datetime.utcnow()
    suggestion.reviewed_by_admin_id = current_user.id
    
    db.session.commit()
    
    return jsonify({'success': True})


@admin_bp.route('/pharmacy-proposal/<int:id>/approve', methods=['POST'])
@login_required
def approve_pharmacy_proposal(id):
    proposal = PharmacyProposal.query.get_or_404(id)
    
    import random
    import string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    pharmacy = Pharmacy(
        code=f"NEW{code}",
        nom=proposal.nom,
        ville=proposal.ville,
        quartier=proposal.quartier,
        telephone=proposal.telephone,
        bp=proposal.bp,
        horaires=proposal.horaires,
        services=proposal.services,
        proprietaire=proposal.proprietaire,
        type_etablissement=proposal.type_etablissement or 'pharmacie_generale',
        categorie_emplacement=proposal.categorie_emplacement or 'standard',
        is_garde=proposal.is_garde,
        latitude=proposal.latitude,
        longitude=proposal.longitude,
        is_verified=False
    )
    
    db.session.add(pharmacy)
    
    proposal.status = 'approved'
    proposal.reviewed_at = datetime.utcnow()
    proposal.reviewed_by_admin_id = current_user.id
    
    db.session.commit()
    
    return jsonify({'success': True, 'pharmacy_id': pharmacy.id})


@admin_bp.route('/pharmacy-proposal/<int:id>/reject', methods=['POST'])
@login_required
def reject_pharmacy_proposal(id):
    proposal = PharmacyProposal.query.get_or_404(id)
    
    proposal.status = 'rejected'
    proposal.reviewed_at = datetime.utcnow()
    proposal.reviewed_by_admin_id = current_user.id
    
    db.session.commit()
    
    return jsonify({'success': True})


@admin_bp.route('/emergency-contacts')
@login_required
def list_emergency_contacts():
    contacts = EmergencyContact.query.order_by(EmergencyContact.ordering).all()
    return render_template('admin/emergency_contacts.html', 
                          contacts=contacts, 
                          service_types=EMERGENCY_SERVICE_TYPES,
                          cities=list(CITY_COORDINATES.keys()))


@admin_bp.route('/emergency-contact/add', methods=['GET', 'POST'])
@login_required
def add_emergency_contact():
    if request.method == 'POST':
        contact = EmergencyContact(
            ville=request.form.get('ville') or None,
            service_type=request.form.get('service_type'),
            label=request.form.get('label'),
            phone_numbers=request.form.get('phone_numbers'),
            address=request.form.get('address', ''),
            notes=request.form.get('notes', ''),
            is_national=request.form.get('is_national') == 'on',
            is_active=request.form.get('is_active') == 'on',
            ordering=int(request.form.get('ordering', 0))
        )
        db.session.add(contact)
        db.session.commit()
        flash('Contact d\'urgence ajouté avec succès', 'success')
        return redirect(url_for('admin.list_emergency_contacts'))
    
    return render_template('admin/emergency_contact_form.html', 
                          contact=None, 
                          service_types=EMERGENCY_SERVICE_TYPES,
                          cities=list(CITY_COORDINATES.keys()))


@admin_bp.route('/emergency-contact/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_emergency_contact(id):
    contact = EmergencyContact.query.get_or_404(id)
    
    if request.method == 'POST':
        contact.ville = request.form.get('ville') or None
        contact.service_type = request.form.get('service_type')
        contact.label = request.form.get('label')
        contact.phone_numbers = request.form.get('phone_numbers')
        contact.address = request.form.get('address', '')
        contact.notes = request.form.get('notes', '')
        contact.is_national = request.form.get('is_national') == 'on'
        contact.is_active = request.form.get('is_active') == 'on'
        contact.ordering = int(request.form.get('ordering', 0))
        
        db.session.commit()
        flash('Contact d\'urgence mis à jour', 'success')
        return redirect(url_for('admin.list_emergency_contacts'))
    
    return render_template('admin/emergency_contact_form.html', 
                          contact=contact, 
                          service_types=EMERGENCY_SERVICE_TYPES,
                          cities=list(CITY_COORDINATES.keys()))


@admin_bp.route('/emergency-contact/<int:id>/delete', methods=['POST'])
@login_required
def delete_emergency_contact(id):
    contact = EmergencyContact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact d\'urgence supprimé', 'success')
    return redirect(url_for('admin.list_emergency_contacts'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def site_settings():
    if request.method == 'POST':
        settings_keys = [
            'site_name', 'site_description',
            'site_timezone', 'contact_email', 'contact_phone',
            'og_title', 'og_description',
            'meta_keywords', 'google_analytics_id', 'header_code'
        ]
        
        for key in settings_keys:
            value = request.form.get(key, '')
            SiteSettings.set(key, value)
        
        upload_dir = get_settings_upload_path()
        
        if request.form.get('remove_logo') == 'on':
            old_filename = SiteSettings.get('site_logo_filename')
            if old_filename:
                safe_delete_settings_upload(old_filename)
                SiteSettings.set('site_logo_filename', '')
        
        if request.form.get('remove_favicon') == 'on':
            old_filename = SiteSettings.get('site_favicon_filename')
            if old_filename:
                safe_delete_settings_upload(old_filename)
                SiteSettings.set('site_favicon_filename', '')
        
        if request.form.get('remove_og_image') == 'on':
            old_filename = SiteSettings.get('og_image_filename')
            if old_filename:
                safe_delete_settings_upload(old_filename)
                SiteSettings.set('og_image_filename', '')
        
        if 'site_logo_file' in request.files:
            file = request.files['site_logo_file']
            if file and file.filename and allowed_file(file.filename):
                old_filename = SiteSettings.get('site_logo_filename')
                if old_filename:
                    safe_delete_settings_upload(old_filename)
                
                original_filename = secure_filename(file.filename)
                ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'png'
                new_filename = f"logo_{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(upload_dir, new_filename))
                SiteSettings.set('site_logo_filename', new_filename)
        
        if 'site_favicon_file' in request.files:
            file = request.files['site_favicon_file']
            if file and file.filename and allowed_file(file.filename):
                old_filename = SiteSettings.get('site_favicon_filename')
                if old_filename:
                    safe_delete_settings_upload(old_filename)
                
                original_filename = secure_filename(file.filename)
                ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'ico'
                new_filename = f"favicon_{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(upload_dir, new_filename))
                SiteSettings.set('site_favicon_filename', new_filename)
        
        if 'og_image_file' in request.files:
            file = request.files['og_image_file']
            if file and file.filename and allowed_file(file.filename):
                old_filename = SiteSettings.get('og_image_filename')
                if old_filename:
                    safe_delete_settings_upload(old_filename)
                
                original_filename = secure_filename(file.filename)
                ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
                new_filename = f"og_image_{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(upload_dir, new_filename))
                SiteSettings.set('og_image_filename', new_filename)
        
        flash('Paramètres enregistrés avec succès', 'success')
        return redirect(url_for('admin.site_settings'))
    
    settings = SiteSettings.get_all()
    return render_template('admin/settings.html', settings=settings)


@admin_bp.route('/popups')
@login_required
def list_popups():
    popups = PopupMessage.query.order_by(PopupMessage.ordering, PopupMessage.created_at.desc()).all()
    return render_template('admin/popups.html', popups=popups)


def get_upload_path():
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'popups')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

@admin_bp.route('/popup/add', methods=['GET', 'POST'])
@login_required
def add_popup():
    if request.method == 'POST':
        image_filename = None
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                original_filename = secure_filename(file.filename)
                ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
                image_filename = f"{uuid.uuid4().hex}.{ext}"
                upload_dir = get_upload_path()
                upload_path = os.path.join(upload_dir, image_filename)
                file.save(upload_path)
        
        popup = PopupMessage(
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            warning_text=request.form.get('warning_text', ''),
            image_url='',
            image_filename=image_filename,
            is_active=request.form.get('is_active') == 'on',
            show_once=request.form.get('show_once') == 'on',
            ordering=int(request.form.get('ordering', 0))
        )
        db.session.add(popup)
        db.session.commit()
        flash('Popup ajouté avec succès', 'success')
        return redirect(url_for('admin.list_popups'))
    
    return render_template('admin/popup_form.html', popup=None)


def safe_delete_upload(filename):
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        return
    upload_dir = get_upload_path()
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)

@admin_bp.route('/popup/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_popup(id):
    popup = PopupMessage.query.get_or_404(id)
    
    if request.method == 'POST':
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                if popup.image_filename:
                    safe_delete_upload(popup.image_filename)
                
                original_filename = secure_filename(file.filename)
                ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
                popup.image_filename = f"{uuid.uuid4().hex}.{ext}"
                upload_dir = get_upload_path()
                upload_path = os.path.join(upload_dir, popup.image_filename)
                file.save(upload_path)
        
        if request.form.get('remove_image') == 'on':
            if popup.image_filename:
                safe_delete_upload(popup.image_filename)
                popup.image_filename = None
            popup.image_url = ''
        
        popup.title = request.form.get('title')
        popup.description = request.form.get('description', '')
        popup.warning_text = request.form.get('warning_text', '')
        popup.is_active = request.form.get('is_active') == 'on'
        popup.show_once = request.form.get('show_once') == 'on'
        popup.ordering = int(request.form.get('ordering', 0))
        
        db.session.commit()
        flash('Popup mis à jour', 'success')
        return redirect(url_for('admin.list_popups'))
    
    return render_template('admin/popup_form.html', popup=popup)


@admin_bp.route('/popup/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_popup(id):
    popup = PopupMessage.query.get_or_404(id)
    popup.is_active = not popup.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': popup.is_active})


@admin_bp.route('/popup/<int:id>/delete', methods=['POST'])
@login_required
def delete_popup(id):
    popup = PopupMessage.query.get_or_404(id)
    db.session.delete(popup)
    db.session.commit()
    flash('Popup supprimé', 'success')
    return redirect(url_for('admin.list_popups'))
