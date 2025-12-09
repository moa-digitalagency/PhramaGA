from extensions import db


class Pharmacy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    quartier = db.Column(db.String(200))
    telephone = db.Column(db.String(100))
    bp = db.Column(db.String(50))
    horaires = db.Column(db.String(200))
    services = db.Column(db.Text)
    proprietaire = db.Column(db.String(200))
    type_etablissement = db.Column(db.String(100))
    is_garde = db.Column(db.Boolean, default=False)
    is_gare = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_validated = db.Column(db.Boolean, default=False)
    validated_at = db.Column(db.DateTime)
    validated_by_admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'nom': self.nom,
            'ville': self.ville,
            'quartier': self.quartier or '',
            'telephone': self.telephone or '',
            'bp': self.bp or '',
            'horaires': self.horaires or '',
            'services': self.services or '',
            'proprietaire': self.proprietaire or '',
            'type_etablissement': self.type_etablissement or '',
            'is_garde': self.is_garde,
            'is_gare': self.is_gare,
            'lat': self.latitude,
            'lng': self.longitude,
            'location_validated': self.location_validated
        }
