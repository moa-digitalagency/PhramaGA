#!/usr/bin/env python3
"""
UrgenceGabon.com - Diagnostic complet de l'application
Analyze errors and database status systematically
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Try to import key modules
def check_imports():
    """Check if all required modules can be imported"""
    print("\n" + "="*90)
    print("VÉRIFICATION DES IMPORTATIONS DE MODULES")
    print("="*90)
    
    modules = [
        'flask',
        'flask_login',
        'flask_sqlalchemy',
        'flask_limiter',
        'sqlalchemy',
        'psycopg2',
        'werkzeug',
        'dotenv',
    ]
    
    results = {}
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}: OK")
            results[module] = True
        except ImportError as e:
            print(f"❌ {module}: MANQUANT ({str(e)[:50]})")
            results[module] = False
    
    return all(results.values())


def check_environment_variables():
    """Check required environment variables"""
    print("\n" + "="*90)
    print("VÉRIFICATION DES VARIABLES D'ENVIRONNEMENT")
    print("="*90)
    
    required = ['DATABASE_URL', 'SESSION_SECRET']
    optional = ['FLASK_ENV', 'ADMIN_USERNAME', 'ADMIN_PASSWORD']
    
    results = {}
    
    print("\n📋 Variables requises:")
    for var in required:
        value = os.environ.get(var)
        if value:
            masked = value[:10] + '...' if len(value) > 10 else value
            print(f"✅ {var}: Défini ({masked})")
            results[var] = True
        else:
            print(f"❌ {var}: MANQUANT")
            results[var] = False
    
    print("\n📋 Variables optionnelles:")
    for var in optional:
        value = os.environ.get(var)
        if value:
            masked = value[:10] + '...' if len(value) > 10 else value
            print(f"✅ {var}: Défini ({masked})")
        else:
            print(f"⚠️  {var}: Non défini")
    
    return all(results.values())


def check_database_connection():
    """Test database connection"""
    print("\n" + "="*90)
    print("VÉRIFICATION DE LA CONNEXION À LA BASE DE DONNÉES")
    print("="*90)
    
    try:
        from sqlalchemy import create_engine, text
        
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL non défini")
            return False
        
        print(f"📍 Tentative de connexion à: {db_url.split('@')[0]}***")
        engine = create_engine(db_url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connexion OK")
            print(f"✅ PostgreSQL: {version.split(',')[0]}")
            return True
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)[:100]}")
        return False


def check_database_tables():
    """Check if all required tables exist"""
    print("\n" + "="*90)
    print("VÉRIFICATION DES TABLES DE LA BASE DE DONNÉES")
    print("="*90)
    
    try:
        from app import app
        from extensions import db
        from sqlalchemy import inspect
        
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                'pharmacy', 'admin', 'location_submission', 'info_submission',
                'pharmacy_view', 'suggestion', 'pharmacy_proposal', 'page_interaction',
                'user_action', 'emergency_contact', 'site_settings', 'popup_message',
                'advertisement', 'ad_settings', 'activity_log'
            ]
            
            print(f"\n📊 Tables existantes: {len(tables)}")
            
            missing = []
            for table in required_tables:
                if table in tables:
                    print(f"✅ {table}")
                else:
                    print(f"❌ {table}: MANQUANTE")
                    missing.append(table)
            
            if missing:
                print(f"\n⚠️  {len(missing)} table(s) manquante(s)")
                print("   Exécutez: python init_db.py")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)[:100]}")
        return False


def check_database_data():
    """Check data in key tables"""
    print("\n" + "="*90)
    print("VÉRIFICATION DES DONNÉES DANS LES TABLES")
    print("="*90)
    
    try:
        from app import app
        from extensions import db
        from sqlalchemy import text
        
        with app.app_context():
            tables_to_check = {
                'admin': 'Administrateurs',
                'pharmacy': 'Pharmacies',
                'site_settings': 'Paramètres du site',
                'activity_log': 'Journaux d\'activité'
            }
            
            for table, label in tables_to_check.items():
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar() or 0
                    if count > 0:
                        print(f"✅ {label}: {count} entrée(s)")
                    else:
                        print(f"⚠️  {label}: Vide")
                except Exception as e:
                    print(f"⚠️  {label}: Erreur ({str(e)[:30]})")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)[:100]}")
        return False


def check_admin_account():
    """Check if admin account exists"""
    print("\n" + "="*90)
    print("VÉRIFICATION DU COMPTE ADMINISTRATEUR")
    print("="*90)
    
    try:
        from app import app
        from models.admin import Admin
        
        with app.app_context():
            admins = Admin.query.all()
            
            if not admins:
                print("❌ Aucun administrateur trouvé")
                print("   Exécutez: python init_db.py")
                return False
            
            print(f"✅ {len(admins)} administrateur(s) trouvé(s)")
            for admin in admins:
                print(f"   - {admin.username} (ID: {admin.id})")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)[:100]}")
        return False


def check_file_permissions():
    """Check file and directory permissions"""
    print("\n" + "="*90)
    print("VÉRIFICATION DES PERMISSIONS DES FICHIERS")
    print("="*90)
    
    paths_to_check = {
        'templates': 'Dossier des templates',
        'static': 'Dossier des fichiers statiques',
        'static/uploads': 'Dossier des uploads',
    }
    
    all_ok = True
    for path, label in paths_to_check.items():
        if os.path.exists(path):
            if os.access(path, os.R_OK):
                print(f"✅ {label}: Lisible")
            else:
                print(f"❌ {label}: Non lisible (permission refusée)")
                all_ok = False
            
            if os.path.isdir(path) and os.access(path, os.W_OK):
                print(f"✅ {label}: Inscriptible")
            elif os.path.isdir(path):
                print(f"⚠️  {label}: Non inscriptible")
        else:
            print(f"⚠️  {label}: N'existe pas")
    
    return all_ok


def check_app_routes():
    """Check if routes are properly registered"""
    print("\n" + "="*90)
    print("VÉRIFICATION DES ROUTES")
    print("="*90)
    
    try:
        from app import app
        
        routes = {}
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                endpoint = rule.endpoint
                if endpoint not in routes:
                    routes[endpoint] = []
                routes[endpoint].append(f"{rule.rule} ({','.join(rule.methods - {'HEAD', 'OPTIONS'})})")
        
        print(f"\n✅ Total de routes: {len(routes)}")
        
        critical_routes = ['admin.admin_dashboard', 'admin.auth_login', 'public.index']
        for route in critical_routes:
            if route in routes:
                print(f"✅ {route}: OK")
            else:
                print(f"❌ {route}: MANQUANT")
        
        return all(route in routes for route in critical_routes)
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)[:100]}")
        return False


def check_app_models():
    """Check if models can be imported"""
    print("\n" + "="*90)
    print("VÉRIFICATION DES MODÈLES DE DONNÉES")
    print("="*90)
    
    models_to_check = [
        ('models.pharmacy', 'Pharmacy'),
        ('models.admin', 'Admin'),
        ('models.submission', 'LocationSubmission'),
        ('models.emergency_contact', 'EmergencyContact'),
        ('models.site_settings', 'SiteSettings'),
        ('models.advertisement', 'Advertisement'),
        ('models.activity_log', 'ActivityLog'),
    ]
    
    all_ok = True
    for module_name, class_name in models_to_check:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {class_name}: OK")
        except Exception as e:
            print(f"❌ {class_name}: Erreur ({str(e)[:50]})")
            all_ok = False
    
    return all_ok


def generate_report():
    """Generate complete diagnostic report"""
    print("\n\n" + "="*90)
    print("DIAGNOSTIC COMPLET - RÉSUMÉ")
    print("="*90)
    
    checks = {
        'Importations de modules': check_imports(),
        'Variables d\'environnement': check_environment_variables(),
        'Connexion à la base de données': check_database_connection(),
        'Tables de la base de données': check_database_tables(),
        'Données dans les tables': check_database_data(),
        'Compte administrateur': check_admin_account(),
        'Permissions des fichiers': check_file_permissions(),
        'Routes de l\'application': check_app_routes(),
        'Modèles de données': check_app_models(),
    }
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    print(f"\nRésultats: {passed}/{total} vérifications réussies")
    print("\nDétails:")
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check_name}")
    
    if passed == total:
        print("\n🎉 Application diagnostiquée avec succès!")
        print("   L'application devrait fonctionner correctement.")
    else:
        print(f"\n⚠️  {total - passed} problème(s) détecté(s)")
        print("\nActions recommandées:")
        print("   1. Vérifier les variables d'environnement")
        print("   2. Vérifier la connexion à PostgreSQL")
        print("   3. Exécuter: python init_db.py")
        print("   4. Vérifier les logs de l'application")
        print("   5. Redémarrer l'application")
    
    return passed == total


if __name__ == '__main__':
    try:
        print("\n🔍 Diagnostic de UrgenceGabon.com")
        print(f"   Démarrage: {datetime.utcnow().isoformat()}")
        
        success = generate_report()
        
        print("\n" + "="*90)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
