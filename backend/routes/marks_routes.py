# backend/routes/marks_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_utils import token_required
from models.marks_model import MarksModel
from models.timetable_model import ( # Reusing helpers from timetable model
    get_subject_id_or_create,
    get_dept_id_or_create,
    get_offering_id_or_create
)
from models.attendance_model import AttendanceModel # For _get_entity_ids (faculty_id)

marks_bp = Blueprint('marks', __name__, url_prefix='/api/marks')

# ---------- Faculty: Get Students with Marks for a Class/Subject ----------
@marks_bp.route('/class-scores', methods=['GET'])
@token_required(roles=['faculty', 'admin'])
def get_class_scores_for_faculty():
    """
    Endpoint for faculty/admin to retrieve a list of students for a class/subject
    along with their current IA scores for display in the marks entry form.
    Query Params: dept_code, semester, section, subject_code
    """
    dept_code = request.args.get('dept_code')
    semester_str = request.args.get('semester')
    section = request.args.get('section')
    subject_code = request.args.get('subject_code')

    if not all([dept_code, semester_str, section, subject_code]):
        return jsonify({"success": False, "error": "Missing required query parameters: dept_code, semester, section, subject_code."}), 400

    try:
        semester = int(semester_str)
    except ValueError:
        return jsonify({"success": False, "error": "'semester' must be an integer."}), 400

    try:
        students_with_marks = MarksModel.get_students_for_class_with_marks(
            dept_code=dept_code,
            semester=semester,
            section=section,
            subject_code=subject_code
        )
        # Frontend expects IA1, IA2, IA3 keys, ensure they are present
        # Or, the frontend can handle potentially missing keys
        return jsonify({"success": True, "students": students_with_marks}), 200
    except Exception as e:
        print(f"Error fetching class scores for faculty: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500

# ---------- Faculty: Update Marks for a Class/Subject ----------
@marks_bp.route('/update', methods=['POST'])
@token_required(roles=['faculty', 'admin'])
def update_class_marks():
    """
    Endpoint for faculty/admin to update/submit IA marks for multiple students
    in a specific class and subject.
    Payload: {
        "dept_code": "CSE",
        "semester": 6,
        "subject_code": "CS601",
        "faculty_user_id": 123, # For verification, if needed, though token_required is primary
        "marks_entries": [
            {"student_id": 1, "ia_name": "IA1", "score": 25.5},
            {"student_id": 1, "ia_name": "IA2", "score": 20.0},
            {"student_id": 2, "ia_name": "IA1", "score": 22.0},
            {"student_id": 2, "ia_name": "IA3", "score": 18.0}
        ]
    }
    """
    data = request.json
    faculty_user_id_from_token = request.user['user_id'] # Authenticated faculty

    required_fields = ["dept_code", "semester", "subject_code", "marks_entries"]
    if not all(field in data for field in required_fields):
        return jsonify({"success": False, "error": "Missing required fields."}), 400

    dept_code = data["dept_code"]
    semester = data["semester"]
    subject_code = data["subject_code"]
    marks_entries = data["marks_entries"]

    if not isinstance(marks_entries, list):
        return jsonify({"success": False, "error": "'marks_entries' must be a list."}), 400

    try:
        # Verify faculty and get faculty_id (optional, token_required is primary, but good for logs)
        faculty_id = AttendanceModel._get_entity_ids(faculty_user_id=faculty_user_id_from_token).get('faculty_id')
        if not faculty_id:
            return jsonify({"success": False, "error": "Faculty record not found for the authenticated user."}), 403

        # Get offering_id
        dept_ids = AttendanceModel._get_entity_ids(dept_code=dept_code)
        dept_id = dept_ids.get('dept_id')
        subject_ids = AttendanceModel._get_entity_ids(subject_code=subject_code)
        subject_id = subject_ids.get('subject_id')

        if not dept_id or not subject_id:
            return jsonify({"success": False, "error": "Department or Subject not found."}), 404

        offering_id = get_offering_id_or_create(subject_id, dept_id, semester)
        if not offering_id:
            return jsonify({"success": False, "error": "Subject offering not found or could not be created."}), 500

        # Process each mark entry
        success_count = 0
        for entry in marks_entries:
            student_id = entry.get('student_id')
            ia_name = entry.get('ia_name')
            score = entry.get('score')

            if not all([student_id, ia_name, score is not None]): # score can be 0
                print(f"Skipping invalid mark entry: {entry}")
                continue
            
            if not isinstance(score, (int, float)) or not (0 <= score <= 100): # Assuming marks are out of 100 for now
                 print(f"Skipping invalid score for entry: {entry}")
                 continue

            ia_type_id = MarksModel.get_ia_type_id_or_create(ia_name)
            if ia_type_id:
                MarksModel.update_student_marks(offering_id, student_id, ia_type_id, score)
                success_count += 1
            else:
                print(f"Could not get/create IA type ID for '{ia_name}'")

        return jsonify({
            "success": True,
            "message": f"Successfully processed {success_count} mark entries.",
            "offering_id": offering_id
        }), 200

    except Exception as e:
        print(f"Error updating marks: {e}")
        return jsonify({"success": False, "error": "Internal server error while updating marks."}), 500

# ---------- Student: Get My Internal Assessment Scores ----------
@marks_bp.route('/my-scores', methods=['GET'])
@token_required(roles=['student'])
def get_my_ia_scores():
    """
    Endpoint for students to retrieve all their internal assessment scores.
    """
    student_user_id = request.user['user_id']

    try:
        ia_scores = MarksModel.get_student_all_ia_scores(student_user_id)
        if not ia_scores:
            return jsonify({"success": True, "message": "No internal assessment scores found for you.", "scores": []}), 200
        
        return jsonify({"success": True, "scores": ia_scores}), 200
    except Exception as e:
        print(f"Error fetching student IA scores: {e}")
        return jsonify({"success": False, "error": "Internal server error while fetching student scores."}), 500