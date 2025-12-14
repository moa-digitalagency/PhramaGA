#!/usr/bin/env python3
"""
UrgenceGabon.com - Script pour réinitialiser le mot de passe admin
Exécutez: python reset_admin_password.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv

env_file = Path('.env')
if env_file.exists():
    load_dotenv(env_file)

from app import app
from extensions import db
from models.admin import Admin


def reset_admin_password():
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')
    
    if not username or not password:
        print("Erreur: ADMIN_USERNAME et ADMIN_PASSWORD requis dans .env")
        return False
    
    with app.app_context():
        admin = Admin.query.filter_by(username=username).first()
        
        if not admin:
            admin = Admin(username=username)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin '{username}' créé avec succès!")
        else:
            admin.set_password(password)
            db.session.commit()
            print(f"Mot de passe de '{username}' mis à jour!")
        
        print("=" * 50)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("=" * 50)
        
        test = admin.check_password(password)
        print(f"Test de vérification: {'OK' if test else 'ECHEC'}")
        
        return True


if __name__ == '__main__':
    reset_admin_password()
