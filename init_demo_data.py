#!/usr/bin/env python3
"""
UrgenceGabon.com - Initialisation des données de démonstration
Ce script importe les pharmacies depuis un fichier CSV.

Usage: 
  python init_demo_data.py                    # Utilise le fichier par défaut
  python init_demo_data.py pharmacies.csv    # Utilise un fichier spécifique
"""

import os
import sys
import csv
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_CSV_FILE = 'pharmacies.csv'


def parse_csv_row(row):
    """Parse une ligne CSV et retourne un dictionnaire de données pharmacie"""
    latitude = None
    longitude = None
    
    try:
        if row.get('latitude'):
            latitude = float(row['latitude'])
    except (ValueError, TypeError):
        pass
    
    try:
        if row.get('longitude'):
            longitude = float(row['longitude'])
    except (ValueError, TypeError):
        pass
    
    services = row.get('services', '')
    is_garde = 'garde' in services.lower() if services else False
    
    return {
        'code': row.get('id', '').strip(),
        'nom': row.get('nom', '').strip(),
        'ville': row.get('ville', '').strip(),
        'quartier': row.get('quartier', '').strip(),
        'telephone': row.get('telephone', '').strip(),
        'horaires': row.get('horaires', '').strip(),
        'services': services.strip(),
        'latitude': latitude,
        'longitude': longitude,
        'is_garde': is_garde,
        'is_verified': True,
        'location_validated': latitude is not None and longitude is not None,
        'type_etablissement': 'pharmacie_generale',
        'categorie_emplacement': 'standard'
    }


def import_pharmacies_from_csv(csv_file):
    """Importe les pharmacies depuis un fichier CSV"""
    try:
        from app import app
        from extensions import db
        from models.pharmacy import Pharmacy
        
        if not os.path.exists(csv_file):
            logger.error(f"Fichier introuvable: {csv_file}")
            return False, 0
        
        with app.app_context():
            imported = 0
            skipped = 0
            errors = 0
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        data = parse_csv_row(row)
                        
                        if not data['code'] or not data['nom']:
                            logger.warning(f"Ligne ignorée (code ou nom manquant): {row}")
                            skipped += 1
                            continue
                        
                        existing = Pharmacy.query.filter_by(code=data['code']).first()
                        if existing:
                            logger.info(f"Pharmacie existante mise à jour: {data['code']} - {data['nom']}")
                            for key, value in data.items():
                                setattr(existing, key, value)
                        else:
                            pharmacy = Pharmacy(**data)
                            db.session.add(pharmacy)
                            logger.info(f"Pharmacie ajoutée: {data['code']} - {data['nom']}")
                        
                        imported += 1
                        
                    except Exception as e:
                        logger.error(f"Erreur ligne {row}: {e}")
                        errors += 1
                        continue
            
            db.session.commit()
            
            logger.info(f"\nRésumé: {imported} importée(s), {skipped} ignorée(s), {errors} erreur(s)")
            return True, imported
            
    except Exception as e:
        logger.error(f"Erreur lors de l'importation: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def main():
    print("\n" + "="*60)
    print("IMPORTATION DES PHARMACIES - UrgenceGabon.com")
    print("="*60)
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV_FILE
    
    print(f"\nFichier source: {csv_file}")
    
    if not os.path.exists(csv_file):
        print(f"\nERREUR: Le fichier '{csv_file}' n'existe pas.")
        print(f"Créez le fichier ou spécifiez un autre fichier en argument.")
        sys.exit(1)
    
    confirm = input("\nImporter les pharmacies? Tapez 'OUI' pour confirmer: ")
    
    if confirm.strip().upper() != 'OUI':
        print("Opération annulée.")
        sys.exit(0)
    
    success, count = import_pharmacies_from_csv(csv_file)
    
    print("\n" + "="*60)
    if success:
        print(f"Importation terminée: {count} pharmacie(s) importée(s).")
    else:
        print("Erreur lors de l'importation.")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
