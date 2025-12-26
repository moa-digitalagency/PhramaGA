#!/usr/bin/env python
"""
Script de correction des pharmacies corrompues
Corrige automatiquement les problèmes identifiés
"""
import os
import sys
from app import app, db
from models.pharmacy import Pharmacy

def fix_pharmacies():
    """Corrige les pharmacies corrompues"""
    with app.app_context():
        print("=" * 60)
        print("CORRECTION DES PHARMACIES DE LIBREVILLE")
        print("=" * 60)
        
        fixed = 0
        deleted = 0
        
        # Récupérer toutes les pharmacies de Libreville
        pharmacies = Pharmacy.query.filter_by(ville='Libreville').all()
        print(f"\nTraitement de {len(pharmacies)} pharmacies...\n")
        
        for pharmacy in pharmacies:
            modified = False
            
            # 1. Supprimer si code manquant
            if not pharmacy.code or pharmacy.code.strip() == '':
                print(f"[SUPPRESSION] Pharmacie {pharmacy.id} ({pharmacy.nom}): Code manquant")
                db.session.delete(pharmacy)
                deleted += 1
                continue
            
            # 2. Supprimer si nom manquant
            if not pharmacy.nom or pharmacy.nom.strip() == '':
                print(f"[SUPPRESSION] Pharmacie {pharmacy.id} ({pharmacy.code}): Nom manquant")
                db.session.delete(pharmacy)
                deleted += 1
                continue
            
            # 3. Corriger les coordonnées GPS invalides
            if pharmacy.latitude is None or pharmacy.longitude is None:
                print(f"[CORRECTION] Pharmacie {pharmacy.id} ({pharmacy.nom}): GPS manquant -> valeur par défaut (Libreville)")
                pharmacy.latitude = 0.4162
                pharmacy.longitude = 9.4673
                modified = True
            else:
                if not (-90 <= pharmacy.latitude <= 90) or not (-180 <= pharmacy.longitude <= 180):
                    print(f"[CORRECTION] Pharmacie {pharmacy.id} ({pharmacy.nom}): GPS invalide -> valeur par défaut (Libreville)")
                    pharmacy.latitude = 0.4162
                    pharmacy.longitude = 9.4673
                    modified = True
            
            # 4. Corriger le type établissement invalide
            valid_types = ['pharmacie_generale', 'depot_pharmaceutique', 'pharmacie_hospitaliere']
            if pharmacy.type_etablissement and pharmacy.type_etablissement not in valid_types:
                print(f"[CORRECTION] Pharmacie {pharmacy.id} ({pharmacy.nom}): Type établissement invalide -> pharmacie_generale")
                pharmacy.type_etablissement = 'pharmacie_generale'
                modified = True
            
            # 5. Vérifier les dates de garde
            if pharmacy.is_garde and pharmacy.garde_start_date and pharmacy.garde_end_date:
                if pharmacy.garde_start_date > pharmacy.garde_end_date:
                    print(f"[CORRECTION] Pharmacie {pharmacy.id} ({pharmacy.nom}): Dates de garde invalides -> désactivé")
                    pharmacy.is_garde = False
                    pharmacy.garde_start_date = None
                    pharmacy.garde_end_date = None
                    modified = True
            
            if modified:
                fixed += 1
        
        # Enregistrer les modifications
        if fixed > 0 or deleted > 0:
            try:
                db.session.commit()
                print("\n" + "=" * 60)
                print("RÉSULTATS")
                print("=" * 60)
                print(f"✅ Pharmacies corrigées: {fixed}")
                print(f"❌ Pharmacies supprimées: {deleted}")
                print("\n✅ Corrections enregistrées avec succès!")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Erreur lors de l'enregistrement: {e}")
                return False
        else:
            print("\n✅ Aucune correction nécessaire!")
            return True

if __name__ == '__main__':
    try:
        success = fix_pharmacies()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
