from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.email import send_invoice_email
from app.models.user import User
from app.models.booking import Booking
from app.models.space import Space
from app import db

emails_bp = Blueprint('emails', __name__)

@emails_bp.route('/invoice', methods=['POST'])
@jwt_required()
def send_invoice():
    """
    Send invoice email to user
    ---
    tags:
      - Emails
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
              invoiceNumber:
                type: string
              booking:
                type: object
              paymentMethod:
                type: string
    responses:
      200:
        description: Email sent successfully
      400:
        description: Bad request
      401:
        description: Unauthorized
      500:
        description: Internal server error
    """
    current_user_id = get_jwt_identity()
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email')
    invoice_number = data.get('invoiceNumber')
    booking_data = data.get('booking')
    payment_method = data.get('paymentMethod')
    
    if not email or not invoice_number or not booking_data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get user and verify permissions
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get booking from database to ensure its valid
    booking_id = booking_data.get('id')
    if not booking_id:
        return jsonify({'error': 'Invalid booking data'}), 400
    
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Verify the booking belongs to the user
    if booking.user_id != current_user_id:
        return jsonify({'error': 'You do not have permission to access this booking'}), 403
    
    # Send the invoice email
    result = send_invoice_email(user, booking, invoice_number, payment_method)
    if result:
        return jsonify({'message': 'Invoice email sent successfully'}), 200
    else:
        return jsonify({'error': 'Failed to send invoice email'}), 500 