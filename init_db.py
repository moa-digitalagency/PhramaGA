#!/usr/bin/env python3
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

if __name__ == '__main__':
    init_database()
