from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({"error": "User not found"}), 404
                
            if user.role not in roles:
                return jsonify({"error": "Unauthorized - insufficient role"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper