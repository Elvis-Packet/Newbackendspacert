from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.space import Space, SpaceImage
from app.models.user import User
from app import db
from app.utils.validators import validate_space_data
from app.utils.cloudinary import upload_image
from app.utils.auth import role_required
from datetime import datetime

spaces_bp = Blueprint('spaces', __name__)

@spaces_bp.route('/', methods=['GET'])
def get_spaces():
    """
    List all available spaces
    """
    current_app.logger.info(f"GET /api/spaces called with args: {request.args}")
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        city = request.args.get('city')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        status = request.args.get('status')
        
        query = Space.query
        
        if status == 'available':
            query = query.filter_by(is_available=True)
        elif status == 'unavailable':
            query = query.filter_by(is_available=False)
        
        if city:
            query = query.filter(Space.city.ilike(f'%{city}%'))
        if min_price:
            query = query.filter(Space.price_per_hour >= min_price)
        if max_price:
            query = query.filter(Space.price_per_hour <= max_price)
        
        spaces = query.paginate(page=page, per_page=per_page)
        
        response = {
            'spaces': [space.to_dict() for space in spaces.items],
            'total': spaces.total,
            'pages': spaces.pages,
            'current_page': spaces.page
        }
        # current_app.logger.info(f"GET /api/spaces response: {response}")
        return jsonify(response), 200
    except Exception as e:
        # current_app.logger.error(f"Error in GET /api/spaces: {str(e)}")
        return jsonify({'error': 'Failed to fetch spaces'}), 500

@spaces_bp.route('/<int:space_id>', methods=['GET'])
def get_space(space_id):
    """
    Get a space by ID
    ---
    tags:
      - Spaces
    parameters:
      - name: space_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Space details
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Space'
      404:
        description: Not found
    """
    space = Space.query.get_or_404(space_id)
    return jsonify(space.to_dict()), 200

