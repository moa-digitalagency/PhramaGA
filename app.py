"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

app.py - Application principale Flask
Ce fichier configure et initialise l'application Flask, incluant la base de données,
l'authentification, les routes et les gestionnaires d'erreurs.
"""

import os
import logging
from flask import Flask, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from extensions import db, login_manager, csrf
from routes import public_bp, admin_bp
from security.auth import init_login_manager, create_default_admin

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    session_secret = os.environ.get("SESSION_SECRET")
    if not session_secret:
        raise RuntimeError("SESSION_SECRET environment variable is required")

    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required")

    app.secret_key = session_secret
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    is_production = os.environ.get('FLASK_ENV', 'production') == 'production'
    use_https = os.environ.get('USE_HTTPS', 'true').lower() == 'true'
    
    app.config['SESSION_COOKIE_SECURE'] = use_https
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    app.config['WTF_CSRF_TIME_LIMIT'] = 3600

    db.init_app(app)
    csrf.init_app(app)
    init_login_manager(app)

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    register_error_handlers(app)

    with app.app_context():
        db.create_all()
        create_default_admin()

    return app


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        if hasattr(error, 'description'):
            message = error.description
        else:
            message = 'Requête invalide'
        return jsonify({'success': False, 'error': message}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Ressource non trouvée'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error(f"Internal error: {error}")
        return jsonify({'success': False, 'error': 'Erreur interne du serveur'}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback()
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        return jsonify({'success': False, 'error': 'Une erreur inattendue est survenue'}), 500


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
