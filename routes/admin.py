from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models.admin import Admin
from models.pharmacy import Pharmacy
from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion
from services.pharmacy_service import PharmacyService
from utils.helpers import safe_float, CITY_COORDINATES
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func

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
    
    top_pharmacies = db.session.query(
        Pharmacy.id, Pharmacy.nom, Pharmacy.ville,
        func.count(PharmacyView.id).label('view_count')
    ).outerjoin(PharmacyView).group_by(Pharmacy.id).order_by(func.count(PharmacyView.id).desc()).limit(10).all()
    
    recent_pharmacies = Pharmacy.query.order_by(Pharmacy.updated_at.desc()).limit(5).all()
    
    total_views = db.session.query(func.count(PharmacyView.id)).scalar() or 0
    
    return render_template('admin/dashboard.html', 
        pharmacies=pharmacies,
        pending_locations=pending_locations,
        pending_infos=pending_infos,
        pending_suggestions=pending_suggestions,
        top_pharmacies=top_pharmacies,
        recent_pharmacies=recent_pharmacies,
        total_views=total_views
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
