# backend/utils/file_upload_utils.py
import os
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename, allowed_extensions):
    """Checks if a file's extension is in the allowed set."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file_storage_object, subfolder, user_id=None):
    """
    Saves an uploaded file to a specific subfolder within the main UPLOAD_FOLDER.
    Returns the relative path (e.g., /uploads/subfolder/unique_filename.ext)
    or None if no file or invalid file.
    """
    if not file_storage_object or file_storage_object.filename == '':
        return None

    # Get the base UPLOAD_FOLDER from current_app config
    base_upload_path = current_app.config.get('UPLOAD_FOLDER')
    if not base_upload_path:
        raise Exception("UPLOAD_FOLDER not configured in Flask app.")

    # Define the specific folder for this type of upload
    target_upload_dir = os.path.join(base_upload_path, subfolder)
    os.makedirs(target_upload_dir, exist_ok=True) # Ensure directory exists

    filename = secure_filename(file_storage_object.filename)
    
    # Prepend a unique identifier to avoid name collisions
    unique_prefix = f"{user_id}_{os.urandom(8).hex()}" if user_id else os.urandom(8).hex()
    unique_filename = f"{unique_prefix}_{filename}"
    
    file_path_on_server = os.path.join(target_upload_dir, unique_filename)
    file_storage_object.save(file_path_on_server)

    # Return the relative URL path to be stored in the database
    # This path should be accessible via a static route
    # Assumes static_url_path is '/uploads'
    return os.path.join(current_app.static_url_path, subfolder, unique_filename).replace('\\', '/')

def delete_file_from_server(relative_file_path):
    """
    Deletes a file from the server given its relative path (as stored in DB).
    Returns True if deleted, False if not found or error.
    """
    if not relative_file_path:
        return False

    base_upload_path = current_app.config.get('UPLOAD_FOLDER')
    if not base_upload_path:
        print("Warning: UPLOAD_FOLDER not configured for file deletion.")
        return False

    # Construct the full path on the server's filesystem
    # relative_file_path might be like /uploads/circular_attachments/some_file.pdf
    # We need to remove the /uploads/ part to get the path relative to base_upload_path
    # or just reconstruct it from filename for simplicity given our current structure
    
    # A safer way: get just the filename and reconstruct with base_upload_path
    filename = os.path.basename(relative_file_path)
    # The actual physical path could be base_upload_path/subfolder/filename
    # We need to infer the subfolder from relative_file_path
    
    # Assuming relative_file_path is always /uploads/subfolder/filename
    # So we can extract 'subfolder' and 'filename' from it.
    parts = relative_file_path.split('/')
    if len(parts) >= 3 and parts[1] == 'uploads': # Check if it follows /uploads/subfolder/filename
        subfolder = parts[2]
        filename = parts[-1]
        full_file_path_on_server = os.path.join(base_upload_path, subfolder, filename)
        
        if os.path.exists(full_file_path_on_server):
            try:
                os.remove(full_file_path_on_server)
                print(f"File {full_file_path_on_server} removed from filesystem.")
                return True
            except OSError as e:
                print(f"Error deleting file {full_file_path_on_server}: {e}")
                return False
        else:
            print(f"Warning: File {full_file_path_on_server} not found on filesystem for deletion.")
            return False
    else:
        print(f"Error: Could not infer subfolder from relative_file_path for deletion: {relative_file_path}")
        return False