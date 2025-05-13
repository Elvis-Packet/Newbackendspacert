from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.space import Space
from app.models.review import Review
from app import db

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('', methods=['GET'])
def get_reviews():
    """
    Get all reviews for a space
    ---
    tags:
      - Reviews
    parameters:
      - name: space_id
        in: query
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of reviews
      404:
        description: Space not found
    """
    space_id = request.args.get('space_id', type=int)
    if not space_id:
        return jsonify({'error': 'Space ID is required'}), 400
    
    space = Space.query.get(space_id)
    if not space:
        return jsonify({'error': 'Space not found'}), 404
    
    reviews = Review.query.filter_by(space_id=space_id).all()
    reviews_data = []
    
    for review in reviews:
        user = User.query.get(review.user_id)
        reviews_data.append({
            'id': review.id,
            'user_id': review.user_id,
            'user_name': f"{user.first_name} {user.last_name}" if user else "Unknown User",
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat() if review.created_at else None
        })
    
    return jsonify({
        'space_id': space_id,
        'space_name': space.name,
        'reviews': reviews_data
    }), 200

@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    """
    Create a new review for a space
    ---
    tags:
      - Reviews
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              space_id:
                type: integer
              rating:
                type: integer
              comment:
                type: string
    responses:
      201:
        description: Review created
      400:
        description: Invalid request
      404:
        description: Space not found
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    space_id = data.get('space_id')
    rating = data.get('rating')
    comment = data.get('comment')
    
    if not space_id or not rating:
        return jsonify({'error': 'Space ID and rating are required'}), 400
    
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
    
    space = Space.query.get(space_id)
    if not space:
        return jsonify({'error': 'Space not found'}), 404
    
    # Check if user already reviewed this space
    existing_review = Review.query.filter_by(space_id=space_id, user_id=current_user_id).first()
    if existing_review:
        return jsonify({'error': 'You have already reviewed this space'}), 400
    
    # Create new review
    review = Review(
        user_id=current_user_id,
        space_id=space_id,
        rating=rating,
        comment=comment
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'id': review.id,
        'user_id': review.user_id,
        'space_id': review.space_id,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.isoformat() if review.created_at else None
    }), 201

@reviews_bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """
    Update a review
    ---
    tags:
      - Reviews
    security:
      - bearerAuth: []
    parameters:
      - name: review_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              rating:
                type: integer
              comment:
                type: string
    responses:
      200:
        description: Review updated
      400:
        description: Invalid request
      403:
        description: Unauthorized
      404:
        description: Review not found
    """
    current_user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    if review.user_id != current_user_id:
        return jsonify({'error': 'You do not have permission to update this review'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    rating = data.get('rating')
    comment = data.get('comment')
    
    if rating is not None:
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
        review.rating = rating
    
    if comment is not None:
        review.comment = comment
    
    db.session.commit()
    
    return jsonify({
        'id': review.id,
        'user_id': review.user_id,
        'space_id': review.space_id,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.isoformat() if review.created_at else None
    }), 200

@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """
    Delete a review
    ---
    tags:
      - Reviews
    security:
      - bearerAuth: []
    parameters:
      - name: review_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Review deleted
      403:
        description: Unauthorized
      404:
        description: Review not found
    """
    current_user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    if review.user_id != current_user_id:
        return jsonify({'error': 'You do not have permission to delete this review'}), 403
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'message': 'Review deleted successfully'}), 200 