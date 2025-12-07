from .auth_routes import auth_bp
from .pet_routes import pet_bp
from .clinic_routes import clinic_bp
from .donation_routes import donation_bp

__all__ = ['auth_bp', 'pet_bp', 'clinic_bp', 'donation_bp']
