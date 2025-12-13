#!/usr/bin/env python3
"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

init_db.py - Initialisation de la base de données
Ce fichier crée les tables de la base de données et initialise le compte
administrateur à partir des variables d'environnement.
"""

import os
from app import app
from extensions import db

def init_database():
    with app.app_context():
        from models.pharmacy import Pharmacy
        from models.admin import Admin
        from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion
        
        db.create_all()
        print("Database tables created successfully!")
        print("Tables created:")
        print("  - pharmacy")
        print("  - admin")
        print("  - location_submission")
        print("  - info_submission")
        print("  - pharmacy_view")
        print("  - suggestion")

def init_admin_from_env():
    with app.app_context():
        from models.admin import Admin
        
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        
        if not username or not password:
            print("ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required.")
            return False
        
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            existing_admin.set_password(password)
            db.session.commit()
            print(f"Admin '{username}' password updated successfully!")
        else:
            admin = Admin(username=username)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin '{username}' created successfully!")
        
        return True

if __name__ == '__main__':
    init_database()
    init_admin_from_env()
