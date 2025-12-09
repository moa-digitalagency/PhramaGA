from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models.admin import Admin
from models.pharmacy import Pharmacy
from services.pharmacy_service import PharmacyService
from utils.helpers import safe_float, CITY_COORDINATES

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
    return render_template('admin/dashboard.html', pharmacies=pharmacies)


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
