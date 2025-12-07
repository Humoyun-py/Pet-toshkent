from . import db
from datetime import datetime

class Pet(db.Model):
    __tablename__ = 'pets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    pet_type = db.Column(db.String(50), nullable=False)  # dog, cat, bird, etc.
    breed = db.Column(db.String(100))
    age = db.Column(db.String(50))  # "2 yil", "6 oy", etc.
    gender = db.Column(db.String(20))  # male, female
    status = db.Column(db.String(50), nullable=False)  # selling, free, foster, adoption
    price = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    location = db.Column(db.String(200))
    approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'name': self.name,
            'pet_type': self.pet_type,
            'breed': self.breed,
            'age': self.age,
            'gender': self.gender,
            'status': self.status,
            'price': self.price,
            'description': self.description,
            'image': self.image,
            'location': self.location,
            'approved': self.approved,
            'is_active': self.is_active,
            'views': self.views,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
