#!/usr/bin/env python3
"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

init_db.py - Initialisation et migration de la base de données
Ce fichier crée les tables, vérifie l'intégrité et initialise les paramètres par défaut.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import inspect, text

env_file = Path('.env')
if env_file.exists():
    load_dotenv(env_file)

from app import app
from extensions import db


def get_required_models():
    """Retourne tous les modèles requis."""
    with app.app_context():
        from models.pharmacy import Pharmacy
        from models.admin import Admin
        from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion, PharmacyProposal, PageInteraction, UserAction
        from models.emergency_contact import EmergencyContact
        from models.site_settings import SiteSettings, PopupMessage
        from models.advertisement import Advertisement, AdSettings
        from models.activity_log import ActivityLog
        
        return {
            'pharmacy': Pharmacy,
            'admin': Admin,
            'location_submission': LocationSubmission,
            'info_submission': InfoSubmission,
            'pharmacy_view': PharmacyView,
            'suggestion': Suggestion,
            'pharmacy_proposal': PharmacyProposal,
            'page_interaction': PageInteraction,
            'user_action': UserAction,
            'emergency_contact': EmergencyContact,
            'site_settings': SiteSettings,
            'popup_message': PopupMessage,
            'advertisement': Advertisement,
            'ad_settings': AdSettings,
            'activity_log': ActivityLog,
        }


def get_existing_tables():
    """Retourne l'ensemble des tables existantes dans la base de données."""
    inspector = inspect(db.engine)
    return set(inspector.get_table_names())


def check_and_create_missing_tables():
    """Vérifie et crée les tables manquantes."""
    with app.app_context():
        models = get_required_models()
        existing_tables = get_existing_tables()
        required_table_names = set(models.keys())
        
        missing_tables = required_table_names - existing_tables
        
        if not missing_tables:
            print("✅ Toutes les tables requises existent!")
            return True
        
        print(f"⚠️  {len(missing_tables)} table(s) manquante(s):")
        for table in sorted(missing_tables):
            print(f"  - {table}")
        
        print("\n📝 Création des tables manquantes...")
        for table_name in sorted(missing_tables):
            try:
                models[table_name].__table__.create(db.engine, checkfirst=True)
                print(f"  ✓ Créée: {table_name}")
            except Exception as e:
                print(f"  ✗ Erreur pour {table_name}: {e}")
                return False
        
        return True


def check_and_add_missing_columns():
    """Vérifie et ajoute les colonnes manquantes aux tables existantes."""
    with app.app_context():
        models = get_required_models()
        existing_tables = get_existing_tables()
        inspector = inspect(db.engine)
        
        schema_issues = []
        
        for table_name, model_class in models.items():
            if table_name not in existing_tables:
                continue
            
            db_columns = {col['name'] for col in inspector.get_columns(table_name)}
            model_columns = {col.name for col in model_class.__table__.columns}
            
            missing_cols = model_columns - db_columns
            if missing_cols:
                schema_issues.append((table_name, missing_cols))
                print(f"  ⚠️  {table_name}: colonnes manquantes {missing_cols}")
            else:
                print(f"  ✓ {table_name}: schéma OK")
        
        if not schema_issues:
            print("✅ Tous les schémas sont à jour!")
            return True
        
        print(f"\n🔧 Ajout des colonnes manquantes...")
        for table_name, missing_cols in schema_issues:
            model_class = models[table_name]
            for col_name in missing_cols:
                try:
                    col = model_class.__table__.columns[col_name]
                    col_type = str(col.type)
                    
                    # Construire la clause ALTER TABLE
                    if col.nullable:
                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                    else:
                        # Pour les colonnes non-nullables, utiliser une valeur par défaut
                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type} DEFAULT NULL"
                    
                    db.session.execute(text(alter_sql))
                    db.session.commit()
                    print(f"  ✓ Ajoutée colonne: {table_name}.{col_name}")
                except Exception as e:
                    db.session.rollback()
                    print(f"  ✗ Erreur pour {table_name}.{col_name}: {str(e)[:60]}")
                    # Continuer même en cas d'erreur
        
        return True


def init_database():
    """Initialise complètement la base de données."""
    print("\n" + "=" * 90)
    print("INITIALISATION ET VÉRIFICATION - BASE DE DONNÉES")
    print("=" * 90)
    
    with app.app_context():
        # Importer tous les modèles pour les enregistrer avec SQLAlchemy
        from models.pharmacy import Pharmacy
        from models.admin import Admin
        from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion, PharmacyProposal, PageInteraction, UserAction
        from models.emergency_contact import EmergencyContact
        from models.site_settings import SiteSettings, PopupMessage
        from models.advertisement import Advertisement, AdSettings
        from models.activity_log import ActivityLog
        
        print("\n📊 État actuel:")
        existing_tables = get_existing_tables()
        print(f"   Tables existantes: {len(existing_tables)}")
        
        # Créer toutes les tables
        print("\n🔨 Création des tables...")
        db.create_all()
        
        print("\n✅ Toutes les tables ont été créées/vérifiées!")
        print("   Tables:")
        for table_name in sorted(get_required_models().keys()):
            print(f"    - {table_name}")


def init_admin_from_env():
    """Initialise le compte administrateur à partir des variables d'environnement."""
    with app.app_context():
        from models.admin import Admin
        
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        
        if not username or not password:
            print("\n⚠️  ADMIN_USERNAME et ADMIN_PASSWORD non configurés.")
            print("   Ajoutez-les à votre fichier .env ou exportez-les en variable d'environnement.")
            return False
        
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            existing_admin.set_password(password)
            db.session.commit()
            print(f"\n✓ Admin '{username}' mot de passe mis à jour!")
        else:
            admin = Admin(username=username)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"\n✓ Admin '{username}' créé avec succès!")
        
        return True


def init_default_seo_settings():
    """Initialise les paramètres SEO par défaut s'ils ne sont pas présents."""
    with app.app_context():
        from models.site_settings import SiteSettings
        
        defaults = {
            'site_name': 'UrgenceGabon.com',
            'og_title': 'UrgenceGabon.com - Trouvez votre pharmacie au Gabon',
            'og_description': 'Annuaire complet des pharmacies au Gabon. Trouvez les pharmacies de garde, numéros d\'urgence et informations de contact.',
            'meta_description': 'Annuaire des pharmacies au Gabon. Pharmacies de garde 24h/24, numéros d\'urgence, carte interactive. Trouvez la pharmacie la plus proche.',
            'meta_keywords': 'pharmacie gabon, pharmacie garde libreville, urgence gabon, pharmacie 24h, samu gabon, pompiers gabon',
            'twitter_handle': '',
            'canonical_url': '',
            'google_site_verification': '',
            'robots_txt': 'User-agent: *\nAllow: /',
        }
        
        created_count = 0
        for key, value in defaults.items():
            existing = SiteSettings.query.filter_by(key=key).first()
            if not existing:
                SiteSettings.set(key, value)
                created_count += 1
        
        if created_count > 0:
            print(f"\n✓ {created_count} paramètre(s) SEO initialisé(s).")
        else:
            print("\n✓ Les paramètres SEO existaient déjà.")


if __name__ == '__main__':
    try:
        init_database()
        check_and_create_missing_tables()
        
        print("\n🔍 Vérification des colonnes...")
        check_and_add_missing_columns()
        
        init_admin_from_env()
        init_default_seo_settings()
        
        print("\n" + "=" * 90)
        print("✅ Migration terminée - La base de données est prête!")
        print("=" * 90)
        
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
