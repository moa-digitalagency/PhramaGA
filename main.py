"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

main.py - Point d'entrée de l'application
Ce fichier charge les variables d'environnement et importe l'application Flask
pour le démarrage du serveur.
"""

from dotenv import load_dotenv
load_dotenv()

from app import app  # noqa: F401
