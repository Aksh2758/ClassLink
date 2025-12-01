# backend/routes/circulars_routes.py
import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory # Import send_from_directory
from utils.jwt_utils import token_required
from models.circulars_model import CircularsModel
from models.attendance_model import AttendanceModel 
from utils.fileupload_utils import allowed_file, save_uploaded_file, delete_file_from_server # Import new utils
from routes.notification_routes import emit_notification_to_user 
from models.timetable_model import get_department_id_by_code

circulars_bp = Blueprint('circulars', __name__, url_prefix='/api/circulars')

VALID_AUDIENCES = {'all', 'students', 'faculty', 'specific_dept'}

# Define allowed extensions specifically for circulars
ALLOWED_CIRCULAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
CIRCULAR_ATTACHMENT_SUBFOLDER = 'circular_attachments' # Subfolder for circulars within the main UPLOAD_FOLDER

# The allowed_file function from utils now takes `allowed_extensions` as an argument

# No need for UPLOAD_FOLDER or os.makedirs here anymore, handled by app.py and save_uploaded_file

# ---------- Faculty/Admin: Create New Circular ----------
@circulars_bp.route('/upload', methods=['POST'])
@token_required(roles=['faculty', 'admin'])
def post_circular():
    title = request.form.get('title')
    content = request.form.get('content')
    audience = request.form.get('audience')
    dept_code = request.form.get('dept_code')
    
    file = request.files.get('attachment')

    user_id = request.user['user_id']
    user_role = request.user['role']

    if not all([title, content, audience]):
        return jsonify({"success": False, "error": "Missing required fields: title, content, audience."}), 400

    if audience not in VALID_AUDIENCES:
        return jsonify({"success": False, "error": f"Invalid audience type. Must be one of: {', '.join(VALID_AUDIENCES)}"}), 400

    # --- Handle File Upload using utility ---
    attachment_path = None
    if file and file.filename != '':
        if not allowed_file(file.filename, ALLOWED_CIRCULAR_EXTENSIONS): # Use utility function
            return jsonify({"success": False, "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_CIRCULAR_EXTENSIONS)}"}), 400
        
        attachment_path = save_uploaded_file(file, CIRCULAR_ATTACHMENT_SUBFOLDER, user_id)
        if not attachment_path:
            return jsonify({"success": False, "error": "Failed to save the uploaded attachment."}), 500

    faculty_id = None
    if user_role == 'faculty':
        faculty_id = CircularsModel.get_faculty_id_from_user_id(user_id)
        if not faculty_id:
            if attachment_path: delete_file_from_server(attachment_path)
            return jsonify({"success": False, "error": "Faculty record not found for the authenticated user."}), 403
    
    dept_id = None
    if audience == 'specific_dept':
        if not dept_code:
            if attachment_path: delete_file_from_server(attachment_path)
            return jsonify({"success": False, "error": "dept_code is required for 'specific_dept' audience."}), 400
        dept_ids_info = AttendanceModel._get_entity_ids(dept_code=dept_code)
        dept_id = dept_ids_info.get('dept_id')
        if not dept_id:
            if attachment_path: delete_file_from_server(attachment_path)
            return jsonify({"success": False, "error": f"Department with code '{dept_code}' not found."}), 404
    elif dept_code:
            if attachment_path: delete_file_from_server(attachment_path)
            return jsonify({"success": False, "error": "dept_code is only valid when audience is 'specific_dept'."}), 400

    try:
        circular_id = CircularsModel.create_circular(faculty_id, title, content, audience, dept_id, attachment_path)
        if circular_id:
            target_user_ids = []
            notification_message = f"New Circular: {title}"

            if audience == 'all':
                target_user_ids.extend(CircularsModel.get_all_student_user_ids())
                target_user_ids.extend(CircularsModel.get_all_faculty_user_ids())
            elif audience == 'students':
                target_user_ids.extend(CircularsModel.get_all_student_user_ids())
            elif audience == 'faculty':
                target_user_ids.extend(CircularsModel.get_all_faculty_user_ids())
            elif audience == 'specific_dept' and dept_id:
                target_user_ids.extend(CircularsModel.get_student_user_ids_by_department(dept_id))
                target_user_ids.extend(CircularsModel.get_faculty_user_ids_by_department(dept_id))
            
            # Remove duplicates if any (e.g., if a user is faculty and also a student - though unlikely in this system)
            target_user_ids = list(set(target_user_ids))

            for target_uid in target_user_ids:
                emit_notification_to_user(
                    user_id=target_uid,
                    notification_data={
                        "user_id": target_uid,
                        "type": "new_circular",
                        "message": notification_message,
                        "related_id": circular_id # Link to the new circular
                    }
                )
        return jsonify({"success": True, "message": "Circular posted successfully.", "circular_id": circular_id}), 201
    except Exception as e:
        print(f"Error posting circular: {e}")
        if attachment_path:
            delete_file_from_server(attachment_path)
        return jsonify({"success": False, "error": "Internal server error while posting circular."}), 500

