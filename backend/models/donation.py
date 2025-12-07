from . import db
from datetime import datetime

class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='UZS')
    payment_method = db.Column(db.String(50))  # click, payme, cash
    payment_id = db.Column(db.String(100))  # External payment reference
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    donor_name = db.Column(db.String(100))
    donor_phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'donor_name': 'Anonim' if self.is_anonymous else self.donor_name,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
