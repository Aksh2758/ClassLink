# backend/routes/attendance_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_utils import token_required # Ensure this is the updated token_required that accepts roles
from models.attendance_model import AttendanceModel
from models.timetable_model import get_student_department_semester_section # Reusing existing helper
from datetime import datetime
from utils.db_connection import get_db_connection

attendance_bp = Blueprint("attendance", __name__, url_prefix="/api/attendance") # Changed blueprint name to 'attendance' and added url_prefix

# Helper function to convert date string to date object
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

@attendance_bp.route('/', methods=['POST'])
@token_required(roles=['faculty', 'admin']) # Only faculty or admin can submit attendance
def submit_class_attendance():
    """
    Endpoint for faculty to submit attendance for a specific class session.
    Expects data for one class session and a list of student statuses.
    """
    data = request.json
    faculty_user_id = request.user['user_id']

    required_fields = ["date", "period_number", "dept_code", "semester",
                       "subject_code", "section", "attendance_list"]

    if not all(k in data for k in required_fields):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    date_str = data["date"]
    period_number = data["period_number"]
    dept_code = data["dept_code"]
    semester = data["semester"]
    subject_code = data["subject_code"]
    section = data["section"]
    attendance_list = data["attendance_list"] # List of {'student_id': <int>, 'status': 'present'/'absent'}

    if not isinstance(attendance_list, list) or not attendance_list:
        return jsonify({"success": False, "error": "'attendance_list' must be a non-empty list"}), 400

    if not parse_date(date_str):
        return jsonify({"success": False, "error": "Invalid date format. Expected YYYY-MM-DD"}), 400
    if not isinstance(period_number, int):
        return jsonify({"success": False, "error": "'period_number' must be an integer"}), 400
    if not isinstance(semester, int):
        return jsonify({"success": False, "error": "'semester' must be an integer"}), 400

    try:
        # 1. Get assignment_id from the class details
        # This function might need to be created or adapted from timetable_model if it doesn't exist
        # For simplicity, we'll try to get the class_session_id directly.
        
        # We need to find the assignment_id first to then potentially create the class_session
        ids = AttendanceModel._get_entity_ids(
            dept_code=dept_code,
            subject_code=subject_code,
            faculty_user_id=faculty_user_id
        )
        if not all(k in ids for k in ['dept_id', 'subject_id', 'faculty_id']):
            return jsonify({"success": False, "error": "Department, Subject, or Faculty not found for the given details."}), 404

        dept_id = ids['dept_id']
        subject_id = ids['subject_id']
        faculty_id = ids['faculty_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT offering_id FROM subject_offerings WHERE subject_id = %s AND dept_id = %s AND semester = %s",
            (subject_id, dept_id, semester)
        )
        offering = cursor.fetchone()
        if not offering:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Subject offering not found for the given department and semester."}), 404
        offering_id = offering[0]

        cursor.execute(
            "SELECT assignment_id FROM faculty_assignment WHERE offering_id = %s AND faculty_id = %s AND section = %s",
            (offering_id, faculty_id, section)
        )
        assignment = cursor.fetchone()
        if not assignment:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Faculty assignment not found for the specified class."}), 404
        assignment_id = assignment[0]
        cursor.close()
        conn.close()


        # 2. Get or Create the class_session_id
        session_id = AttendanceModel.create_class_session_from_template(
            assignment_id=assignment_id,
            session_date_str=date_str,
            period_number=period_number
        )

        if not session_id:
            return jsonify({"success": False, "error": "Could not create or retrieve class session."}), 500

        # 3. Submit attendance for students in this session
        processed_count = AttendanceModel.submit_attendance_for_session(session_id, attendance_list)

        return jsonify({
            "success": True,
            "message": f"Attendance for session {session_id} saved/updated for {processed_count} students.",
            "session_id": session_id
        }), 201

    except Exception as e:
        print(f"Error submitting attendance: {e}")
        return jsonify({"success": False, "error": "Internal server error while submitting attendance."}), 500


