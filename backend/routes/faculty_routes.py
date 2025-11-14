# backend/routes/faculty_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_utils import decode_token
from models.faculty_model import FacultyModel # Import the model
# Assuming you will have a general `auth_middleware.py` or similar for token_required
# For now, keeping it here, but it's often a good candidate for a shared `utils` file.

faculty_bp = Blueprint('faculty', __name__)

# Moving token_required to a shared util if it's used by multiple blueprints
# For now, let's assume it's still defined here or imported from a common place.
def token_required(f):
    """Middleware to check if JWT is valid and attach user info to request."""
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid token"}), 401
        token = auth_header.split(" ")[1]
        decoded = decode_token(token)
        if not decoded:
            return jsonify({"message": "Invalid or expired token"}), 401
        # It's good practice to verify the role if this route is faculty-specific
        if decoded.get('role') != 'faculty' and decoded.get('role') != 'admin': # Admin might also access faculty details
            return jsonify({"message": "Unauthorized role"}), 403

        request.user = decoded
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@faculty_bp.route('/api/faculty/details', methods=['GET'])
@token_required
def get_faculty_details():
    user_id = request.user['user_id'] # user_id from the token

    faculty = FacultyModel.get_faculty_by_user_id(user_id) # Call the model method

    if not faculty:
        return jsonify({"success": False, "message": "Faculty not found"}), 404

    return jsonify({"success": True, "faculty": faculty}), 200