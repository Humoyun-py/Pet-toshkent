from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    # Validate required fields
    required = ['full_name', 'email', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if email exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    user = User(
        full_name=data['full_name'],
        email=data['email'],
        phone=data.get('phone'),
        role='user'
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generate token
    token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if user.is_banned:
        return jsonify({'error': 'Account is banned'}), 403
    
    token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Get current user info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()})

@auth_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if data.get('full_name'):
        user.full_name = data['full_name']
    if data.get('phone'):
        user.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated',
        'user': user.to_dict()
    })

@auth_bp.route('/telegram', methods=['POST'])
def telegram_login():
    """Login or register via Telegram"""
    data = request.get_json()
    
    telegram_id = data.get('telegram_id')
    full_name = data.get('full_name', 'Telegram User')
    username = data.get('username', '')
    
    if not telegram_id:
        return jsonify({'error': 'telegram_id is required'}), 400
    
    # Find or create user
    user = User.query.filter_by(telegram_id=telegram_id).first()
    
    if not user:
        # Create new user with Telegram
        email = f"tg_{telegram_id}@pettashkent.uz"
        user = User(
            full_name=full_name,
            email=email,
            telegram_id=telegram_id,
            phone=username if username else None,
            role='user'
        )
        user.set_password(str(telegram_id))  # Default password
        
        db.session.add(user)
        db.session.commit()
    
    if user.is_banned:
        return jsonify({'error': 'Account is banned'}), 403
    
    token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Telegram login successful',
        'token': token,
        'user': user.to_dict()
    })

@auth_bp.route('/telegram/check/<int:telegram_id>', methods=['GET'])
def check_telegram_user(telegram_id):
    """Check if Telegram user exists"""
    user = User.query.filter_by(telegram_id=telegram_id).first()
    
    if user:
        return jsonify({
            'exists': True,
            'user': user.to_dict()
        })
    
    return jsonify({'exists': False})

