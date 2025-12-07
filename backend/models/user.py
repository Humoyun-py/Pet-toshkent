from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')  # user, admin
    is_banned = db.Column(db.Boolean, default=False)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pets = db.relationship('Pet', backref='owner', lazy=True)
    donations = db.relationship('Donation', backref='donor', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_banned': self.is_banned,
            'telegram_id': self.telegram_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
