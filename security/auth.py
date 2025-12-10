import os
from extensions import login_manager, db
from models.admin import Admin


def init_login_manager(app):
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


def create_default_admin():
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    if not admin_username or not admin_password:
        return
    
    try:
        existing_admin = Admin.query.filter_by(username=admin_username).first()
        if existing_admin:
            existing_admin.set_password(admin_password)
            db.session.commit()
            return
        
        any_admin = Admin.query.first()
        if any_admin:
            any_admin.username = admin_username
            any_admin.set_password(admin_password)
            db.session.commit()
            return
        
        admin = Admin(username=admin_username)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
    except Exception:
        db.session.rollback()
