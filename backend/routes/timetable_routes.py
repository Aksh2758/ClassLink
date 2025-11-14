# backend/routes/timetable_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_utils import token_required # Import the new middleware
from models.timetable_model import (
    save_timetable_entry,
    get_timetable_for_class,
    get_student_department_semester_section
)

timetable_bp = Blueprint("timetable", __name__, url_prefix="/api/timetable")

@timetable_bp.route("/faculty/save", methods=["POST"]) # Changed route name for clarity
@token_required(roles=['faculty', 'admin']) # Only faculty or admin can save timetables
def save_timetable():
    data = request.json
    semester = data.get("semester")
    department_name = data.get("department_name") # Changed to department_name for clarity
    department_code = data.get("department_code") # Added department_code for new dept creation
    section = data.get("section")
    entries = data.get("entries")

    if semester is None or not isinstance(semester, int):
        return jsonify({"success": False, "error": "'semester' must be an integer"}), 400
    if not department_name:
        return jsonify({"success": False, "error": "Missing 'department_name' in request"}), 400
    if not department_code:
        return jsonify({"success": False, "error": "Missing 'department_code' in request. Required for department lookup/creation."}), 400
    if not entries or not isinstance(entries, list):
        return jsonify({"success": False, "error": "Missing or invalid 'entries' data in request"}), 400
    
    # Ensure the user making the request is a faculty member whose faculty_id is passed,
    # or that an admin is making the request and `faculty_id` is correct.
    # For now, we assume the `faculty_id` in each entry is valid and passed correctly.
    # In a real app, you might check if request.user['user_id'] matches the faculty_id,
    # or if the user is an admin allowed to assign any faculty.

    processed_count = 0
    errors = []

    for e in entries:
        if not all(k in e for k in ["day", "period", "subject_code", "subject_name", "faculty_id"]): # Added subject_name
            errors.append(f"Invalid entry found: {e}. Missing 'day', 'period', 'subject_code', 'subject_name', or 'faculty_id'.")
            continue
        
        # Further type validation for individual fields
        if not isinstance(e["day"], str) or not e["day"]:
            errors.append(f"Invalid 'day' in entry: {e}. Must be a non-empty string.")
            continue
        if not isinstance(e["period"], int):
            errors.append(f"Invalid 'period' in entry: {e}. Must be an integer.")
            continue
        if not isinstance(e["subject_code"], str):
            errors.append(f"Invalid 'subject_code' in entry: {e}. Must be a string.")
            continue
        if not isinstance(e["subject_name"], str): # Validate subject_name
            errors.append(f"Invalid 'subject_name' in entry: {e}. Must be a string.")
            continue
        if not e["faculty_id"]:
             errors.append(f"Invalid 'faculty_id' in entry: {e}. Must be a non-empty value for an assignment.")
             continue

        try:
            save_timetable_entry(
                semester=semester,
                department_name=department_name,
                department_code=department_code, # Pass department_code
                section=section,
                day_of_week=e["day"],
                period_number=e["period"],
                subject_code=e["subject_code"],
                subject_name=e["subject_name"], # Pass subject_name
                faculty_id=e["faculty_id"]
            )
            processed_count += 1
        except Exception as db_err:
            errors.append(f"Database error for entry {e}: {db_err}")
            print(f"Database error saving timetable entry: {db_err}")

    if errors:
        if processed_count > 0:
            return jsonify({
                "success": True, # Still partially successful
                "message": f"Timetable partially saved. {processed_count} entries processed. Errors occurred for {len(errors)} entries.",
                "errors": errors
            }), 206 # Partial Content
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save any timetable entries.",
                "details": errors
            }), 400

    return jsonify({"success": True, "message": "Timetable saved successfully", "processed_entries": processed_count}), 200

@timetable_bp.route("/student", methods=["GET"]) # Removed student_id from URL
@token_required(roles=['student']) # Only authenticated students can view their timetable
def get_student_timetable():
    user_id = request.user['user_id'] # Get user_id from the authenticated token

    try:
        # Get student's academic details using their user_id
        student_details = get_student_department_semester_section(user_id)

        if not student_details:
            return jsonify({"success": False, "error": "Student details not found for this user."}), 404

        data = get_timetable_for_class(
            dept_name=student_details["dept_name"],
            semester=student_details["semester"],
            section=student_details.get("section")
        )
        return jsonify({"success": True, "timetable": data}), 200 # Wrapped in success object
    except Exception as e:
        print(f"Error fetching student timetable for user {user_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching student timetable."}), 500


@timetable_bp.route("/faculty/<int:semester>/<string:department_name>", defaults={'section': None}, methods=["GET"])
@timetable_bp.route("/faculty/<int:semester>/<string:department_name>/<string:section>", methods=["GET"])
@token_required(roles=['faculty', 'admin']) # Only faculty or admin can view faculty timetables
def get_faculty_timetable_by_class_semester(semester, department_name, section):
    user_id = request.user['user_id'] # Authenticated user
    user_role = request.user['role']

    try:
        # In a more granular system, you might check if this faculty_id matches the requested department.
        # For simplicity, if they are faculty or admin, they can query.
        data = get_timetable_for_class(department_name, semester, section)

        if not data:
            return jsonify({"success": True, "message": "No timetable found for this department, semester, and section"}), 200 # Return 200 with empty data
            # Or return 404 if "not found" is considered an error state. For timetable, empty list is often okay.

        return jsonify({"success": True, "timetable": data}), 200 # Wrapped in success object
    except Exception as e:
        print(f"Error fetching faculty timetable by department/semester/section for user {user_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching timetable."}), 500