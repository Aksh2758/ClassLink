# backend/routes/circulars_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_utils import token_required
from models.circulars_model import CircularsModel
from models.attendance_model import AttendanceModel # For _get_entity_ids (dept_id)

circulars_bp = Blueprint('circulars', __name__, url_prefix='/api/circulars')

# Valid audience types as per ENUM in schema
VALID_AUDIENCES = {'all', 'students', 'faculty', 'specific_dept'}

# ---------- Faculty/Admin: Create New Circular ----------
@circulars_bp.route('/', methods=['POST'])
@token_required(roles=['faculty', 'admin'])
def post_circular():
    """
    Endpoint for faculty or admin to create a new circular.
    Requires title, content, audience. Optional dept_code if audience is 'specific_dept'.
    """
    data = request.json
    user_id = request.user['user_id']
    user_role = request.user['role']

    title = data.get('title')
    content = data.get('content')
    audience = data.get('audience')
    dept_code = data.get('dept_code') # Optional

    if not all([title, content, audience]):
        return jsonify({"success": False, "error": "Missing required fields: title, content, audience."}), 400

    if audience not in VALID_AUDIENCES:
        return jsonify({"success": False, "error": f"Invalid audience type. Must be one of: {', '.join(VALID_AUDIENCES)}"}), 400

    faculty_id = None
    if user_role == 'faculty':
        faculty_id = CircularsModel.get_faculty_id_from_user_id(user_id)
        if not faculty_id:
            return jsonify({"success": False, "error": "Faculty record not found for the authenticated user."}), 403
    # If admin is posting, faculty_id remains NULL in DB as per schema (or you can assign a default admin faculty_id)
    # Your schema states faculty_id INT NULL, so we can pass None if an admin posts.
    
    dept_id = None
    if audience == 'specific_dept':
        if not dept_code:
            return jsonify({"success": False, "error": "dept_code is required for 'specific_dept' audience."}), 400
        dept_ids_info = AttendanceModel._get_entity_ids(dept_code=dept_code)
        dept_id = dept_ids_info.get('dept_id')
        if not dept_id:
            return jsonify({"success": False, "error": f"Department with code '{dept_code}' not found."}), 404
    elif dept_code: # If dept_code is provided but audience is not specific_dept
        return jsonify({"success": False, "error": "dept_code is only valid when audience is 'specific_dept'."}), 400

    try:
        circular_id = CircularsModel.create_circular(faculty_id, title, content, audience, dept_id)
        return jsonify({"success": True, "message": "Circular posted successfully.", "circular_id": circular_id}), 201
    except Exception as e:
        print(f"Error posting circular: {e}")
        return jsonify({"success": False, "error": "Internal server error while posting circular."}), 500

# ---------- All Users: Get Circulars Relevant to Them ----------
@circulars_bp.route('/', methods=['GET'])
@token_required(roles=['student', 'faculty', 'admin'])
def get_my_circulars():
    """
    Endpoint for any authenticated user to fetch circulars relevant to them.
    Filters by user role and department.
    """
    user_id = request.user['user_id']
    user_role = request.user['role']

    try:
        circulars = CircularsModel.get_circulars_for_user(user_id, user_role)
        return jsonify({"success": True, "circulars": circulars}), 200
    except Exception as e:
        print(f"Error fetching circulars for user {user_id} ({user_role}): {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching circulars."}), 500

