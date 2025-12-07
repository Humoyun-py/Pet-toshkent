from flask import Blueprint, request, jsonify
from models import db, Clinic
from utils import admin_required, save_image, delete_image
from math import cos, radians

clinic_bp = Blueprint('clinics', __name__)

@clinic_bp.route('/list', methods=['GET'])
def list_clinics():
    """Get all active clinics"""
    clinics = Clinic.query.filter_by(is_active=True).all()
    return jsonify({'clinics': [clinic.to_dict() for clinic in clinics]})

@clinic_bp.route('/<int:clinic_id>', methods=['GET'])
def get_clinic(clinic_id):
    """Get single clinic details"""
    clinic = Clinic.query.get_or_404(clinic_id)
    return jsonify({'clinic': clinic.to_dict()})

@clinic_bp.route('/near', methods=['POST'])
def nearby_clinics():
    """Find clinics near location"""
    data = request.get_json()
    
    lat = data.get('lat')
    lng = data.get('lng')
    radius = data.get('radius', 5)  # km
    
    if lat is None or lng is None:
        return jsonify({'error': 'lat and lng required'}), 400
    
    # Calculate bounding box
    lat_range = radius / 111.0
    lng_range = radius / (111.0 * abs(cos(radians(lat))))
    
    clinics = Clinic.query.filter(
        Clinic.lat.between(lat - lat_range, lat + lat_range),
        Clinic.lng.between(lng - lng_range, lng + lng_range),
        Clinic.is_active == True
    ).all()
    
    # Calculate actual distance and sort
    def calc_distance(clinic):
        from math import sqrt, pow
        return sqrt(pow((clinic.lat - lat) * 111, 2) + pow((clinic.lng - lng) * 111 * cos(radians(lat)), 2))
    
    clinics_with_distance = []
    for clinic in clinics:
        clinic_dict = clinic.to_dict()
        clinic_dict['distance'] = round(calc_distance(clinic), 2)
        clinics_with_distance.append(clinic_dict)
    
    # Sort by distance
    clinics_with_distance.sort(key=lambda x: x['distance'])
    
    return jsonify({'clinics': clinics_with_distance})

# Admin routes
@clinic_bp.route('/add', methods=['POST'])
@admin_required()
def add_clinic():
    """Add new clinic (admin only)"""
    if request.content_type.startswith('multipart/form-data'):
        data = request.form.to_dict()
        image_file = request.files.get('image')
    else:
        data = request.get_json()
        image_file = None
    
    required = ['name', 'address', 'lat', 'lng']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    image_filename = None
    if image_file:
        image_filename = save_image(image_file)
    
    clinic = Clinic(
        name=data['name'],
        address=data['address'],
        lat=float(data['lat']),
        lng=float(data['lng']),
        phone=data.get('phone'),
        website=data.get('website'),
        working_hours=data.get('working_hours'),
        services=data.get('services'),
        rating=float(data.get('rating', 0)),
        image=image_filename
    )
    
    db.session.add(clinic)
    db.session.commit()
    
    return jsonify({
        'message': 'Clinic added',
        'clinic': clinic.to_dict()
    }), 201

@clinic_bp.route('/<int:clinic_id>', methods=['PUT'])
@admin_required()
def update_clinic(clinic_id):
    """Update clinic (admin only)"""
    clinic = Clinic.query.get_or_404(clinic_id)
    
    data = request.get_json() if request.is_json else request.form.to_dict()
    
    updateable = ['name', 'address', 'lat', 'lng', 'phone', 'website', 'working_hours', 'services', 'rating']
    for field in updateable:
        if field in data:
            if field in ['lat', 'lng', 'rating']:
                setattr(clinic, field, float(data[field]))
            else:
                setattr(clinic, field, data[field])
    
    if request.files.get('image'):
        if clinic.image:
            delete_image(clinic.image)
        clinic.image = save_image(request.files['image'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Clinic updated',
        'clinic': clinic.to_dict()
    })

@clinic_bp.route('/<int:clinic_id>', methods=['DELETE'])
@admin_required()
def delete_clinic(clinic_id):
    """Delete clinic (admin only)"""
    clinic = Clinic.query.get_or_404(clinic_id)
    
    if clinic.image:
        delete_image(clinic.image)
    
    db.session.delete(clinic)
    db.session.commit()
    
    return jsonify({'message': 'Clinic deleted'})
