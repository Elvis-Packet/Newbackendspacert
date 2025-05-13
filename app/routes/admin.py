from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.space import Space
from app.models.booking import Booking, Payment
from app import db

admin_bp = Blueprint('admin', __name__)

# Decorator to check if user is admin
def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    """
    Get admin dashboard statistics
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
    responses:
      200:
        description: Admin statistics
      403:
        description: Admin privileges required
    """
    # Get user count
    total_users = User.query.count()
    
    # Get space count
    total_spaces = Space.query.count()
    
    # Get booking count
    total_bookings = Booking.query.count()
    
    # Get completed payments total
    completed_payments = Payment.query.filter_by(status='completed').all()
    total_revenue = sum(payment.amount for payment in completed_payments)
    
    return jsonify({
        'totalUsers': total_users,
        'totalSpaces': total_spaces,
        'totalBookings': total_bookings,
        'totalRevenue': float(total_revenue) if total_revenue else 0
    }), 200

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """
    Get all users (admin only)
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of users
      403:
        description: Admin privileges required
    """
    users = User.query.all()
    users_data = []
    
    for user in users:
        users_data.append({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_verified': user.is_verified,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    
    return jsonify(users_data), 200

@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def get_bookings():
    """
    Get all bookings (admin only)
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of bookings
      403:
        description: Admin privileges required
    """
    bookings = Booking.query.all()
    bookings_data = []
    
    for booking in bookings:
        user = User.query.get(booking.user_id)
        space = Space.query.get(booking.space_id)
        
        bookings_data.append({
            'id': booking.id,
            'user_id': booking.user_id,
            'user_name': f"{user.first_name} {user.last_name}" if user else "Unknown",
            'space_id': booking.space_id,
            'space_name': space.name if space else "Unknown",
            'start_time': booking.start_time.isoformat() if booking.start_time else None,
            'end_time': booking.end_time.isoformat() if booking.end_time else None,
            'total_price': float(booking.total_price) if booking.total_price else 0,
            'status': booking.status,
            'payment_status': booking.payment_status,
            'created_at': booking.created_at.isoformat() if booking.created_at else None
        })
    
    return jsonify(bookings_data), 200

@admin_bp.route('/users/recent', methods=['GET'])
@admin_required
def get_recent_users():
    """
    Get recent users (admin only)
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of recent users
      403:
        description: Admin privileges required
    """
    users = User.query.order_by(User.created_at.desc()).limit(10).all()
    users_data = []
    
    for user in users:
        users_data.append({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_verified': user.is_verified,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    
    return jsonify(users_data), 200

@admin_bp.route('/bookings/recent', methods=['GET'])
@admin_required
def get_recent_bookings():
    """
    Get recent bookings (admin only)
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of recent bookings
      403:
        description: Admin privileges required
    """
    bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    bookings_data = []
    
    for booking in bookings:
        user = User.query.get(booking.user_id)
        space = Space.query.get(booking.space_id)
        
        bookings_data.append({
            'id': booking.id,
            'user_id': booking.user_id,
            'user_name': f"{user.first_name} {user.last_name}" if user else "Unknown",
            'space_id': booking.space_id,
            'space_name': space.name if space else "Unknown",
            'start_time': booking.start_time.isoformat() if booking.start_time else None,
            'end_time': booking.end_time.isoformat() if booking.end_time else None,
            'total_price': float(booking.total_price) if booking.total_price else 0,
            'status': booking.status,
            'payment_status': booking.payment_status,
            'created_at': booking.created_at.isoformat() if booking.created_at else None
        })
    
    return jsonify(bookings_data), 200 