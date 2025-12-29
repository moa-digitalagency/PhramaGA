#!/usr/bin/env python3
"""
UrgenceGabon.com - Script de chargement des données de pharmacies
Charge les données des pharmacies dans la base de données
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

env_file = Path('.env')
if env_file.exists():
    load_dotenv(env_file)

from app import app, db
from models.pharmacy import Pharmacy

# Données de pharmacies pour Libreville
PHARMACIES_DATA = [
    {
        'code': 'PH001',
        'nom': 'Pharmacie Centrale',
        'ville': 'Libreville',
        'quartier': 'Centre-ville',
        'telephone': '+241 01 45 23 45',
        'bp': 'BP 123',
        'horaires': '07:00-22:00',
        'proprietaire': 'Dr. Jean Pierre',
        'type_etablissement': 'pharmacie_generale',
        'categorie_emplacement': 'centre_ville',
        'latitude': 0.4162,
        'longitude': 9.4673,
        'is_garde': True,
        'services': 'Consultation, Vaccinations, Vente de médicaments',
        'location_validated': True,
        'is_verified': True,
    },
    {
        'code': 'PH002',
        'nom': 'Pharmacie du Port',
        'ville': 'Libreville',
        'quartier': 'Akébé',
        'telephone': '+241 01 45 23 46',
        'bp': 'BP 456',
        'horaires': '06:00-23:00',
        'proprietaire': 'Mme Angélique',
        'type_etablissement': 'pharmacie_generale',
        'categorie_emplacement': 'standard',
        'latitude': 0.4150,
        'longitude': 9.4700,
        'is_garde': False,
        'services': 'Vente de médicaments, Conseil pharmaceutique',
        'location_validated': True,
        'is_verified': True,
    },
    {
        'code': 'PH003',
        'nom': 'Pharmacie Moderne',
        'ville': 'Libreville',
        'quartier': 'Gros Bouquet',
        'telephone': '+241 01 45 23 47',
        'bp': 'BP 789',
        'horaires': '07:30-22:30',
        'proprietaire': 'Dr. Paul Mbadinga',
        'type_etablissement': 'pharmacie_hospitaliere',
        'categorie_emplacement': 'hopital',
        'latitude': 0.4200,
        'longitude': 9.4650,
        'is_garde': True,
        'services': 'Service d\'urgence 24h/24, Consultation spécialisée',
        'location_validated': True,
        'is_verified': True,
    },
    {
        'code': 'PH004',
        'nom': 'Pharmacie de Nuit',
        'ville': 'Libreville',
        'quartier': 'La Sablière',
        'telephone': '+241 01 45 23 48',
        'bp': 'BP 111',
        'horaires': '21:00-08:00',
        'proprietaire': 'M. Eric',
        'type_etablissement': 'pharmacie_generale',
        'categorie_emplacement': 'centre_ville',
        'latitude': 0.4180,
        'longitude': 9.4690,
        'is_garde': True,
        'services': 'Service de nuit, Urgences',
        'location_validated': True,
        'is_verified': True,
    },
    {
        'code': 'PH005',
        'nom': 'Pharmacie Familiale',
        'ville': 'Libreville',
        'quartier': 'Plein Ciel',
        'telephone': '+241 01 45 23 49',
        'bp': 'BP 222',
        'horaires': '07:00-21:00',
        'proprietaire': 'Mme Martine',
        'type_etablissement': 'pharmacie_generale',
        'categorie_emplacement': 'zone_residentielle',
        'latitude': 0.4140,
        'longitude': 9.4660,
        'is_garde': False,
        'services': 'Vente de médicaments, Service de parapharmaceutique',
        'location_validated': True,
        'is_verified': True,
    },
    {
        'code': 'PH006',
        'nom': 'Pharmacie Express',
        'ville': 'Libreville',
        'quartier': 'Deido',
        'telephone': '+241 01 45 23 50',
        'bp': 'BP 333',
        'horaires': '06:00-22:00',
        'proprietaire': 'Dr. Laurent',
        'type_etablissement': 'depot_pharmaceutique',
        'categorie_emplacement': 'centre_commercial',
        'latitude': 0.4170,
        'longitude': 9.4680,
        'is_garde': False,
        'services': 'Vente en gros et détail',
        'location_validated': True,
        'is_verified': True,
    },
    {
        'code': 'PH007',
        'nom': 'Pharmacie Médicale',
        'ville': 'Libreville',
        'quartier': 'Mont-Bouët',
        'telephone': '+241 01 45 23 51',
        'bp': 'BP 444',
        'horaires': '07:00-20:00',
        'proprietaire': 'Dr. Sophie',
        'type_etablissement': 'pharmacie_hospitaliere',
        'categorie_emplacement': 'hopital',
        'latitude': 0.4190,
        'longitude': 9.4700,
        'is_garde': True,
        'services': 'Pharmacie hospitalière, Service d\'urgence',
        'location_validated': True,
        'is_verified': True,
    },
    {
        'code': 'PH008',
        'nom': 'Pharmacie Santé Plus',
        'ville': 'Libreville',
        'quartier': 'Nzeng Ayong',
        'telephone': '+241 01 45 23 52',
        'bp': 'BP 555',
        'horaires': '07:30-21:30',
        'proprietaire': 'M. Joseph',
        'type_etablissement': 'pharmacie_generale',
        'categorie_emplacement': 'zone_residentielle',
        'latitude': 0.4130,
        'longitude': 9.4670,
        'is_garde': False,
        'services': 'Consultation, Vente de médicaments, Conseil',
        'location_validated': True,
        'is_verified': True,
    },
    {
        'code': 'PH009',
        'nom': 'Pharmacie de l\'Aéroport',
        'ville': 'Libreville',
        'quartier': 'Aéroport',
        'telephone': '+241 01 45 23 53',
        'bp': 'BP 666',
        'horaires': '06:00-23:00',
        'proprietaire': 'Aéroports Gabon',
        'type_etablissement': 'pharmacie_generale',
        'categorie_emplacement': 'aeroport',
        'latitude': 0.4100,
        'longitude': 9.4500,
        'is_garde': True,
        'services': 'Vente 24h/24, Urgences, Pharmacie internationale',
        'location_validated': True,
        'is_verified': True,
    },
    {
        'code': 'PH010',
        'nom': 'Pharmacie Gare',
        'ville': 'Libreville',
        'quartier': 'Gare',
        'telephone': '+241 01 45 23 54',
        'bp': 'BP 777',
        'horaires': '06:00-21:00',
        'proprietaire': 'SNFT',
        'type_etablissement': 'pharmacie_generale',
        'categorie_emplacement': 'gare',
        'latitude': 0.4220,
        'longitude': 9.4750,
        'is_garde': False,
        'services': 'Vente de médicaments, Consultation',
        'location_validated': True,
        'is_verified': True,
    },
]


def load_pharmacies_data():
    """Charge les données des pharmacies dans la base de données"""
    with app.app_context():
        print("\n" + "=" * 90)
        print("CHARGEMENT DES DONNÉES DE PHARMACIES")
        print("=" * 90)
        
        # Vérifier si des pharmacies existent déjà
        existing_count = Pharmacy.query.count()
        print(f"\nPharmacies existantes: {existing_count}")
        
        if existing_count > 0:
            print("⚠️  Des pharmacies existent déjà. Vous pouvez:")
            print("   1. Ajouter de nouvelles pharmacies (doublon possible sur codes)")
            print("   2. Supprimer les anciennes et recharger")
            response = input("\nVoulez-vous ajouter les nouvelles pharmacies? (oui/non): ").strip().lower()
            if response != 'oui':
                print("Chargement annulé.")
                return False
        
        print(f"\n📝 Chargement de {len(PHARMACIES_DATA)} pharmacies...")
        
        added = 0
        skipped = 0
        errors = 0
        
        for pharmacy_data in PHARMACIES_DATA:
            try:
                # Vérifier si la pharmacie existe déjà
                existing = Pharmacy.query.filter_by(code=pharmacy_data['code']).first()
                if existing:
                    print(f"  ⏭️  {pharmacy_data['code']} - {pharmacy_data['nom']}: Existe déjà (skipped)")
                    skipped += 1
                    continue
                
                # Créer la nouvelle pharmacie
                pharmacy = Pharmacy(
                    code=pharmacy_data['code'],
                    nom=pharmacy_data['nom'],
                    ville=pharmacy_data['ville'],
                    quartier=pharmacy_data['quartier'],
                    telephone=pharmacy_data['telephone'],
                    bp=pharmacy_data['bp'],
                    horaires=pharmacy_data['horaires'],
                    proprietaire=pharmacy_data['proprietaire'],
                    type_etablissement=pharmacy_data['type_etablissement'],
                    categorie_emplacement=pharmacy_data['categorie_emplacement'],
                    latitude=pharmacy_data['latitude'],
                    longitude=pharmacy_data['longitude'],
                    is_garde=pharmacy_data['is_garde'],
                    services=pharmacy_data['services'],
                    location_validated=pharmacy_data['location_validated'],
                    is_verified=pharmacy_data['is_verified'],
                    validated_at=datetime.utcnow(),
                )
                
                # Si c'est une pharmacie de garde, définir les dates
                if pharmacy.is_garde:
                    pharmacy.garde_start_date = datetime.utcnow()
                    pharmacy.garde_end_date = datetime.utcnow() + timedelta(days=7)
                
                db.session.add(pharmacy)
                print(f"  ✅ {pharmacy_data['code']} - {pharmacy_data['nom']}: Chargée")
                added += 1
                
            except Exception as e:
                print(f"  ❌ {pharmacy_data['code']} - Erreur: {str(e)[:50]}")
                errors += 1
                continue
        
        # Enregistrer les modifications
        try:
            db.session.commit()
            print("\n" + "=" * 90)
            print("RÉSULTATS")
            print("=" * 90)
            print(f"✅ Pharmacies ajoutées: {added}")
            print(f"⏭️  Pharmacies existantes (skipped): {skipped}")
            print(f"❌ Erreurs: {errors}")
            
            total = Pharmacy.query.count()
            print(f"\nTotal de pharmacies en base: {total}")
            
            print("\n" + "=" * 90)
            return True
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors de l'enregistrement: {e}")
            return False


if __name__ == '__main__':
    try:
        success = load_pharmacies_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
