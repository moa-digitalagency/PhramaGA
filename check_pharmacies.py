#!/usr/bin/env python
"""
Script de diagnostic des pharmacies corrompues
Identifie les problèmes dans les données des pharmacies de Libreville
"""
import os
import sys
from app import app, db
from models.pharmacy import Pharmacy
from datetime import datetime

def check_pharmacies():
    """Vérifie les pharmacies et identifie les problèmes"""
    with app.app_context():
        print("=" * 60)
        print("DIAGNOSTIC DES PHARMACIES DE LIBREVILLE")
        print("=" * 60)
        
        # Récupérer toutes les pharmacies de Libreville
        pharmacies = Pharmacy.query.filter_by(ville='Libreville').all()
        print(f"\nNombre total de pharmacies à Libreville: {len(pharmacies)}\n")
        
        errors = []
        warnings = []
        
        for pharmacy in pharmacies:
            print(f"\n[ID: {pharmacy.id}] {pharmacy.nom} ({pharmacy.code})")
            print(f"  Ville: {pharmacy.ville}")
            print(f"  Quartier: {pharmacy.quartier}")
            print(f"  Téléphone: {pharmacy.telephone}")
            
            # Vérifications
            issues = []
            
            # Vérifier les champs obligatoires
            if not pharmacy.code:
                issues.append("❌ CODE MANQUANT")
                errors.append(f"Pharmacie {pharmacy.id}: Code manquant")
            
            if not pharmacy.nom:
                issues.append("❌ NOM MANQUANT")
                errors.append(f"Pharmacie {pharmacy.id}: Nom manquant")
            
            if not pharmacy.ville:
                issues.append("❌ VILLE MANQUANTE")
                errors.append(f"Pharmacie {pharmacy.id}: Ville manquante")
            
            # Vérifier les coordonnées GPS
            if pharmacy.latitude is None or pharmacy.longitude is None:
                issues.append("⚠️  GPS INCOMPLET")
                warnings.append(f"Pharmacie {pharmacy.id}: Coordonnées GPS manquantes")
            else:
                # Valider la plage des coordonnées
                if not (-90 <= pharmacy.latitude <= 90):
                    issues.append(f"❌ LATITUDE INVALIDE: {pharmacy.latitude}")
                    errors.append(f"Pharmacie {pharmacy.id}: Latitude invalide {pharmacy.latitude}")
                if not (-180 <= pharmacy.longitude <= 180):
                    issues.append(f"❌ LONGITUDE INVALIDE: {pharmacy.longitude}")
                    errors.append(f"Pharmacie {pharmacy.id}: Longitude invalide {pharmacy.longitude}")
            
            # Vérifier les dates de garde
            if pharmacy.is_garde and pharmacy.garde_end_date:
                if pharmacy.garde_start_date and pharmacy.garde_start_date > pharmacy.garde_end_date:
                    issues.append("❌ DATES DE GARDE INVALIDES")
                    errors.append(f"Pharmacie {pharmacy.id}: Date début > date fin")
            
            # Vérifier les champs texte non valides
            if pharmacy.type_etablissement not in ['pharmacie_generale', 'depot_pharmaceutique', 'pharmacie_hospitaliere', None]:
                issues.append(f"❌ TYPE ÉTABLISSEMENT INVALIDE: {pharmacy.type_etablissement}")
                errors.append(f"Pharmacie {pharmacy.id}: Type établissement invalide")
            
            if issues:
                for issue in issues:
                    print(f"  {issue}")
            else:
                print(f"  ✅ Pas de problème détecté")
        
        # Résumé
        print("\n" + "=" * 60)
        print("RÉSUMÉ DU DIAGNOSTIC")
        print("=" * 60)
        print(f"\n⚠️  Avertissements: {len(warnings)}")
        for warning in warnings:
            print(f"   - {warning}")
        
        print(f"\n❌ Erreurs: {len(errors)}")
        for error in errors:
            print(f"   - {error}")
        
        if errors:
            print("\n" + "=" * 60)
            print("SCRIPT SQL DE CORRECTION")
            print("=" * 60)
            print("\nExécutez les commandes SQL suivantes pour corriger:")
            print("\n-- Supprimer les pharmacies avec code manquant")
            print("DELETE FROM pharmacy WHERE (code IS NULL OR code = '') AND ville = 'Libreville';")
            print("\n-- Supprimer les pharmacies avec nom manquant")
            print("DELETE FROM pharmacy WHERE (nom IS NULL OR nom = '') AND ville = 'Libreville';")
            print("\n-- Supprimer les pharmacies avec données corrompues")
            print("DELETE FROM pharmacy WHERE ville = 'Libreville' AND (")
            print("  (latitude < -90 OR latitude > 90) OR")
            print("  (longitude < -180 OR longitude > 180)")
            print(");")
            
            print("\n-- Ou corriger les coordonnées invalides à des valeurs par défaut (Libreville)")
            print("UPDATE pharmacy SET latitude = 0.4162, longitude = 9.4673")
            print("WHERE ville = 'Libreville' AND (latitude IS NULL OR longitude IS NULL");
            print("  OR latitude < -90 OR latitude > 90 OR longitude < -180 OR longitude > 180);")
        
        print("\n" + "=" * 60)
        if not errors and not warnings:
            print("✅ TOUTES LES PHARMACIES SONT OK!")
        print("=" * 60 + "\n")
        
        return len(errors) == 0

if __name__ == '__main__':
    try:
        success = check_pharmacies()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
