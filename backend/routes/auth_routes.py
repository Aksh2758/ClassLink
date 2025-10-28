from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from utils.db_connection import get_db_connection
from utils.jwt_utils import create_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user_id = data.get("id")
    password = data.get("password")
    role = data.get("role")

    if not all([user_id, password, role]):
        return jsonify({"success": False, "message": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, password_hash, role FROM users WHERE id = %s AND role = %s",(user_id, role))
    user = cursor.fetchone()
    conn.close()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    if user['password_hash'] != password:  # plain check for now
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Invalid password"}), 401

    # --- success case ---
    token = create_token(user['id'], user['role'])

    cursor.close()
    conn.close()
    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "role": user['role']
    }), 200
