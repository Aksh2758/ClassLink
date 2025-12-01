# backend/routes/notes_routes.py
from flask import Blueprint, request, jsonify, send_from_directory, current_app
import os
from utils.jwt_utils import token_required
from models.notes_model import NotesModel
from utils.db_connection import get_db_connection
from utils.fileupload_utils import allowed_file, save_uploaded_file, delete_file_from_server
from routes.notification_routes import emit_notification_to_user 

notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')

# Define allowed extensions specifically for notes
ALLOWED_NOTE_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt', 'zip'}
NOTE_SUBFOLDER = 'notes' # Subfolder for notes within the main UPLOAD_FOLDER

# The allowed_file function from utils now takes `allowed_extensions` as an argument

# ---------- Upload Note ----------
@notes_bp.route('/upload', methods=['POST'])
@token_required(roles=['faculty', 'admin'])
def upload_note():
    # request.user contains user_id, role, etc., from the JWT token
    faculty_user_id = request.user['user_id'] # This is the user_id from the token
    
    subject_code = request.form.get('subject_code')
    title = request.form.get('title')
    description = request.form.get('description', None)
    file = request.files.get('file')
    faculty_id_param = request.form.get('faculty_id')

    if not all([subject_code, title, file, faculty_id_param]):
        return jsonify({"success": False, "error": "Missing required fields (subject_code, title, file, faculty_id)."}), 400

    if not allowed_file(file.filename, ALLOWED_NOTE_EXTENSIONS):
        return jsonify({"success": False, "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_NOTE_EXTENSIONS)}"}), 400

    file_url_for_db = None
    note_id = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT dept_id FROM faculty_details WHERE faculty_id = %s", (faculty_id_param,))
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
        subject_name = subject_info['subject_name'] # Get subject name for notification
        
        offering_id_result = NotesModel.get_offering_id_for_faculty_upload(subject_id, faculty_dept_id)
        
        if not offering_id_result:
            return jsonify({"success": False, "error": f"No active subject offering found for '{subject_code}' in your department. Please contact admin to set up the offering."}), 404
        
        offering_id = offering_id_result
        
        file_url_for_db = save_uploaded_file(file, NOTE_SUBFOLDER, faculty_user_id)
        if not file_url_for_db:
             return jsonify({"success": False, "error": "Failed to save the uploaded file."}), 500

        note_id = NotesModel.upload_new_note(offering_id, faculty_id_param, title, description, file_url_for_db)

        # --- SOCKET.IO NOTIFICATION INTEGRATION ---
        # 1. Get student IDs associated with this offering_id
        if note_id:
            # 1. Get student IDs associated with this offering_id
            student_user_ids = NotesModel.get_student_user_ids_for_offering(offering_id)
            
            # 2. Construct the notification message
            notification_message = f"New note '{title}' uploaded for {subject_name} ({subject_code})!"
            
            # 3. Emit notification to each student
            for student_uid in student_user_ids:
                emit_notification_to_user(
                    user_id=student_uid,
                    notification_data={
                        "user_id": student_uid, # Target user
                        "type": "new_note",
                        "message": notification_message,
                        "related_id": note_id # Link to the new note
                    }
                )
        
        return jsonify({
            "success": True,
            "message": "Note uploaded successfully",
            "note_id": note_id,
            "file_url": file_url_for_db
        }), 201

    except Exception as e:
        print(f"Error uploading note: {e}")
        if file_url_for_db:
            delete_file_from_server(file_url_for_db)
        return jsonify({"success": False, "error": "Internal server error while uploading note."}), 500

# ---------- Get Notes (Filtered by student or offering) ----------
@notes_bp.route('/', methods=['GET'])
@token_required(roles=['student', 'faculty', 'admin'])
def get_notes():
    user_role = request.user['role']
    user_id = request.user['user_id']

    offering_id_str = request.args.get('offering_id')
    notes_data = []

    try:
        if user_role == 'student':
            # This is correct: a student should only see notes for subjects they are enrolled in
            notes_data = NotesModel.get_notes_by_filter(student_user_id=user_id)
        else: # Faculty or Admin
            if offering_id_str:
                try:
                    offering_id = int(offering_id_str)
                    notes_data = NotesModel.get_notes_by_filter(offering_id=offering_id)
                except ValueError:
                    return jsonify({"success": False, "error": "'offering_id' must be an integer if provided."}), 400
            else:
                if user_role == 'faculty':
                    faculty_db_id = NotesModel.get_faculty_id_from_user_id(user_id)
                    notes_data = NotesModel.get_notes_by_filter(faculty_id=faculty_db_id)
                else: # Admin
                    notes_data = NotesModel.get_notes_by_filter()
                
        return jsonify({"success": True, "notes": notes_data}), 200

    except Exception as e:
        print(f"Error fetching notes: {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching notes."}), 500

# ---------- Download Note (Actual File Serving) ----------
@notes_bp.route('/download/<int:note_id>', methods=['GET'])
@token_required(roles=['student', 'faculty', 'admin'])
def download_note(note_id):
    try:
        file_url_from_db = NotesModel.get_note_file_url(note_id)
        if not file_url_from_db:
            return jsonify({"success": False, "error": "Note not found."}), 404

        path_segments = file_url_from_db.split('/')
        if len(path_segments) >= 3 and path_segments[1] == 'uploads':
            subfolder = path_segments[2]
            filename = path_segments[-1]
            directory_to_serve_from = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)

            return send_from_directory(
                directory=directory_to_serve_from,
                path=filename,
                as_attachment=True
            )
        else:
            return jsonify({"success": False, "error": "Invalid file path stored for note."}), 500

    except Exception as e:
        print(f"Error downloading note: {e}")
        return jsonify({"success": False, "error": "Internal server error while downloading note."}), 500


# ---------- Delete Note ----------
@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@token_required(roles=['faculty', 'admin'])
def delete_note(note_id):
    user_id = request.user['user_id']
    user_role = request.user['role']

    file_url_to_delete = None

    try:
        file_url_to_delete = NotesModel.get_note_file_url(note_id)
        if not file_url_to_delete:
            return jsonify({"success": False, "error": "Note not found."}), 404

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT faculty_id FROM notes WHERE note_id = %s", (note_id,))
        uploader_faculty_record = cursor.fetchone()
        cursor.close()
           
        if uploader_faculty_record:
            uploader_faculty_id = uploader_faculty_record['faculty_id']
            requesting_faculty_id = NotesModel.get_faculty_id_from_user_id(user_id)
            
            if user_role == 'faculty' and requesting_faculty_id != uploader_faculty_id:
                conn.close() # Close here if unauthorized
                return jsonify({"success": False, "error": "Unauthorized: You can only delete notes you have uploaded."}), 403
        elif user_role == 'faculty':
             conn.close() # Close here if note not found for faculty
             return jsonify({"success": False, "error": "Note not found or you are not authorized."}), 403

        deleted_from_db = NotesModel.delete_note_by_id(note_id)

        if deleted_from_db:
            delete_file_from_server(file_url_to_delete)
            conn.close() # Close connection after successful DB operations
            return jsonify({"success": True, "message": "Note deleted successfully."}), 200
        else:
            conn.close() # Close connection if note not found for deletion
            return jsonify({"success": False, "error": "Note not found in the database."}), 404

    except Exception as e:
        print(f"Error deleting note: {e}")
        # Ensure connection is closed even on error
        if 'conn' in locals() and conn:
            conn.close()
        return jsonify({"success": False, "error": "Internal server error while deleting note."}), 500