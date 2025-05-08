from flask import Blueprint, request, jsonify
from app.models.testimonial import Testimonial
from app import db

testimonials_bp = Blueprint('testimonials', __name__, url_prefix='/api/testimonials')

@testimonials_bp.route('', methods=['GET'])
def get_testimonials():
    testimonials = Testimonial.query.all()
    result = [t.to_dict() for t in testimonials]
    return jsonify(result), 200

@testimonials_bp.route('', methods=['POST'])
def create_testimonial():
    data = request.get_json()
    user_name = data.get('user_name')
    content = data.get('content')
    if not user_name or not content:
        return jsonify({'error': 'Missing user_name or content'}), 400
    testimonial = Testimonial(user_name=user_name, content=content)
    db.session.add(testimonial)
    db.session.commit()
    return jsonify(testimonial.to_dict()), 201