@circulars_bp.route('/', methods=['GET'])
@token_required(roles=['student', 'faculty', 'admin'])
def get_my_circulars():
    user_id = request.user['user_id']
    user_role = request.user['role']

    try:
        circulars = CircularsModel.get_circulars_for_user(user_id, user_role)
        return jsonify({"success": True, "circulars": circulars}), 200
    except Exception as e:
        print(f"Error fetching circulars for user {user_id} ({user_role}): {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching circulars."}), 500

@circulars_bp.route('/<int:circular_id>', methods=['GET'])
@token_required(roles=['student', 'faculty', 'admin'])
def get_single_circular(circular_id):
    try:
        circular = CircularsModel.get_circular_by_id(circular_id)
        if not circular:
            return jsonify({"success": False, "error": "Circular not found."}), 404
        return jsonify({"success": True, "circular": circular}), 200
    except Exception as e:
        print(f"Error fetching circular {circular_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500

@circulars_bp.route('/<int:circular_id>', methods=['PUT'])
@token_required(roles=['faculty', 'admin'])
def update_circular(circular_id):
    title = request.form.get('title')
    content = request.form.get('content')
    audience = request.form.get('audience')
    dept_code = request.form.get('dept_code')
    
    file = request.files.get('attachment')
    delete_existing_attachment_flag = request.form.get('delete_attachment', 'false').lower() == 'true'

    user_id = request.user['user_id']
    user_role = request.user['role']

    if not all([title, content, audience]):
        return jsonify({"success": False, "error": "Missing required fields: title, content, audience."}), 400

    if audience not in VALID_AUDIENCES:
        return jsonify({"success": False, "error": f"Invalid audience type. Must be one of: {', '.join(VALID_AUDIENCES)}"}), 400
    
    existing_circular = CircularsModel.get_circular_by_id(circular_id)
    if not existing_circular:
        return jsonify({"success": False, "error": "Circular not found."}), 404

    if user_role == 'faculty':
        requesting_faculty_id = CircularsModel.get_faculty_id_from_user_id(user_id)
        if not requesting_faculty_id or requesting_faculty_id != existing_circular.get('faculty_id'):
            return jsonify({"success": False, "error": "Unauthorized: You can only update circulars you have posted."}), 403

    # --- Handle File Update/Deletion using utilities ---
    current_attachment_path = existing_circular.get('attachment_path')
    new_attachment_path = current_attachment_path # Assume no change by default
    
    file_to_cleanup_if_error = None # Track newly uploaded file for cleanup

    if delete_existing_attachment_flag and current_attachment_path:
        delete_file_from_server(current_attachment_path)
        new_attachment_path = None # Set to None as it's deleted

    if file and file.filename != '':
        if not allowed_file(file.filename, ALLOWED_CIRCULAR_EXTENSIONS):
            return jsonify({"success": False, "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_CIRCULAR_EXTENSIONS)}"}), 400
        
        # If a new file is uploaded, and there was an old one, delete the old one first
        if current_attachment_path and not delete_existing_attachment_flag: # If not explicitly deleted above
            delete_file_from_server(current_attachment_path)
        
        new_attachment_path = save_uploaded_file(file, CIRCULAR_ATTACHMENT_SUBFOLDER, user_id)
        if not new_attachment_path:
            return jsonify({"success": False, "error": "Failed to save the new attachment."}), 500
        file_to_cleanup_if_error = new_attachment_path # Mark for potential cleanup

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
        updated = CircularsModel.update_circular(circular_id, title, content, audience, dept_id, new_attachment_path)
        if updated:
            target_user_ids = []
            notification_message = f"Circular Updated: {title}"

            if audience == 'all':
                target_user_ids.extend(CircularsModel.get_all_student_user_ids())
                target_user_ids.extend(CircularsModel.get_all_faculty_user_ids())
            elif audience == 'students':
                target_user_ids.extend(CircularsModel.get_all_student_user_ids())
            elif audience == 'faculty':
                target_user_ids.extend(CircularsModel.get_all_faculty_user_ids())
            elif audience == 'specific_dept' and dept_id:
                target_user_ids.extend(CircularsModel.get_student_user_ids_by_department(dept_id))
                target_user_ids.extend(CircularsModel.get_faculty_user_ids_by_department(dept_id))
            
            target_user_ids = list(set(target_user_ids))

            for target_uid in target_user_ids:
                emit_notification_to_user(
                    user_id=target_uid,
                    notification_data={
                        "user_id": target_uid,
                        "type": "circular_update", # New type for updates
                        "message": notification_message,
                        "related_id": circular_id
                    }
                )
            return jsonify({"success": True, "message": "Circular updated successfully."}), 200
        else:
            # If update didn't happen (e.g., circular_id not found), clean up new file
            if file_to_cleanup_if_error:
                delete_file_from_server(file_to_cleanup_if_error)
            return jsonify({"success": False, "error": "Circular not found or no changes made."}), 404
    except Exception as e:
        print(f"Error updating circular {circular_id}: {e}")
        # If an error occurred, clean up the newly uploaded file if any
        if file_to_cleanup_if_error:
            delete_file_from_server(file_to_cleanup_if_error)
        return jsonify({"success": False, "error": "Internal server error while updating circular."}), 500

@circulars_bp.route('/<int:circular_id>', methods=['DELETE'])
@token_required(roles=['faculty', 'admin'])
def delete_circular(circular_id):
    user_id = request.user['user_id']
    user_role = request.user['role']

    existing_circular = CircularsModel.get_circular_by_id(circular_id)
    if not existing_circular:
        return jsonify({"success": False, "error": "Circular not found."}), 404

    if user_role == 'faculty':
        requesting_faculty_id = CircularsModel.get_faculty_id_from_user_id(user_id)
        if not requesting_faculty_id or requesting_faculty_id != existing_circular.get('faculty_id'):
            return jsonify({"success": False, "error": "Unauthorized: You can only delete circulars you have posted."}), 403

    attachment_path_to_delete = existing_circular.get('attachment_path') # Get path before DB deletion

    try:
        deleted = CircularsModel.delete_circular(circular_id)
        if deleted:
            # --- Use the generic file deletion utility ---
            if attachment_path_to_delete:
                delete_file_from_server(attachment_path_to_delete)
            return jsonify({"success": True, "message": "Circular deleted successfully."}), 200
        else:
            return jsonify({"success": False, "error": "Circular not found in the database."}), 404
    except Exception as e:
        print(f"Error deleting circular {circular_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error while deleting circular."}), 500

@circulars_bp.route('/recent', methods=['GET'])
@token_required(roles=['faculty', 'admin'])
def get_recent_announcements():
    try:
        recent_circulars = CircularsModel.get_recent_circulars(limit=5)
        return jsonify({"success": True, "recent_circulars": recent_circulars}), 200
    except Exception as e:
        print(f"Error fetching recent announcements: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500
