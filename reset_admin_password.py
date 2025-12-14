#!/usr/bin/env python3
"""
Script pour réinitialiser le mot de passe admin
Exécutez: python reset_admin_password.py
"""

from app import app
from extensions import db
from models.admin import Admin

def reset_admin_password():
    with app.app_context():
        admin = Admin.query.filter_by(username='myoneart').first()
        
        if not admin:
            print("Erreur: Admin 'myoneart' non trouvé!")
            return False
        
        admin.set_password('my0n34rt')
        db.session.commit()
        
        print("=" * 50)
        print("Mot de passe réinitialisé avec succès!")
        print("=" * 50)
        print(f"Username: myoneart")
        print(f"Password: my0n34rt")
        print("=" * 50)
        
        test = admin.check_password('my0n34rt')
        print(f"Test de vérification: {'OK' if test else 'ECHEC'}")
        
        return True

if __name__ == '__main__':
    reset_admin_password()
