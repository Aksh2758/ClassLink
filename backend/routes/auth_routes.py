from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from utils.db_connection import get_db_connection
from utils.jwt_utils import create_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    identifier = data.get("identifier") # Changed from 'login_id' to 'identifier'
    password = data.get("password")
    role = data.get("role")            # student / faculty / admin

    if not all([identifier, password, role]):
        return jsonify({"success": False, "message": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    user = None
    if role == "student":
        # For students, 'identifier' is USN
        cursor.execute(
            """
            SELECT u.id, u.email, u.password_hash, u.role, sd.usn
            FROM users u
            JOIN student_details sd ON u.id = sd.user_id
            WHERE sd.usn = %s AND u.role = %s
            """,
            (identifier, role)
        )
        user = cursor.fetchone()
    elif role == "faculty" or role == "admin": # Admin can also login with email
        # For faculty and admin, 'identifier' is email
        cursor.execute(
            "SELECT id, email, password_hash, role FROM users WHERE email = %s AND role = %s",
            (identifier, role)
        )
        user = cursor.fetchone()
    else:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Invalid role specified"}), 400


    if not user:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "User not found or role mismatch"}), 401

    # Compare hashed password
    if not check_password_hash(user["password_hash"], password):
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Invalid password"}), 401

    # Create token
    # Ensure the 'id' field is correctly picked from the 'users' table (aliased as u.id in student query)
    token = create_token(user["id"], user["role"])

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "role": user["role"]
    }), 200