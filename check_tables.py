#!/usr/bin/env python3
"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

check_tables.py - Vérification et création des tables manquantes
Ce fichier vérifie que toutes les tables existent dans la base de données
et les crée si elles manquent.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

env_file = Path('.env')
if env_file.exists():
    load_dotenv(env_file)

from app import app
from extensions import db
from sqlalchemy import inspect


def get_existing_tables():
    """Get list of existing tables in the database."""
    inspector = inspect(db.engine)
    return set(inspector.get_table_names())


def get_required_tables():
    """Get list of required models."""
    return {
        'pharmacy': 'Pharmacy',
        'admin': 'Admin',
        'location_submission': 'LocationSubmission',
        'info_submission': 'InfoSubmission',
        'pharmacy_view': 'PharmacyView',
        'suggestion': 'Suggestion',
        'pharmacy_proposal': 'PharmacyProposal',
        'emergency_contact': 'EmergencyContact',
        'site_settings': 'SiteSettings',
        'popup_message': 'PopupMessage',
        'advertisement': 'Advertisement',
        'ad_settings': 'AdSettings',
        'activity_log': 'ActivityLog',
        'page_interaction': 'PageInteraction',
        'user_action': 'UserAction'
    }


def check_and_create_tables():
    """Check for missing tables and create them."""
    with app.app_context():
        # Import all models to register them with SQLAlchemy
        from models.pharmacy import Pharmacy
        from models.admin import Admin
        from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion, PharmacyProposal, PageInteraction, UserAction
        from models.emergency_contact import EmergencyContact
        from models.site_settings import SiteSettings, PopupMessage
        from models.advertisement import Advertisement, AdSettings
        from models.activity_log import ActivityLog
        
        existing_tables = get_existing_tables()
        required_tables = get_required_tables()
        
        missing_tables = set(required_tables.keys()) - existing_tables
        
        if not missing_tables:
            print("✅ All required tables exist!")
            return True
        
        print(f"⚠️ Found {len(missing_tables)} missing table(s):")
        for table in missing_tables:
            print(f"  - {table}")
        
        print("\n📝 Creating missing tables...")
        db.create_all()
        
        # Verify creation
        new_existing_tables = get_existing_tables()
        created_tables = missing_tables & new_existing_tables
        
        if created_tables == missing_tables:
            print(f"✅ Successfully created {len(created_tables)} table(s):")
            for table in created_tables:
                print(f"  - {table}")
            return True
        else:
            failed = missing_tables - new_existing_tables
            print(f"❌ Failed to create {len(failed)} table(s):")
            for table in failed:
                print(f"  - {table}")
            return False


if __name__ == '__main__':
    success = check_and_create_tables()
    exit(0 if success else 1)
