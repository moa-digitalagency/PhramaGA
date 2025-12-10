import csv
import os
from datetime import datetime
from extensions import db
from models.pharmacy import Pharmacy
from utils.helpers import CITY_COORDINATES


class PharmacyService:
    @staticmethod
    def get_all_pharmacies(search=None, ville=None, garde_only=False, gare_only=False):
        query = Pharmacy.query
        
        if search:
            search_lower = f'%{search.lower()}%'
            query = query.filter(
                db.or_(
                    Pharmacy.nom.ilike(search_lower),
                    Pharmacy.quartier.ilike(search_lower),
                    Pharmacy.services.ilike(search_lower)
                )
            )
        
        if ville:
            query = query.filter(Pharmacy.ville == ville)
        
        if garde_only:
            query = query.filter(Pharmacy.is_garde == True)
        
        if gare_only:
            query = query.filter(Pharmacy.is_gare == True)
        
        return query.order_by(Pharmacy.nom).all()
    
    @staticmethod
    def get_pharmacy_by_id(pharmacy_id):
        return Pharmacy.query.get_or_404(pharmacy_id)
    
    @staticmethod
    def get_stats():
        total = Pharmacy.query.count()
        garde = Pharmacy.query.filter(Pharmacy.is_garde == True).count()
        gare = Pharmacy.query.filter(Pharmacy.is_gare == True).count()
        validated = Pharmacy.query.filter(Pharmacy.location_validated == True).count()
        
        villes = db.session.query(
            Pharmacy.ville, 
            db.func.count(Pharmacy.id)
        ).group_by(Pharmacy.ville).all()
        
        return {
            'total': total,
            'pharmacies_garde': garde,
            'pharmacies_gare': gare,
            'locations_validated': validated,
            'par_ville': {v: c for v, c in villes}
        }
    
    @staticmethod
    def get_distinct_cities():
        villes = db.session.query(Pharmacy.ville).distinct().order_by(Pharmacy.ville).all()
        return [v[0] for v in villes]
    
    @staticmethod
    def create_pharmacy(data):
        pharmacy = Pharmacy(
            code=data.get('code'),
            nom=data.get('nom'),
            ville=data.get('ville'),
            quartier=data.get('quartier'),
            telephone=data.get('telephone'),
            bp=data.get('bp'),
            horaires=data.get('horaires'),
            services=data.get('services'),
            proprietaire=data.get('proprietaire'),
            type_etablissement=data.get('type_etablissement'),
            is_garde=data.get('is_garde', False),
            is_gare=data.get('is_gare', False),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            location_validated=data.get('location_validated', False)
        )
        db.session.add(pharmacy)
        db.session.commit()
        return pharmacy
    
    @staticmethod
    def update_pharmacy(pharmacy, data):
        pharmacy.code = data.get('code', pharmacy.code)
        pharmacy.nom = data.get('nom', pharmacy.nom)
        pharmacy.ville = data.get('ville', pharmacy.ville)
        pharmacy.quartier = data.get('quartier', pharmacy.quartier)
        pharmacy.telephone = data.get('telephone', pharmacy.telephone)
        pharmacy.bp = data.get('bp', pharmacy.bp)
        pharmacy.horaires = data.get('horaires', pharmacy.horaires)
        pharmacy.services = data.get('services', pharmacy.services)
        pharmacy.proprietaire = data.get('proprietaire', pharmacy.proprietaire)
        pharmacy.type_etablissement = data.get('type_etablissement', pharmacy.type_etablissement)
        pharmacy.is_garde = data.get('is_garde', pharmacy.is_garde)
        pharmacy.is_gare = data.get('is_gare', pharmacy.is_gare)
        
        if 'latitude' in data:
            pharmacy.latitude = data['latitude']
        if 'longitude' in data:
            pharmacy.longitude = data['longitude']
        
        db.session.commit()
        return pharmacy
    
    @staticmethod
    def delete_pharmacy(pharmacy):
        db.session.delete(pharmacy)
        db.session.commit()
    
    @staticmethod
    def toggle_garde(pharmacy):
        pharmacy.is_garde = not pharmacy.is_garde
        db.session.commit()
        return pharmacy.is_garde
    
    @staticmethod
    def validate_location(pharmacy, admin_id):
        pharmacy.location_validated = True
        pharmacy.validated_at = datetime.utcnow()
        pharmacy.validated_by_admin_id = admin_id
        db.session.commit()
        return pharmacy
    
    @staticmethod
    def invalidate_location(pharmacy):
        pharmacy.location_validated = False
        pharmacy.validated_at = None
        pharmacy.validated_by_admin_id = None
        db.session.commit()
        return pharmacy
    
    @staticmethod
    def update_coordinates(pharmacy, latitude, longitude):
        pharmacy.latitude = latitude
        pharmacy.longitude = longitude
        pharmacy.location_validated = False
        pharmacy.validated_at = None
        pharmacy.validated_by_admin_id = None
        db.session.commit()
        return pharmacy
    
    @staticmethod
    def import_csv_data():
        csv_path = os.path.join('attached_assets', 'pharmacies_gabon_exhaustive_1765368648009.csv')
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
                    longitude=base_coords['lng'] + lng_offset,
                    location_validated=False
                )
                db.session.add(pharmacy)
            
            db.session.commit()
