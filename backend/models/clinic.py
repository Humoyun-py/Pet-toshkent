from . import db
from datetime import datetime

class Clinic(db.Model):
    __tablename__ = 'clinics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(50))
    website = db.Column(db.String(200))
    working_hours = db.Column(db.String(100))
    services = db.Column(db.Text)  # JSON string of services
    rating = db.Column(db.Float, default=0)
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'lat': self.lat,
            'lng': self.lng,
            'phone': self.phone,
            'website': self.website,
            'working_hours': self.working_hours,
            'services': self.services,
            'rating': self.rating,
            'image': self.image,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_nearby(lat, lng, radius_km=5):
        """Get clinics within radius using Haversine formula approximation"""
        # Approximate degrees per km
        lat_range = radius_km / 111.0
        lng_range = radius_km / (111.0 * abs(cos(radians(lat))))
        
        return Clinic.query.filter(
            Clinic.lat.between(lat - lat_range, lat + lat_range),
            Clinic.lng.between(lng - lng_range, lng + lng_range),
            Clinic.is_active == True
        ).all()

from math import cos, radians
