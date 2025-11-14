# backend/routes/student_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_utils import decode_token
from models.student_model import StudentModel # Import the model
from utils.db_connection import get_db_connection

student_bp = Blueprint('student', __name__)

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
        # Verify student role
        if decoded.get('role') != 'student':
            return jsonify({"message": "Unauthorized role"}), 403

        request.user = decoded
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@student_bp.route('/api/student/details', methods=['GET'])
@token_required
def get_student_details():
    user_id = request.user['user_id'] # user_id from the token

    student = StudentModel.get_student_by_user_id(user_id) # Call the model method

    if not student:
        return jsonify({"success": False, "message": "Student not found"}), 404

    return jsonify({"success": True, "student": student}), 200

@student_bp.route('/api/student/circulars', methods=['GET']) # Changed route name to reflect circulars
@token_required # Circulars also need authentication
def get_student_circulars():
    # We need the actual student_id (from student_details) for circulars filtering
    user_id = request.user['user_id']
    
    conn = get_db_connection() # Temporary connection to get student_id
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student_details WHERE user_id = %s", (user_id,))
    student_record = cursor.fetchone()
    cursor.close()
    conn.close()

    if not student_record:
        return jsonify({"success": False, "message": "Student record not found for user."}), 404
        
    student_id = student_record['student_id']

    circulars = StudentModel.get_notifications_for_student(student_id) # Call the model method

    return jsonify({"success": True, "circulars": circulars}), 200