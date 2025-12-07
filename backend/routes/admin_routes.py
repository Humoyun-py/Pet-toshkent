from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Pet, Clinic, Donation
from utils import admin_required
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required()
def dashboard():
    """Get admin dashboard statistics"""
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    
    # User stats
    total_users = User.query.count()
    new_users_today = User.query.filter(func.date(User.created_at) == today).count()
    new_users_week = User.query.filter(func.date(User.created_at) >= week_ago).count()
    
    # Pet stats
    total_pets = Pet.query.count()
    active_pets = Pet.query.filter_by(is_active=True, approved=True).count()
    pending_pets = Pet.query.filter_by(approved=False, is_active=True).count()
    new_pets_today = Pet.query.filter(func.date(Pet.created_at) == today).count()
    
    # Clinic stats
    total_clinics = Clinic.query.filter_by(is_active=True).count()
    
    # Donation stats
    total_donations = db.session.query(func.sum(Donation.amount))\
        .filter_by(status='completed').scalar() or 0
    today_donations = db.session.query(func.sum(Donation.amount))\
        .filter(Donation.status == 'completed', func.date(Donation.created_at) == today).scalar() or 0
    
    # Recent activity
    recent_pets = Pet.query.order_by(Pet.created_at.desc()).limit(5).all()
    recent_donations = Donation.query.filter_by(status='completed')\
        .order_by(Donation.created_at.desc()).limit(5).all()
    
    # Charts data - daily pets and donations
    daily_pets = db.session.query(
        func.date(Pet.created_at).label('date'),
        func.count(Pet.id).label('count')
    ).filter(func.date(Pet.created_at) >= week_ago)\
    .group_by(func.date(Pet.created_at)).all()
    
    return jsonify({
        'stats': {
            'users': {
                'total': total_users,
                'today': new_users_today,
                'week': new_users_week
            },
            'pets': {
                'total': total_pets,
                'active': active_pets,
                'pending': pending_pets,
                'today': new_pets_today
            },
            'clinics': {
                'total': total_clinics
            },
            'donations': {
                'total': total_donations,
                'today': today_donations
            }
        },
        'recent': {
            'pets': [p.to_dict() for p in recent_pets],
            'donations': [d.to_dict() for d in recent_donations]
        },
        'charts': {
            'daily_pets': [{'date': str(d.date), 'count': d.count} for d in daily_pets]
        }
    })

# User management
@admin_bp.route('/users', methods=['GET'])
@admin_required()
def list_users():
    """Get all users"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    pagination = query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required()
def get_user(user_id):
    """Get single user details"""
    user = User.query.get_or_404(user_id)
    
    # Get user's pets and donations
    pets = Pet.query.filter_by(user_id=user_id).all()
    donations = Donation.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'user': user.to_dict(),
        'pets': [p.to_dict() for p in pets],
        'donations': [d.to_dict() for d in donations]
    })

@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@admin_required()
def ban_user(user_id):
    """Ban user"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        return jsonify({'error': 'Cannot ban admin'}), 400
    
    user.is_banned = True
    db.session.commit()
    
    return jsonify({'message': 'User banned', 'user': user.to_dict()})

@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@admin_required()
def unban_user(user_id):
    """Unban user"""
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    
    return jsonify({'message': 'User unbanned', 'user': user.to_dict()})

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required()
def change_role(user_id):
    """Change user role"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    new_role = data.get('role')
    if new_role not in ['user', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    user.role = new_role
    db.session.commit()
    
    return jsonify({'message': 'Role updated', 'user': user.to_dict()})

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        return jsonify({'error': 'Cannot delete admin'}), 400
    
    # Delete user's pets
    Pet.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted'})
