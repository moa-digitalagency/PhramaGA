#!/usr/bin/env python3
import csv
import os
import sys

from app import app
from extensions import db
from models.pharmacy import Pharmacy
from utils.helpers import CITY_COORDINATES

def init_demo_data():
    with app.app_context():
        if Pharmacy.query.count() > 0:
            print(f"Database already contains {Pharmacy.query.count()} pharmacies.")
            response = input("Do you want to clear and reimport? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
            Pharmacy.query.delete()
            db.session.commit()
            print("Existing pharmacies cleared.")
        
        csv_path = os.path.join('attached_assets', 'pharmacies_gabon_exhaustive_1765303770607.csv')
        if not os.path.exists(csv_path):
            print(f"Error: CSV file not found at {csv_path}")
            return
        
        quartier_offsets = {}
        count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                if not row.get('id'):
                    continue
                
                ville = row.get('ville', '')
                quartier = row.get('quartier', '')
                
                base_coords = CITY_COORDINATES.get(ville, {"lat": 0.4162, "lng": 9.4673})
                
                offset_key = f"{ville}_{quartier}"
                if offset_key not in quartier_offsets:
                    quartier_offsets[offset_key] = len(quartier_offsets)
                
                offset_idx = quartier_offsets[offset_key] + idx
                lat_offset = (offset_idx % 50) * 0.002 - 0.05
                lng_offset = (offset_idx // 50 % 50) * 0.002 - 0.05
                
                type_etablissement = row.get('type_etablissement', '')
                horaires = row.get('horaires', '')
                nom = row.get('nom', '')
                
                is_garde = 'garde' in type_etablissement.lower() or '24h' in horaires
                is_gare = 'gare' in quartier.lower() or 'gare' in nom.lower()
                
                pharmacy = Pharmacy(
                    code=row['id'],
                    nom=nom,
                    ville=ville,
                    quartier=quartier,
                    telephone=row.get('telephone', ''),
                    bp=row.get('bp', ''),
                    horaires=horaires,
                    services=row.get('services', ''),
                    proprietaire=row.get('proprietaire', ''),
                    type_etablissement=type_etablissement,
                    is_garde=is_garde,
                    is_gare=is_gare,
                    latitude=base_coords['lat'] + lat_offset,
                    longitude=base_coords['lng'] + lng_offset,
                    location_validated=False
                )
                db.session.add(pharmacy)
                count += 1
            
            db.session.commit()
        
        print(f"Successfully imported {count} pharmacies!")
        print("\nNote: Admin user should be created via environment variables:")
        print("  - ADMIN_USERNAME")
        print("  - ADMIN_PASSWORD")

if __name__ == '__main__':
    init_demo_data()