@spaces_bp.route('/', methods=['POST'])
@role_required('admin', 'owner')
def create_space():
    """
    Create a new space
    ---
    tags:
      - Spaces
    security:
      - BearerAuth: []
    parameters:
      - in: formData
        name: name
        type: string
        required: true
        description: Name of the space
        example: Conference Room
      - in: formData
        name: description
        type: string
        required: true
        description: Detailed description of the space
        example: Spacious room for meetings
      - in: formData
        name: address
        type: string
        required: true
        description: Physical address of the space
        example: 123 Main St
      - in: formData
        name: city
        type: string
        required: true
        description: City where the space is located
        example: Nairobi
      - in: formData
        name: price_per_hour
        type: number
        required: true
        description: Hourly rate in KES
        example: 100
      - in: formData
        name: capacity
        type: integer
        required: true
        description: Maximum number of people the space can accommodate
        example: 20
      - in: formData
        name: images
        type: file
        required: false
        description: Space images (supports multiple files)
        allowMultiple: true
    consumes:
      - multipart/form-data
    responses:
      201:
        description: Space created successfully
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Space'
      400:
        description: Invalid input
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Name is required
      401:
        description: Unauthorized - valid JWT token required
      403:
        description: Forbidden - user must be admin or owner
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role not in ['admin', 'owner']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.form.to_dict()
    is_valid, error_message = validate_space_data(data)
    
    if not is_valid:
        return jsonify({'error': error_message}), 400
    
    # Create space
    space = Space(
        name=data['name'],
        description=data['description'],
        address=data['address'],
        city=data['city'],
        price_per_hour=float(data['price_per_hour']),
        capacity=int(data['capacity']),
        owner_id=current_user_id
    )
    
    db.session.add(space)
    db.session.flush()  # Get space ID without committing
    
    # Handles image uploads
    if 'images' in request.files:
        images = request.files.getlist('images')
        for i, image in enumerate(images):
            if image:
                image_url = upload_image(image)
                space_image = SpaceImage(
                    space_id=space.id,
                    image_url=image_url,
                    is_primary=(i == 0)  # First image is primary
                )
                db.session.add(space_image)
    
    db.session.commit()
    return jsonify(space.to_dict()), 201

@spaces_bp.route('/<int:space_id>', methods=['PUT'])
@jwt_required()
def update_space(space_id):
    """
    Update a space
    ---
    tags:
      - Spaces
    security:
      - BearerAuth: []
    parameters:
      - name: space_id
        in: path
        type: integer
        required: true
        description: ID of the space to update
      - in: formData
        name: name
        type: string
        required: false
        description: Name of the space
        example: Conference Room
      - in: formData
        name: description
        type: string
        required: false
        description: Detailed description of the space
        example: Spacious room for meetings
      - in: formData
        name: address
        type: string
        required: false
        description: Physical address of the space
        example: 123 Main St
      - in: formData
        name: city
        type: string
        required: false
        description: City where the space is located
        example: Nairobi
      - in: formData
        name: price_per_hour
        type: number
        required: false
        description: Hourly rate in KES
        example: 100
      - in: formData
        name: capacity
        type: integer
        required: false
        description: Maximum number of people the space can accommodate
        example: 20
      - in: formData
        name: images
        type: file
        required: false
        description: Space images (supports multiple files)
        allowMultiple: true
    consumes:
      - multipart/form-data
    responses:
      200:
        description: Space updated successfully
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Space'
      400:
        description: Invalid input
      401:
        description: Unauthorized - valid JWT token required
      403:
        description: Forbidden - user not authorized to update this space
      404:
        description: Space not found
      422:
        description: Validation error
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    space = Space.query.get_or_404(space_id)
    
    # Allow space owner or admin to update
    if space.owner_id != current_user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get form data
    data = request.form.to_dict() if request.form else request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update only provided fields
    if 'name' in data:
        space.name = data['name']
    if 'description' in data:
        space.description = data['description']
    if 'address' in data:
        space.address = data['address']
    if 'city' in data:
        space.city = data['city']
    if 'price_per_hour' in data:
        try:
            space.price_per_hour = float(data['price_per_hour'])
        except ValueError:
            return jsonify({'error': 'Invalid price format'}), 400
    if 'capacity' in data:
        try:
            space.capacity = int(data['capacity'])
        except ValueError:
            return jsonify({'error': 'Invalid capacity format'}), 400
    
    # Handle image uploads
    if request.files and 'images' in request.files:
        # Delete existing images if new ones are provided
        SpaceImage.query.filter_by(space_id=space.id).delete()
        
        images = request.files.getlist('images')
        for i, image in enumerate(images):
            if image:
                try:
                    image_url = upload_image(image)
                    space_image = SpaceImage(
                        space_id=space.id,
                        image_url=image_url,
                        is_primary=(i == 0)
                    )
                    db.session.add(space_image)
                except Exception as e:
                    return jsonify({'error': f'Failed to upload image: {str(e)}'}), 422
    
    try:
        db.session.commit()
        return jsonify(space.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update space: {str(e)}'}), 422

@spaces_bp.route('/<int:space_id>', methods=['DELETE'])
@jwt_required()
def delete_space(space_id):
    """
    Delete a space
    ---
    tags:
      - Spaces
    security:
      - BearerAuth: []
    parameters:
      - name: space_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Space deleted
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Space deleted successfully
      403:
        description: Unauthorized
      404:
        description: Not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    space = Space.query.get_or_404(space_id)
    
    # Allow space owner or admin to delete a space
    if space.owner_id != current_user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(space)
    db.session.commit()
    return jsonify({'message': 'Space deleted successfully'}), 200

@spaces_bp.route('/my-spaces', methods=['GET'])
@jwt_required()
def get_my_spaces():
    """Get spaces owned by current user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role not in ['owner', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    spaces = Space.query.filter_by(owner_id=current_user_id).all()
    return jsonify([space.to_dict() for space in spaces]), 200

@spaces_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_space_stats():
    """Get statistics about spaces based on user role"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'admin':
        # Get all spaces stats
        spaces = Space.query.all()
    elif user.role == 'owner':
        # Get stats for owned spaces
        spaces = Space.query.filter_by(owner_id=current_user_id).all()
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    stats = {
        'total': len(spaces),
        'available': sum(1 for s in spaces if s.is_available),
        'booked': sum(1 for s in spaces if not s.is_available),
        'total_revenue': sum(
            booking.total_price 
            for space in spaces 
            for booking in space.bookings 
            if booking.payment_status == 'paid'
        )
    }
    
    return jsonify(stats), 200
