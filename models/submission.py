from extensions import db
from datetime import datetime


class LocationSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    submitted_by_name = db.Column(db.String(100))
    submitted_by_phone = db.Column(db.String(50))
    comment = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by_admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    
    pharmacy = db.relationship('Pharmacy', backref='location_submissions')
    reviewed_by = db.relationship('Admin', foreign_keys=[reviewed_by_admin_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'pharmacy_id': self.pharmacy_id,
            'pharmacy_name': self.pharmacy.nom if self.pharmacy else '',
            'latitude': self.latitude,
            'longitude': self.longitude,
            'submitted_by_name': self.submitted_by_name or 'Anonyme',
            'submitted_by_phone': self.submitted_by_phone or '',
            'comment': self.comment or '',
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class InfoSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    current_value = db.Column(db.Text)
    proposed_value = db.Column(db.Text, nullable=False)
    submitted_by_name = db.Column(db.String(100))
    submitted_by_phone = db.Column(db.String(50))
    comment = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by_admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    
    pharmacy = db.relationship('Pharmacy', backref='info_submissions')
    reviewed_by = db.relationship('Admin', foreign_keys=[reviewed_by_admin_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'pharmacy_id': self.pharmacy_id,
            'pharmacy_name': self.pharmacy.nom if self.pharmacy else '',
            'field_name': self.field_name,
            'current_value': self.current_value or '',
            'proposed_value': self.proposed_value,
            'submitted_by_name': self.submitted_by_name or 'Anonyme',
            'submitted_by_phone': self.submitted_by_phone or '',
            'comment': self.comment or '',
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PharmacyView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pharmacy = db.relationship('Pharmacy', backref='views')
