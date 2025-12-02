# backend/routes/timetable_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_utils import token_required
from models.timetable_model import (
    save_timetable_entry,
    get_timetable_for_class,
    get_student_department_semester_section,
    #get_department_id_by_name, # <-- NEW: Import this helper
    get_department_id_by_code  # <-- NEW: Import this helper
)
from routes.notification_routes import emit_notification_to_user, get_students_in_department_and_semester 

timetable_bp = Blueprint("timetable", __name__, url_prefix="/api/timetable")

@timetable_bp.route("/faculty/save", methods=["POST"])
@token_required(roles=['faculty', 'admin'])
def save_timetable():
    data = request.json
    semester = data.get("semester")
    department_name = data.get("department_name")
    department_code = data.get("department_code")
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
    
    # --- Notification Logic Preparation ---
    # We need the dept_id to target students
    dept_id = get_department_id_by_code(department_code) # Assuming this function exists or will be created
    if not dept_id:
        print(f"Warning: Department with code '{department_code}' not found for notification targeting.")

    processed_count = 0
    errors = []

    for e in entries:
        if not all(k in e for k in ["day", "period", "subject_code", "subject_name", "faculty_id"]):
            errors.append(f"Invalid entry found: {e}. Missing 'day', 'period', 'subject_code', 'subject_name', or 'faculty_id'.")
            continue
        
        if not isinstance(e["day"], str) or not e["day"]:
            errors.append(f"Invalid 'day' in entry: {e}. Must be a non-empty string.")
            continue
        if not isinstance(e["period"], int):
            errors.append(f"Invalid 'period' in entry: {e}. Must be an integer.")
            continue
        if not isinstance(e["subject_code"], str):
            errors.append(f"Invalid 'subject_code' in entry: {e}. Must be a string.")
            continue
        if not isinstance(e["subject_name"], str):
            errors.append(f"Invalid 'subject_name' in entry: {e}. Must be a string.")
            continue
        if not e["faculty_id"]:
             errors.append(f"Invalid 'faculty_id' in entry: {e}. Must be a non-empty value for an assignment.")
             continue

        try:
            save_timetable_entry(
                semester=semester,
                department_name=department_name,
                department_code=department_code,
                section=section,
                day_of_week=e["day"],
                period_number=e["period"],
                subject_code=e["subject_code"],
                subject_name=e["subject_name"],
                faculty_id=e["faculty_id"]
            )
            processed_count += 1
        except Exception as db_err:
            errors.append(f"Database error for entry {e}: {db_err}")
            print(f"Database error saving timetable entry: {db_err}")

    # --- Emit Notification AFTER all entries are processed ---
    final_dept_id = get_department_id_by_code(department_code)
    if processed_count > 0 and final_dept_id:
        notification_message = f"Timetable for {department_name} (Semester {semester}, Section {section if section else 'All'}) has been updated."
        
        # Get all student user IDs for this department and semester
        student_user_ids = get_students_in_department_and_semester(final_dept_id, semester)
        
        for student_id in student_user_ids:
            emit_notification_to_user(
                user_id=student_id,
                notification_data={
                    "user_id": student_id,
                    "type": "timetable_update",
                    "message": notification_message,
                    "related_id": None
                }
            )
        print(f"Timetable update notification emitted to {len(student_user_ids)} students.")
    elif processed_count > 0 and not dept_id:
         print(f"Timetable saved but could not emit targeted notifications: Department {department_name} (code: {department_code}) not found.")


    if errors:
        if processed_count > 0:
            return jsonify({
                "success": True,
                "message": f"Timetable partially saved. {processed_count} entries processed. Errors occurred for {len(errors)} entries.",
                "errors": errors
            }), 206
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save any timetable entries.",
                "details": errors
            }), 400

    return jsonify({"success": True, "message": "Timetable saved successfully", "processed_entries": processed_count}), 200

@timetable_bp.route("/student", methods=["GET"])
@token_required(roles=['student'])
def get_student_timetable():
    user_id = request.user['user_id']

    try:
        student_details = get_student_department_semester_section(user_id)

        if not student_details:
            return jsonify({"success": False, "error": "Student details not found for this user."}), 404

        data = get_timetable_for_class(
            dept_name=student_details["dept_name"],
            semester=student_details["semester"],
            section=student_details.get("section")
        )
        return jsonify({"success": True, "timetable": data}), 200
    except Exception as e:
        print(f"Error fetching student timetable for user {user_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching student timetable."}), 500


@timetable_bp.route("/faculty/<int:semester>/<string:department_name>", defaults={'section': None}, methods=["GET"])
@timetable_bp.route("/faculty/<int:semester>/<string:department_name>/<string:section>", methods=["GET"])
@token_required(roles=['faculty', 'admin'])
def get_faculty_timetable_by_class_semester(semester, department_name, section):
    user_id = request.user['user_id']
    user_role = request.user['role']

    try:
        data = get_timetable_for_class(department_name, semester, section)

        if not data:
            return jsonify({"success": True, "message": "No timetable found for this department, semester, and section"}), 200
            
        return jsonify({"success": True, "timetable": data}), 200
    except Exception as e:
        print(f"Error fetching faculty timetable by department/semester/section for user {user_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching timetable."}), 500