from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Donation, User
from utils import admin_required
from datetime import datetime, timedelta
from sqlalchemy import func

donation_bp = Blueprint('donations', __name__)

@donation_bp.route('/create', methods=['POST'])
def create_donation():
    """Create new donation"""
    data = request.get_json()
    
    if not data.get('amount'):
        return jsonify({'error': 'Amount is required'}), 400
    
    # Get user if authenticated
    user_id = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        pass
    
    donation = Donation(
        user_id=user_id,
        amount=float(data['amount']),
        currency=data.get('currency', 'UZS'),
        payment_method=data.get('payment_method'),
        donor_name=data.get('donor_name'),
        donor_phone=data.get('donor_phone'),
        message=data.get('message'),
        is_anonymous=data.get('is_anonymous', False),
        status='pending'
    )
    
    db.session.add(donation)
    db.session.commit()
    
    # Generate payment link based on method
    payment_link = None
    if data.get('payment_method') == 'click':
        payment_link = f"https://my.click.uz/services/pay?merchant_id=YOUR_MERCHANT&amount={donation.amount}&transaction_id={donation.id}"
    elif data.get('payment_method') == 'payme':
        payment_link = f"https://checkout.paycom.uz/YOUR_MERCHANT_ID?amount={int(donation.amount * 100)}"
    
    return jsonify({
        'message': 'Donation created',
        'donation': donation.to_dict(),
        'payment_link': payment_link
    }), 201

@donation_bp.route('/callback', methods=['POST'])
def payment_callback():
    """Handle payment callback from Click/Payme"""
    data = request.get_json()
    
    donation_id = data.get('transaction_id') or data.get('donation_id')
    if not donation_id:
        return jsonify({'error': 'Transaction ID required'}), 400
    
    donation = Donation.query.get(donation_id)
    if not donation:
        return jsonify({'error': 'Donation not found'}), 404
    
    # Update status based on payment result
    if data.get('status') == 'success':
        donation.status = 'completed'
        donation.payment_id = data.get('payment_id')
    else:
        donation.status = 'failed'
    
    db.session.commit()
    
    return jsonify({'message': 'Status updated'})

@donation_bp.route('/public-stats', methods=['GET'])
def public_stats():
    """Get public donation statistics"""
    total_donations = db.session.query(func.sum(Donation.amount))\
        .filter_by(status='completed').scalar() or 0
    
    donation_count = Donation.query.filter_by(status='completed').count()
    
    # Recent donations (anonymous names hidden)
    recent = Donation.query.filter_by(status='completed')\
        .order_by(Donation.created_at.desc()).limit(10).all()
    
    return jsonify({
        'total_amount': total_donations,
        'total_count': donation_count,
        'recent_donations': [d.to_dict() for d in recent]
    })

# Admin routes
@donation_bp.route('/stats', methods=['GET'])
@admin_required()
def admin_stats():
    """Get detailed donation statistics (admin only)"""
    # Time ranges
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Total stats
    total_amount = db.session.query(func.sum(Donation.amount))\
        .filter_by(status='completed').scalar() or 0
    
    # Today stats
    today_amount = db.session.query(func.sum(Donation.amount))\
        .filter(
            Donation.status == 'completed',
            func.date(Donation.created_at) == today
        ).scalar() or 0
    
    # Week stats
    week_amount = db.session.query(func.sum(Donation.amount))\
        .filter(
            Donation.status == 'completed',
            func.date(Donation.created_at) >= week_ago
        ).scalar() or 0
    
    # Month stats
    month_amount = db.session.query(func.sum(Donation.amount))\
        .filter(
            Donation.status == 'completed',
            func.date(Donation.created_at) >= month_ago
        ).scalar() or 0
    
    # Count by status
    status_counts = db.session.query(
        Donation.status, func.count(Donation.id)
    ).group_by(Donation.status).all()
    
    # Daily donations for chart (last 30 days)
    daily_donations = db.session.query(
        func.date(Donation.created_at).label('date'),
        func.sum(Donation.amount).label('amount')
    ).filter(
        Donation.status == 'completed',
        func.date(Donation.created_at) >= month_ago
    ).group_by(func.date(Donation.created_at))\
    .order_by(func.date(Donation.created_at)).all()
    
    return jsonify({
        'total_amount': total_amount,
        'today_amount': today_amount,
        'week_amount': week_amount,
        'month_amount': month_amount,
        'status_counts': dict(status_counts),
        'daily_donations': [{'date': str(d.date), 'amount': d.amount} for d in daily_donations]
    })

@donation_bp.route('/all', methods=['GET'])
@admin_required()
def all_donations():
    """Get all donations (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Donation.query
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Donation.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'donations': [d.to_dict() for d in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })
