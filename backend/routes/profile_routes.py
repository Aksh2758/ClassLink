# backend/routes/profile_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_utils import token_required
from models.profile_model import ProfileModel
import re # For password validation

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

# ---------- Get User Profile ----------
@profile_bp.route('/', methods=['GET'])
@token_required(roles=['student', 'faculty', 'admin'])
def get_profile():
    """
    Endpoint to retrieve the authenticated user's profile details.
    """
    user_id = request.user['user_id']
    user_role = request.user['role']

    try:
        profile_data = ProfileModel.get_user_profile(user_id, user_role)
        if not profile_data:
            return jsonify({"success": False, "error": "Profile not found."}), 404
        
        return jsonify({"success": True, "profile": profile_data}), 200
    except Exception as e:
        print(f"Error fetching profile for user {user_id} ({user_role}): {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching profile."}), 500

# ---------- Update User Profile ----------
@profile_bp.route('/', methods=['PUT'])
@token_required(roles=['student', 'faculty', 'admin'])
def update_profile():
    """
    Endpoint to update the authenticated user's profile details.
    Fields allowed for update depend on the user's role.
    """
    user_id = request.user['user_id']
    user_role = request.user['role']
    data = request.json

    updated = False
    message = "No fields to update or no changes made."

    try:
        if user_role == 'student':
            name = data.get('name')
            usn = data.get('usn')
            semester = data.get('semester')
            section = data.get('section')
            dept_code = data.get('dept_code')

            # Ensure 'name' is always provided if attempting to update
            if not name:
                return jsonify({"success": False, "error": "Student 'name' is required for update."}), 400

            updated = ProfileModel.update_student_profile(
                user_id, name, usn, semester, section, dept_code
            )
            message = "Student profile updated successfully." if updated else message

        elif user_role == 'faculty':
            name = data.get('name')
            designation = data.get('designation')
            dept_code = data.get('dept_code')

            # Ensure 'name' is always provided if attempting to update
            if not name:
                return jsonify({"success": False, "error": "Faculty 'name' is required for update."}), 400

            updated = ProfileModel.update_faculty_profile(
                user_id, name, designation, dept_code
            )
            message = "Faculty profile updated successfully." if updated else message
            
        elif user_role == 'admin':
            # Admins generally only have email/password in 'users' table,
            # no specific 'admin_details' in your schema to update here.
            message = "Admin profiles can only update password via /change-password endpoint."
            return jsonify({"success": False, "error": message}), 403 # Not allowed to update profile via this endpoint
        
        return jsonify({"success": True, "message": message}), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400 # Catching errors like dept_code not found
    except Exception as e:
        print(f"Error updating profile for user {user_id} ({user_role}): {e}")
        return jsonify({"success": False, "error": "Internal server error while updating profile."}), 500

# ---------- Change Password ----------
@profile_bp.route('/change-password', methods=['PUT'])
@token_required(roles=['student', 'faculty', 'admin'])
def change_password():
    """
    Endpoint for any authenticated user to change their password.
    Requires current_password and new_password.
    """
    user_id = request.user['user_id']
    data = request.json

    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not all([current_password, new_password]):
        return jsonify({"success": False, "error": "Missing 'current_password' or 'new_password'."}), 400

    # Basic password strength validation
    if len(new_password) < 8:
        return jsonify({"success": False, "error": "New password must be at least 8 characters long."}), 400
    if not re.search(r"[A-Z]", new_password):
        return jsonify({"success": False, "error": "New password must contain at least one uppercase letter."}), 400
    if not re.search(r"[a-z]", new_password):
        return jsonify({"success": False, "error": "New password must contain at least one lowercase letter."}), 400
    if not re.search(r"[0-9]", new_password):
        return jsonify({"success": False, "error": "New password must contain at least one digit."}), 400
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
        return jsonify({"success": False, "error": "New password must contain at least one special character."}), 400

    try:
        success, message = ProfileModel.change_user_password(user_id, current_password, new_password)
        if success:
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "error": message}), 401 # 401 for password mismatch
    except Exception as e:
        print(f"Error changing password for user {user_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error while changing password."}), 500