@attendance_bp.route("/class/students", methods=["GET"])
@token_required(roles=['faculty', 'admin'])
def get_students_for_attendance_marking():
    """
    Endpoint for faculty to get a list of students for a specific class
    to easily mark attendance.
    Expects dept_code, semester, section as query parameters.
    """
    dept_code = request.args.get("dept_code")
    semester_str = request.args.get("semester")
    section = request.args.get("section")

    if not all([dept_code, semester_str, section]):
        return jsonify({"success": False, "error": "Missing dept_code, semester, or section query parameters."}), 400

    try:
        semester = int(semester_str)
    except ValueError:
        return jsonify({"success": False, "error": "'semester' must be an integer."}), 400

    try:
        ids = AttendanceModel._get_entity_ids(dept_code=dept_code)
        if 'dept_id' not in ids:
            return jsonify({"success": False, "error": "Department not found."}), 404
        dept_id = ids['dept_id']

        students = AttendanceModel.get_student_ids_for_section(dept_id, semester, section)
        if not students:
            return jsonify({"success": True, "message": "No students found for this class.", "students": []}), 200

        return jsonify({"success": True, "students": students}), 200
    except Exception as e:
        print(f"Error fetching students for attendance: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500


@attendance_bp.route("/class/history", methods=["GET"])
@token_required(roles=['faculty', 'admin']) # Faculty can view class attendance history
def get_class_attendance_history():
    """
    Endpoint to view the history of class sessions for a specific class.
    Query params: dept_code, semester, section, optional: subject_code, start_date, end_date
    """
    dept_code = request.args.get("dept_code")
    semester_str = request.args.get("semester")
    section = request.args.get("section")
    subject_code = request.args.get("subject_code") # Optional
    start_date_str = request.args.get("start_date") # Optional: YYYY-MM-DD
    end_date_str = request.args.get("end_date")     # Optional: YYYY-MM-DD

    if not all([dept_code, semester_str, section]):
        return jsonify({"success": False, "error": "Missing dept_code, semester, or section query parameters."}), 400

    try:
        semester = int(semester_str)
    except ValueError:
        return jsonify({"success": False, "error": "'semester' must be an integer."}), 400

    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)
    if start_date_str and not start_date:
        return jsonify({"success": False, "error": "Invalid start_date format. Expected YYYY-MM-DD"}), 400
    if end_date_str and not end_date:
        return jsonify({"success": False, "error": "Invalid end_date format. Expected YYYY-MM-DD"}), 400


    try:
        history = AttendanceModel.get_attendance_history_for_class(
            dept_code=dept_code,
            semester=semester,
            section=section,
            subject_code=subject_code,
            start_date=start_date,
            end_date=end_date
        )
        return jsonify({"success": True, "history": history}), 200
    except Exception as e:
        print(f"Error fetching class attendance history: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500


@attendance_bp.route("/session/<int:session_id>/details", methods=["GET"])
@token_required(roles=['faculty', 'admin', 'student']) # Students can view their attendance for a session too
def get_session_attendance_details(session_id):
    """
    Endpoint to get detailed attendance status for all students in a specific class session.
    """
    user_role = request.user['role']
    user_id = request.user['user_id']

    try:
        details = AttendanceModel.get_attendance_details_for_session(session_id)

        if not details:
            return jsonify({"success": True, "message": "No attendance details found for this session.", "details": []}), 200

        # If student is requesting, filter to show only their own attendance
        if user_role == 'student':
            student_ids_record = AttendanceModel._get_entity_ids(student_user_id=user_id)
            if 'student_id' not in student_ids_record:
                return jsonify({"success": False, "error": "Student ID not found for authenticated user."}), 403

            student_id = student_ids_record['student_id']
            filtered_details = [d for d in details if d['student_id'] == student_id]
            if not filtered_details:
                return jsonify({"success": True, "message": "No attendance found for you in this session.", "details": []}), 200
            
            return jsonify({"success": True, "details": filtered_details[0]}), 200 # A student only sees their own entry
        
        return jsonify({"success": True, "details": details}), 200
    except Exception as e:
        print(f"Error fetching session attendance details: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500


@attendance_bp.route("/update/<int:attendance_id>", methods=["PUT"])
@token_required(roles=['faculty', 'admin']) # Only faculty or admin can update attendance status
def update_single_attendance_entry(attendance_id):
    """
    Endpoint to update the status of a single student's attendance record (identified by attendance_id).
    """
    data = request.json
    new_status = data.get("status")

    if not new_status or new_status not in ['present', 'absent']:
        return jsonify({"success": False, "error": "Missing or invalid 'status'. Must be 'present' or 'absent'."}), 400

    try:
        updated = AttendanceModel.update_single_attendance_status(attendance_id, new_status)
        if updated:
            return jsonify({"success": True, "message": "Attendance record updated successfully."}), 200
        else:
            return jsonify({"success": False, "message": "Attendance record not found or no change made."}), 404
    except Exception as e:
        print(f"Error updating single attendance record: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500


@attendance_bp.route("/student/my-attendance", methods=["GET"])
@token_required(roles=['student'])
def get_my_overall_attendance():
    """
    Endpoint for a student to view their overall attendance across all subjects.
    """
    student_user_id = request.user['user_id']

    try:
        overall_attendance = AttendanceModel.get_student_overall_attendance(student_user_id)
        if not overall_attendance:
            return jsonify({"success": True, "message": "No attendance data found for this student.", "attendance": []}), 200
        
        return jsonify({"success": True, "attendance": overall_attendance}), 200
    except Exception as e:
        print(f"Error fetching overall student attendance for user {student_user_id}: {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching attendance."}), 500