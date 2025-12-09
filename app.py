import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from extensions import db, login_manager
from routes import public_bp, admin_bp
from security.auth import init_login_manager, create_default_admin
from services.pharmacy_service import PharmacyService


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    db.init_app(app)
    init_login_manager(app)
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    
    with app.app_context():
        db.create_all()
        create_default_admin()
        
        from models.pharmacy import Pharmacy
        if Pharmacy.query.count() == 0:
            PharmacyService.import_csv_data()
    
    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
