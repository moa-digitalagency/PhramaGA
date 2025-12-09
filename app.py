from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import csv

def safe_float(value):
    """Safely convert a value to float, returning None for empty/invalid values."""
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

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

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Pharmacy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    quartier = db.Column(db.String(200))
    telephone = db.Column(db.String(100))
    bp = db.Column(db.String(50))
    horaires = db.Column(db.String(200))
    services = db.Column(db.Text)
    proprietaire = db.Column(db.String(200))
    type_etablissement = db.Column(db.String(100))
    is_garde = db.Column(db.Boolean, default=False)
    is_gare = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'nom': self.nom,
            'ville': self.ville,
            'quartier': self.quartier or '',
            'telephone': self.telephone or '',
            'bp': self.bp or '',
            'horaires': self.horaires or '',
            'services': self.services or '',
            'proprietaire': self.proprietaire or '',
            'type_etablissement': self.type_etablissement or '',
            'is_garde': self.is_garde,
            'is_gare': self.is_gare,
            'lat': self.latitude,
            'lng': self.longitude
        }

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/')
def index():
    villes = db.session.query(Pharmacy.ville).distinct().order_by(Pharmacy.ville).all()
    villes = [v[0] for v in villes]
    return render_template('index.html', villes=villes)

@app.route('/api/pharmacies')
def get_pharmacies():
    query = Pharmacy.query
    
    search = request.args.get('search', '').lower()
    ville = request.args.get('ville', '')
    garde_only = request.args.get('garde', '') == 'true'
    gare_only = request.args.get('gare', '') == 'true'
    
    if search:
        query = query.filter(
            db.or_(
                Pharmacy.nom.ilike(f'%{search}%'),
                Pharmacy.quartier.ilike(f'%{search}%'),
                Pharmacy.services.ilike(f'%{search}%')
            )
        )
    
    if ville:
        query = query.filter(Pharmacy.ville == ville)
    
    if garde_only:
        query = query.filter(Pharmacy.is_garde == True)
    
    if gare_only:
        query = query.filter(Pharmacy.is_gare == True)
    
    pharmacies = query.order_by(Pharmacy.nom).all()
    return jsonify([p.to_dict() for p in pharmacies])

@app.route('/api/stats')
def get_stats():
    total = Pharmacy.query.count()
    garde = Pharmacy.query.filter(Pharmacy.is_garde == True).count()
    gare = Pharmacy.query.filter(Pharmacy.is_gare == True).count()
    
    villes = db.session.query(Pharmacy.ville, db.func.count(Pharmacy.id)).group_by(Pharmacy.ville).all()
    
    return jsonify({
        'total': total,
        'pharmacies_garde': garde,
        'pharmacies_gare': gare,
        'par_ville': {v: c for v, c in villes}
    })

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Identifiants incorrects', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    pharmacies = Pharmacy.query.order_by(Pharmacy.ville, Pharmacy.nom).all()
    return render_template('admin/dashboard.html', pharmacies=pharmacies)

@app.route('/admin/pharmacy/add', methods=['GET', 'POST'])
@login_required
def admin_add_pharmacy():
    if request.method == 'POST':
        pharmacy = Pharmacy(
            code=request.form.get('code'),
            nom=request.form.get('nom'),
            ville=request.form.get('ville'),
            quartier=request.form.get('quartier'),
            telephone=request.form.get('telephone'),
            bp=request.form.get('bp'),
            horaires=request.form.get('horaires'),
            services=request.form.get('services'),
            proprietaire=request.form.get('proprietaire'),
            type_etablissement=request.form.get('type_etablissement'),
            is_garde=request.form.get('is_garde') == 'on',
            is_gare=request.form.get('is_gare') == 'on',
            latitude=safe_float(request.form.get('latitude')),
            longitude=safe_float(request.form.get('longitude'))
        )
        db.session.add(pharmacy)
        db.session.commit()
        flash('Pharmacie ajoutée avec succès', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/pharmacy_form.html', pharmacy=None, cities=list(CITY_COORDINATES.keys()))

@app.route('/admin/pharmacy/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_pharmacy(id):
    pharmacy = Pharmacy.query.get_or_404(id)
    
    if request.method == 'POST':
        pharmacy.code = request.form.get('code')
        pharmacy.nom = request.form.get('nom')
        pharmacy.ville = request.form.get('ville')
        pharmacy.quartier = request.form.get('quartier')
        pharmacy.telephone = request.form.get('telephone')
        pharmacy.bp = request.form.get('bp')
        pharmacy.horaires = request.form.get('horaires')
        pharmacy.services = request.form.get('services')
        pharmacy.proprietaire = request.form.get('proprietaire')
        pharmacy.type_etablissement = request.form.get('type_etablissement')
        pharmacy.is_garde = request.form.get('is_garde') == 'on'
        pharmacy.is_gare = request.form.get('is_gare') == 'on'
        pharmacy.latitude = safe_float(request.form.get('latitude'))
        pharmacy.longitude = safe_float(request.form.get('longitude'))
        
        db.session.commit()
        flash('Pharmacie mise à jour avec succès', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/pharmacy_form.html', pharmacy=pharmacy, cities=list(CITY_COORDINATES.keys()))

@app.route('/admin/pharmacy/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_pharmacy(id):
    pharmacy = Pharmacy.query.get_or_404(id)
    db.session.delete(pharmacy)
    db.session.commit()
    flash('Pharmacie supprimée', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/pharmacy/<int:id>/toggle-garde', methods=['POST'])
@login_required
def admin_toggle_garde(id):
    pharmacy = Pharmacy.query.get_or_404(id)
    pharmacy.is_garde = not pharmacy.is_garde
    db.session.commit()
    return jsonify({'success': True, 'is_garde': pharmacy.is_garde})

def init_db():
    with app.app_context():
        db.create_all()
        
        if Admin.query.count() == 0:
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        if Pharmacy.query.count() == 0:
            import_csv_data()

def import_csv_data():
    csv_path = os.path.join('attached_assets', 'pharmacies_gabon_exhaustive_1765303770607.csv')
    if not os.path.exists(csv_path):
        return
    
    quartier_offsets = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if not row['id']:
                continue
            
            ville = row['ville']
            quartier = row['quartier']
            
            base_coords = CITY_COORDINATES.get(ville, {"lat": 0.4162, "lng": 9.4673})
            
            offset_key = f"{ville}_{quartier}"
            if offset_key not in quartier_offsets:
                quartier_offsets[offset_key] = len(quartier_offsets)
            
            offset_idx = quartier_offsets[offset_key] + idx
            lat_offset = (offset_idx % 50) * 0.002 - 0.05
            lng_offset = (offset_idx // 50 % 50) * 0.002 - 0.05
            
            is_garde = 'garde' in row['type_etablissement'].lower() or '24h' in row['horaires']
            is_gare = 'gare' in row['quartier'].lower() or 'gare' in row['nom'].lower()
            
            pharmacy = Pharmacy(
                code=row['id'],
                nom=row['nom'],
                ville=ville,
                quartier=quartier,
                telephone=row['telephone'],
                bp=row['bp'],
                horaires=row['horaires'],
                services=row['services'],
                proprietaire=row['proprietaire'],
                type_etablissement=row['type_etablissement'],
                is_garde=is_garde,
                is_gare=is_gare,
                latitude=base_coords['lat'] + lat_offset,
                longitude=base_coords['lng'] + lng_offset
            )
            db.session.add(pharmacy)
        
        db.session.commit()

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
