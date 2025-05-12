from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.booking import Booking, Payment
from app.models.space import Space
from app.models.user import User
from app import db
from app.utils.validators import validate_booking_dates
from app.utils.email import send_booking_confirmation_email
from app.utils.auth import role_required
from datetime import datetime

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/', methods=['GET'])
@jwt_required()
def get_bookings():
    """Get bookings based on user role"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'admin':
        # Admin can see all bookings
        bookings = Booking.query.all()
    elif user.role == 'owner':
        # Owner can see bookings for their spaces
        bookings = Booking.query.join(Space).filter(Space.owner_id == current_user_id).all()
    else:
        # Client can only see their own bookings
        bookings = Booking.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([booking.to_dict() for booking in bookings]), 200

@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get a specific booking"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    booking = Booking.query.get_or_404(booking_id)
    
    # Check authorization
    if not (user.role == 'admin' or 
            user.id == booking.user_id or 
            (user.role == 'owner' and booking.space.owner_id == user.id)):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(booking.to_dict()), 200

@bookings_bp.route('/', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new booking"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Only clients can create bookings
    if user.role not in ['client', 'admin']:
        return jsonify({'error': 'Only clients can create bookings'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['space_id', 'start_time', 'end_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate dates
    is_valid, error_message = validate_booking_dates(data['start_time'], data['end_time'])
    if not is_valid:
        return jsonify({'error': error_message}), 400
    
    # Validate space exists and is available
    space = Space.query.get_or_404(data['space_id'])
    if not space.is_available:
        return jsonify({'error': 'Space is not available'}), 400
    
    # Check for overlapping bookings
    start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
    
    overlapping_booking = Booking.query.filter(
        Booking.space_id == space.id,
        Booking.status != 'cancelled',
        (
            (Booking.start_time <= start_time) & (Booking.end_time > start_time) |
            (Booking.start_time < end_time) & (Booking.end_time >= end_time) |
            (Booking.start_time >= start_time) & (Booking.end_time <= end_time)
        )
    ).first()
    
    if overlapping_booking:
        return jsonify({'error': 'Space is already booked for this time period'}), 400
    
    # Calculate total price
    duration_hours = (end_time - start_time).total_seconds() / 3600
    total_price = space.price_per_hour * duration_hours
    
    # Create booking
    booking = Booking(
        space_id=space.id,
        user_id=current_user_id,
        start_time=start_time,
        end_time=end_time,
        total_price=total_price,
        purpose="test purpose"
    )
    
    db.session.add(booking)
    db.session.commit()
    
    # Send confirmation email
    send_booking_confirmation_email(booking)
    
    return jsonify(booking.to_dict()), 201

@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancel a booking"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    booking = Booking.query.get_or_404(booking_id)
    
    # Check authorization
    if not (user.role == 'admin' or 
            user.id == booking.user_id or 
            (user.role == 'owner' and booking.space.owner_id == user.id)):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if booking can be cancelled
    if booking.status == 'cancelled':
        return jsonify({'error': 'Booking is already cancelled'}), 400
    
    if booking.status == 'completed':
        return jsonify({'error': 'Cannot cancel completed booking'}), 400
    
    # Cancel booking
    booking.status = 'cancelled'
    
    # If payment exists, mark it as refunded
    if booking.payment:
        booking.payment.status = 'refunded'
    
    db.session.commit()
    return jsonify(booking.to_dict()), 200

@bookings_bp.route('/<int:booking_id>/payment', methods=['POST'])
@jwt_required()
def process_payment(booking_id):
    """
    Process payment for a booking
    ---
    tags:
      - Bookings
    security:
      - BearerAuth: []
    parameters:
      - name: booking_id
        in: path
        type: integer
        required: true
        description: Booking ID
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - payment_method
            properties:
              payment_method:
                type: string
                enum: [mpesa, card, cash]
                example: mpesa
              transaction_id:
                type: string
                example: MPESA123456789
    responses:
      201:
        description: Payment processed
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Payment'
      400:
        description: Invalid input or booking status
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Invalid booking status for payment
      401:
        description: Unauthorized
      403:
        description: Forbidden - user not authorized to process payment
      404:
        description: Booking not found
    """
    current_user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if booking.status != 'pending':
        return jsonify({'error': 'Invalid booking status for payment'}), 400
    
    data = request.get_json()
    if 'payment_method' not in data:
        return jsonify({'error': 'Payment method is required'}), 400
    
    # Create payment record
    payment = Payment(
        booking_id=booking.id,
        amount=booking.total_price,
        payment_method=data['payment_method'],
        transaction_id=data.get('transaction_id')  # For external payment systems
    )
    
    db.session.add(payment)
    
    # Update booking status
    booking.status = 'confirmed'
    booking.payment_status = 'paid'
    
    db.session.commit()
    return jsonify(payment.to_dict()), 201

@bookings_bp.route('/by-spaces', methods=['GET'])
@jwt_required()
def get_bookings_by_spaces():
    """Get bookings for specified spaces"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Get space IDs from query params
    space_ids = request.args.getlist('space_ids', type=int)
    
    # Validate ownership or admin status
    if user.role == 'admin':
        bookings = Booking.query.filter(Booking.space_id.in_(space_ids)).all()
    elif user.role == 'owner':
        # Only get bookings for spaces owned by the user
        owned_spaces = Space.query.filter_by(owner_id=current_user_id).all()
        owned_space_ids = [space.id for space in owned_spaces]
        valid_space_ids = list(set(space_ids) & set(owned_space_ids))
        bookings = Booking.query.filter(Booking.space_id.in_(valid_space_ids)).all()
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify([booking.to_dict() for booking in bookings]), 200

@bookings_bp.route('/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():
    """Get current user's bookings"""
    current_user_id = get_jwt_identity()
    
    bookings = Booking.query.filter_by(user_id=current_user_id).all()
    return jsonify([booking.to_dict() for booking in bookings]), 200

@bookings_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_booking_stats():
    """Get booking statistics based on user role"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'admin':
        # Get all booking stats
        bookings = Booking.query.all()
    elif user.role == 'owner':
        # Get stats for bookings on owned spaces
        owned_spaces = Space.query.filter_by(owner_id=current_user_id).all()
        space_ids = [space.id for space in owned_spaces]
        bookings = Booking.query.filter(Booking.space_id.in_(space_ids)).all()
    else:
        # Get stats for user's own bookings
        bookings = Booking.query.filter_by(user_id=current_user_id).all()
    
    stats = {
        'total': len(bookings),
        'pending': sum(1 for b in bookings if b.status == 'pending'),
        'confirmed': sum(1 for b in bookings if b.status == 'confirmed'),
        'cancelled': sum(1 for b in bookings if b.status == 'cancelled'),
        'completed': sum(1 for b in bookings if b.status == 'completed'),
        'total_value': sum(b.total_price for b in bookings),
        'paid_value': sum(b.total_price for b in bookings if b.payment_status == 'paid')
    }
    
    return jsonify(stats), 200