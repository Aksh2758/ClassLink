from flask import Blueprint, request, jsonify
from utils.db_connection import get_db_connection
from utils.jwt_utils import decode_token

student_bp = Blueprint('student', __name__)

def token_required(f):
    """Middleware to check if JWT is valid."""
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid token"}), 401
        token = auth_header.split(" ")[1]
        decoded = decode_token(token)
        if not decoded:
            return jsonify({"message": "Invalid or expired token"}), 401
        request.user = decoded  # Attach decoded user info to request
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@student_bp.route('/api/student/details', methods=['GET'])
@token_required
def get_student_details():
    user_id = request.user['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name, usn, email FROM student_details WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if not student:
        return jsonify({"success": False, "message": "Student not found"}), 404

    return jsonify({"success": True, "student": student}), 200

