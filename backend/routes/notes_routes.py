# backend/routes/notes_routes.py
from flask import Blueprint, request, jsonify, send_from_directory, current_app
import os
from werkzeug.utils import secure_filename
from utils.jwt_utils import token_required # Ensure this accepts roles
from models.notes_model import NotesModel
from models.timetable_model import get_subject_id_or_create, get_dept_id_or_create, get_offering_id_or_create
from utils.db_connection import get_db_connection
notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')

# UPLOAD_FOLDER from app.py configuration
# current_app.config['UPLOAD_FOLDER'] is set in app.py from Config.UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt', 'zip'} # Added zip as common for study material

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- Upload Note ----------
@notes_bp.route('/upload', methods=['POST'])
@token_required(roles=['faculty', 'admin']) # Only faculty or admin can upload notes
def upload_note():
    # Retrieve faculty_user_id from the authenticated token
    faculty_user_id = request.user['user_id']

    # Data from form-data (for file uploads)
    subject_code = request.form.get('subject_code')
    subject_name = request.form.get('subject_name') # Added subject_name for consistency with timetable
    dept_code = request.form.get('dept_code')
    semester_str = request.form.get('semester')
    title = request.form.get('title')
    description = request.form.get('description', None)
    file = request.files.get('file')

    # Basic validation
    if not all([subject_code, subject_name, dept_code, semester_str, title, file]):
        return jsonify({"success": False, "error": "Missing required fields (subject_code, subject_name, dept_code, semester, title, file)."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    try:
        semester = int(semester_str)
    except ValueError:
        return jsonify({"success": False, "error": "'semester' must be an integer."}), 400

    try:
        # Get faculty_id from the authenticated user_id
        faculty_id = NotesModel.get_faculty_id_from_user_id(faculty_user_id)
        if not faculty_id:
            return jsonify({"success": False, "error": "Faculty record not found for the authenticated user."}), 404

        # Use timetable_model's helpers to ensure subject, department, and offering exist
        subject_id = get_subject_id_or_create(subject_code.strip(), subject_name.strip())
        if not subject_id:
            return jsonify({"success": False, "error": f"Could not find or create subject '{subject_name}'."}), 500

        dept_id = get_dept_id_or_create(dept_code.strip(), dept_code.strip()) # Assuming dept_name == dept_code for simplicity here
        if not dept_id:
            return jsonify({"success": False, "error": f"Could not find or create department '{dept_code}'."}), 500

        offering_id = get_offering_id_or_create(subject_id, dept_id, semester)
        if not offering_id:
            return jsonify({"success": False, "error": f"Could not find or create subject offering for {subject_code} in {dept_code} semester {semester}."}), 500

        # Secure filename and save the file
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Store a relative URL or path
        # Assuming the frontend will use the '/uploads' static route configured in app.py
        file_url_for_db = os.path.join(current_app.static_url_path, filename).replace('\\', '/')

        # Insert the note record using the model
        note_id = NotesModel.upload_new_note(offering_id, faculty_id, title, description, file_url_for_db)

        return jsonify({
            "success": True,
            "message": "Note uploaded successfully",
            "note_id": note_id,
            "file_url": file_url_for_db # Return the full path for immediate use
        }), 201

    except Exception as e:
        print(f"Error uploading note: {e}")
        return jsonify({"success": False, "error": "Internal server error while uploading note."}), 500

# ---------- Get Notes (Filtered by student or offering) ----------
@notes_bp.route('/', methods=['GET'])
@token_required(roles=['student', 'faculty', 'admin']) # All can view notes, potentially filtered
def get_notes():
    user_role = request.user['role']
    user_id = request.user['user_id']

    # Filters for faculty/admin
    offering_id_str = request.args.get('offering_id') # For faculty/admin to filter by specific offering
    
    # Logic for student to get their relevant notes (by their department/semester)
    notes_data = []

    try:
        if user_role == 'student':
            # Students get notes for their current department and semester
            notes_data = NotesModel.get_notes_by_filter(student_user_id=user_id)
        else: # Faculty or Admin
            if offering_id_str:
                try:
                    offering_id = int(offering_id_str)
                    notes_data = NotesModel.get_notes_by_filter(offering_id=offering_id)
                except ValueError:
                    return jsonify({"success": False, "error": "'offering_id' must be an integer if provided."}), 400
            else:
                # Faculty/Admin can view all notes if no specific filter
                notes_data = NotesModel.get_notes_by_filter() # Gets all if no filter is provided
                
        # The file_url stored in DB is already a public path via Flask's static route
        return jsonify({"success": True, "notes": notes_data}), 200

    except Exception as e:
        print(f"Error fetching notes: {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching notes."}), 500

# ---------- Download Note (Actual File Serving) ----------
@notes_bp.route('/download/<int:note_id>', methods=['GET'])
@token_required(roles=['student', 'faculty', 'admin']) # All roles can download notes
def download_note(note_id):
    try:
        file_url_from_db = NotesModel.get_note_file_url(note_id)
        if not file_url_from_db:
            return jsonify({"success": False, "error": "Note not found."}), 404

        # Extract filename from the stored file_url
        filename = os.path.basename(file_url_from_db)
        
        # The static_folder ('uploads') is already configured in app.py
        # We use send_from_directory to serve the file
        return send_from_directory(
            directory=current_app.config['UPLOAD_FOLDER'], # points to 'uploads'
            path=filename,
            as_attachment=True # Forces download
        )
    except Exception as e:
        print(f"Error downloading note: {e}")
        return jsonify({"success": False, "error": "Internal server error while downloading note."}), 500


# ---------- Delete Note ----------
@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@token_required(roles=['faculty', 'admin']) # Only faculty or admin can delete notes
def delete_note(note_id):
    user_id = request.user['user_id']
    user_role = request.user['role']

    try:
        # Get file_url before deleting the DB record
        file_url_to_delete = NotesModel.get_note_file_url(note_id)
        if not file_url_to_delete:
            return jsonify({"success": False, "error": "Note not found."}), 404

        # Additional security: Only the faculty who uploaded it, or an admin, can delete.
        # Fetch the faculty_id who uploaded this note
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT faculty_id FROM notes WHERE note_id = %s", (note_id,))
        uploader_faculty_record = cursor.fetchone()
        cursor.close()
        conn.close()

        if uploader_faculty_record:
            uploader_faculty_id = uploader_faculty_record['faculty_id']
            # Convert request.user['user_id'] to faculty_id for comparison
            requesting_faculty_id = NotesModel.get_faculty_id_from_user_id(user_id)
            
            if user_role == 'faculty' and requesting_faculty_id != uploader_faculty_id:
                return jsonify({"success": False, "error": "Unauthorized: You can only delete notes you have uploaded."}), 403
        elif user_role == 'faculty': # Note not found or faculty_id not in notes (unlikely)
             return jsonify({"success": False, "error": "Note not found or you are not authorized."}), 403


        # Delete from DB
        deleted_from_db = NotesModel.delete_note_by_id(note_id)

        if deleted_from_db:
            # Attempt to delete the file from the filesystem
            # We need to construct the full server path from the relative file_url_to_delete
            # The file_url_to_delete looks like /uploads/filename.ext
            base_upload_path = current_app.config['UPLOAD_FOLDER'] # This is 'uploads'
            filename_to_delete = os.path.basename(file_url_to_delete)
            full_file_path_on_server = os.path.join(base_upload_path, filename_to_delete)

            if os.path.exists(full_file_path_on_server):
                os.remove(full_file_path_on_server)
                print(f"File {full_file_path_on_server} removed from filesystem.")
            else:
                print(f"Warning: File {full_file_path_on_server} not found on filesystem, but DB record deleted.")

            return jsonify({"success": True, "message": "Note deleted successfully."}), 200
        else:
            return jsonify({"success": False, "error": "Note not found in the database."}), 404

    except Exception as e:
        print(f"Error deleting note: {e}")
        return jsonify({"success": False, "error": "Internal server error while deleting note."}), 500