# ---------- All Users: Get a Single Circular by ID ----------
@circulars_bp.route('/<int:circular_id>', methods=['GET'])
@token_required(roles=['student', 'faculty', 'admin'])
def get_single_circular(circular_id):
    """
    Endpoint to retrieve details of a specific circular by ID.
    Access control for content might be handled on the frontend based on audience/role,
    or a more robust check could be added here.
    """
    try:
        circular = CircularsModel.get_circular_by_id(circular_id)
        if not circular:
            return jsonify({"success": False, "error": "Circular not found."}), 404
        # Additional check could be added here to ensure the user is authorized to view this specific circular
        # based on its audience, if the frontend is not trusted. For a prototype, the general get_my_circulars
        # endpoint provides the list, and getting a single one by ID assumes it was already filtered.
        return jsonify({"success": True, "circular": circular}), 200
    except Exception as e:
        print(f"Error fetching circular {circular_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500

# ---------- Faculty/Admin: Update Circular ----------
@circulars_bp.route('/<int:circular_id>', methods=['PUT'])
@token_required(roles=['faculty', 'admin'])
def update_circular(circular_id):
    """
    Endpoint for faculty or admin to update an existing circular.
    Requires title, content, audience. Optional dept_code if audience is 'specific_dept'.
    A faculty can only update their own circulars. Admin can update any.
    """
    data = request.json
    user_id = request.user['user_id']
    user_role = request.user['role']

    title = data.get('title')
    content = data.get('content')
    audience = data.get('audience')
    dept_code = data.get('dept_code') # Optional

    if not all([title, content, audience]):
        return jsonify({"success": False, "error": "Missing required fields: title, content, audience."}), 400

    if audience not in VALID_AUDIENCES:
        return jsonify({"success": False, "error": f"Invalid audience type. Must be one of: {', '.join(VALID_AUDIENCES)}"}), 400
    
    # Authorization check: Fetch the existing circular to verify uploader
    existing_circular = CircularsModel.get_circular_by_id(circular_id)
    if not existing_circular:
        return jsonify({"success": False, "error": "Circular not found."}), 404

    if user_role == 'faculty':
        requesting_faculty_id = CircularsModel.get_faculty_id_from_user_id(user_id)
        if not requesting_faculty_id or requesting_faculty_id != existing_circular.get('faculty_id'):
            return jsonify({"success": False, "error": "Unauthorized: You can only update circulars you have posted."}), 403

    dept_id = None
    if audience == 'specific_dept':
        if not dept_code:
            return jsonify({"success": False, "error": "dept_code is required for 'specific_dept' audience."}), 400
        dept_ids_info = AttendanceModel._get_entity_ids(dept_code=dept_code)
        dept_id = dept_ids_info.get('dept_id')
        if not dept_id:
            return jsonify({"success": False, "error": f"Department with code '{dept_code}' not found."}), 404
    elif dept_code:
        return jsonify({"success": False, "error": "dept_code is only valid when audience is 'specific_dept'."}), 400

    try:
        updated = CircularsModel.update_circular(circular_id, title, content, audience, dept_id)
        if updated:
            return jsonify({"success": True, "message": "Circular updated successfully."}), 200
        else:
            return jsonify({"success": False, "error": "Circular not found or no changes made."}), 404
    except Exception as e:
        print(f"Error updating circular {circular_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error while updating circular."}), 500

# ---------- Faculty/Admin: Delete Circular ----------
@circulars_bp.route('/<int:circular_id>', methods=['DELETE'])
@token_required(roles=['faculty', 'admin'])
def delete_circular(circular_id):
    """
    Endpoint for faculty or admin to delete a circular.
    A faculty can only delete their own circulars. Admin can delete any.
    """
    user_id = request.user['user_id']
    user_role = request.user['role']

    # Authorization check
    existing_circular = CircularsModel.get_circular_by_id(circular_id)
    if not existing_circular:
        return jsonify({"success": False, "error": "Circular not found."}), 404

    if user_role == 'faculty':
        requesting_faculty_id = CircularsModel.get_faculty_id_from_user_id(user_id)
        if not requesting_faculty_id or requesting_faculty_id != existing_circular.get('faculty_id'):
            return jsonify({"success": False, "error": "Unauthorized: You can only delete circulars you have posted."}), 403

    try:
        deleted = CircularsModel.delete_circular(circular_id)
        if deleted:
            return jsonify({"success": True, "message": "Circular deleted successfully."}), 200
        else:
            return jsonify({"success": False, "error": "Circular not found in the database."}), 404
    except Exception as e:
        print(f"Error deleting circular {circular_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error while deleting circular."}), 500

# ---------- Faculty/Admin Dashboard: Get Recent Announcements (for compose screen) ----------
@circulars_bp.route('/recent', methods=['GET'])
@token_required(roles=['faculty', 'admin'])
def get_recent_announcements():
    """
    Endpoint to fetch a list of recent circulars, for display on the faculty/admin dashboard
    where new circulars are composed.
    """
    try:
        recent_circulars = CircularsModel.get_recent_circulars(limit=5) # Default limit of 5
        return jsonify({"success": True, "recent_circulars": recent_circulars}), 200
    except Exception as e:
        print(f"Error fetching recent announcements: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500