from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .pet import Pet
from .clinic import Clinic
from .donation import Donation

__all__ = ['db', 'User', 'Pet', 'Clinic', 'Donation']
