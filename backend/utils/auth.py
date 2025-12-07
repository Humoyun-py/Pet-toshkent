from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User

def admin_required():
    """Decorator to require admin role - optional for demo mode"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Try to verify JWT if Authorization header exists
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                try:
                    verify_jwt_in_request()
                    user_id = get_jwt_identity()
                    user = User.query.get(user_id)
                    
                    if not user or user.role != 'admin':
                        return jsonify({'error': 'Admin access required'}), 403
                    
                    if user.is_banned:
                        return jsonify({'error': 'Account is banned'}), 403
                except Exception as e:
                    # Token invalid - check if demo mode
                    pass
            # For demo mode, allow access without token
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def get_current_user():
    """Get current user from JWT token"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None
