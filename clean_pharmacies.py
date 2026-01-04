#!/usr/bin/env python3
"""
UrgenceGabon.com - Nettoyage des données pharmacies
Ce script supprime toutes les pharmacies de la base de données.
À utiliser avec précaution sur le VPS de production.

Usage: python clean_pharmacies.py
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def clean_pharmacies():
    """Supprime toutes les pharmacies de la base de données"""
    try:
        from app import app
        from extensions import db
        from models.pharmacy import Pharmacy
        
        with app.app_context():
            count = Pharmacy.query.count()
            
            if count == 0:
                logger.info("Aucune pharmacie à supprimer.")
                return True
            
            logger.info(f"Suppression de {count} pharmacie(s)...")
            
            Pharmacy.query.delete()
            db.session.commit()
            
            logger.info(f"{count} pharmacie(s) supprimée(s) avec succès.")
            return True
            
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        db.session.rollback()
        return False


def main():
    print("\n" + "="*60)
    print("NETTOYAGE DES PHARMACIES - UrgenceGabon.com")
    print("="*60)
    
    confirm = input("\nATTENTION: Cette action va supprimer TOUTES les pharmacies.\nTapez 'OUI' pour confirmer: ")
    
    if confirm.strip().upper() != 'OUI':
        print("Opération annulée.")
        sys.exit(0)
    
    success = clean_pharmacies()
    
    print("\n" + "="*60)
    if success:
        print("Nettoyage terminé avec succès.")
    else:
        print("Erreur lors du nettoyage.")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
