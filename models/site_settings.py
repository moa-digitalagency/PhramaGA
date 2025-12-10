from extensions import db
from datetime import datetime


class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get(key, default=None):
        setting = SiteSettings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set(key, value):
        setting = SiteSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = SiteSettings(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
        return setting
    
    @staticmethod
    def get_all():
        settings = SiteSettings.query.all()
        return {s.key: s.value for s in settings}


class PopupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    warning_text = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    show_once = db.Column(db.Boolean, default=True)
    ordering = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description or '',
            'warning_text': self.warning_text or '',
            'image_url': self.image_url or '',
            'is_active': self.is_active,
            'show_once': self.show_once,
            'ordering': self.ordering
        }
