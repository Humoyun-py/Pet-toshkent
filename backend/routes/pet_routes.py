from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Pet
from utils import save_image, delete_image, admin_required

pet_bp = Blueprint('pets', __name__)

@pet_bp.route('/list', methods=['GET'])
def list_pets():
    """Get all approved pets with filters"""
    # Get query params
    pet_type = request.args.get('type')
    status = request.args.get('status')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    location = request.args.get('location')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # Build query
    query = Pet.query.filter_by(approved=True, is_active=True)
    
    if pet_type:
        query = query.filter_by(pet_type=pet_type)
    if status:
        query = query.filter_by(status=status)
    if min_price is not None:
        query = query.filter(Pet.price >= min_price)
    if max_price is not None:
        query = query.filter(Pet.price <= max_price)
    if location:
        query = query.filter(Pet.location.ilike(f'%{location}%'))
    
    # Order by newest first
    query = query.order_by(Pet.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'pets': [pet.to_dict() for pet in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })

@pet_bp.route('/featured', methods=['GET'])
def featured_pets():
    """Get featured/latest pets for homepage"""
    pets = Pet.query.filter_by(approved=True, is_active=True)\
        .order_by(Pet.created_at.desc())\
        .limit(8).all()
    
    return jsonify({'pets': [pet.to_dict() for pet in pets]})

@pet_bp.route('/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    """Get single pet details"""
    pet = Pet.query.get_or_404(pet_id)
    
    # Increment views
    pet.views += 1
    db.session.commit()
    
    return jsonify({'pet': pet.to_dict()})

@pet_bp.route('/add', methods=['POST'])
@jwt_required(optional=True)
def add_pet():
    """Add new pet listing"""
    user_id = get_jwt_identity() or 1  # Default to admin user for demo
    
    # Handle form data or JSON
    data = {}
    image_file = None
    
    # Check content type
    content_type = request.content_type or ''
    print(f"Content-Type: {content_type}")
    
    if 'multipart/form-data' in content_type:
        data = request.form.to_dict()
        image_file = request.files.get('image')
        print(f"Form data: {data}")
        print(f"Image file: {image_file}")
        if image_file:
            print(f"Image filename: {image_file.filename}")
    else:
        try:
            data = request.get_json() or {}
        except:
            data = {}
    
    # Validate required fields
    required = ['name', 'pet_type', 'status']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Save image if provided
    image_filename = None
    if image_file and image_file.filename:
        image_filename = save_image(image_file)
    
    # Create pet
    pet = Pet(
        user_id=user_id,
        name=data['name'],
        pet_type=data['pet_type'],
        breed=data.get('breed'),
        age=data.get('age'),
        gender=data.get('gender'),
        status=data['status'],
        price=float(data.get('price', 0)),
        description=data.get('description'),
        image=image_filename,
        location=data.get('location'),
        approved=True  # Auto-approve for demo (set False for production)
    )
    
    db.session.add(pet)
    db.session.commit()
    
    return jsonify({
        'message': 'Pet listing created. Awaiting admin approval.',
        'pet': pet.to_dict()
    }), 201

@pet_bp.route('/<int:pet_id>', methods=['PUT'])
@jwt_required()
def update_pet(pet_id):
    """Update pet listing"""
    user_id = get_jwt_identity()
    pet = Pet.query.get_or_404(pet_id)
    
    # Check ownership or admin
    from models import User
    user = User.query.get(user_id)
    if pet.user_id != user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() if request.is_json else request.form.to_dict()
    
    # Update fields
    updateable = ['name', 'pet_type', 'breed', 'age', 'gender', 'status', 'price', 'description', 'location']
    for field in updateable:
        if field in data:
            if field == 'price':
                setattr(pet, field, float(data[field]))
            else:
                setattr(pet, field, data[field])
    
    # Handle image update
    if request.files.get('image'):
        if pet.image:
            delete_image(pet.image)
        pet.image = save_image(request.files['image'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Pet updated',
        'pet': pet.to_dict()
    })

@pet_bp.route('/<int:pet_id>', methods=['DELETE'])
@jwt_required()
def delete_pet(pet_id):
    """Delete pet listing"""
    user_id = get_jwt_identity()
    pet = Pet.query.get_or_404(pet_id)
    
    # Check ownership or admin
    from models import User
    user = User.query.get(user_id)
    if pet.user_id != user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete image
    if pet.image:
        delete_image(pet.image)
    
    db.session.delete(pet)
    db.session.commit()
    
    return jsonify({'message': 'Pet deleted'})

@pet_bp.route('/my', methods=['GET'])
@jwt_required()
def my_pets():
    """Get current user's pets"""
    user_id = get_jwt_identity()
    pets = Pet.query.filter_by(user_id=user_id).order_by(Pet.created_at.desc()).all()
    
    return jsonify({'pets': [pet.to_dict() for pet in pets]})

# Admin routes
@pet_bp.route('/pending', methods=['GET'])
@admin_required()
def pending_pets():
    """Get pets pending approval (admin only)"""
    pets = Pet.query.filter_by(approved=False, is_active=True)\
        .order_by(Pet.created_at.desc()).all()
    
    return jsonify({'pets': [pet.to_dict() for pet in pets]})

@pet_bp.route('/<int:pet_id>/approve', methods=['POST'])
@admin_required()
def approve_pet(pet_id):
    """Approve pet listing (admin only)"""
    pet = Pet.query.get_or_404(pet_id)
    pet.approved = True
    db.session.commit()
    
    return jsonify({
        'message': 'Pet approved',
        'pet': pet.to_dict()
    })

@pet_bp.route('/<int:pet_id>/reject', methods=['POST'])
@admin_required()
def reject_pet(pet_id):
    """Reject pet listing (admin only)"""
    pet = Pet.query.get_or_404(pet_id)
    pet.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Pet rejected'})

@pet_bp.route('/all', methods=['GET'])
@admin_required()
def all_pets():
    """Get all pets including unapproved (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Pet.query.order_by(Pet.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'pets': [pet.to_dict() for pet in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })
