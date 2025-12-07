from .start import router as start_router
from .pets import router as pets_router
from .clinics import router as clinics_router
from .donation import router as donation_router
from .admin import router as admin_router

__all__ = ['start_router', 'pets_router', 'clinics_router', 'donation_router', 'admin_router']
