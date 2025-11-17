from flask import Blueprint, request, jsonify, send_from_directory, current_app
import os
from werkzeug.utils import secure_filename
from utils.jwt_utils import token_required 
from models.notes_model import NotesModel
from utils.db_connection import get_db_connection
notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt', 'zip'} 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- Upload Note ----------
@notes_bp.route('/upload', methods=['POST'])
@token_required(roles=['faculty', 'admin']) 
def upload_note():
    faculty_user_id = request.user['user_id']

    # Data from form-data (now only minimum inputs)
    subject_code = request.form.get('subject_code')
    title = request.form.get('title')
    description = request.form.get('description', None)
    file = request.files.get('file')
    faculty_id=request.form.get('faculty_id')

    # Basic validation for the fields we expect
    if not all([subject_code, title, file, faculty_id]):
        return jsonify({"success": False, "error": "Missing required fields (subject_code, title, file)."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT dept_id FROM faculty_details WHERE faculty_id = %s", (faculty_id,))
        faculty_dept_result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not faculty_dept_result:
            return jsonify({"success": False, "error": "Faculty's department not found."}), 404
        faculty_dept_id = faculty_dept_result[0]

        subject_info = NotesModel.get_subject_details_by_code(subject_code.strip())
        if not subject_info:
            return jsonify({"success": False, "error": f"Subject with code '{subject_code}' not found."}), 404
        
        subject_id = subject_info['subject_id']
        subject_name = subject_info['subject_name']

        # 3. Infer the offering_id based on subject_id and faculty_dept_id
        offering_id_result = NotesModel.get_offering_id_for_faculty_upload(subject_id, faculty_dept_id)
        
        if not offering_id_result:
            return jsonify({"success": False, "error": f"No active subject offering found for '{subject_code}' in your department. Please contact admin to set up the offering."}), 404
        
        offering_id = offering_id_result 
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Store a relative URL or path
        file_url_for_db = os.path.join(current_app.static_url_path, filename).replace('\\', '/')

        # Insert the note record using the model
        note_id = NotesModel.upload_new_note(offering_id, faculty_id, title, description, file_url_for_db)

        return jsonify({
            "success": True,
            "message": "Note uploaded successfully",
            "note_id": note_id,
            "file_url": file_url_for_db
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