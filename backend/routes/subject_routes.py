# backend/routes/subject_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_utils import token_required # Assuming you want to protect this endpoint
from utils.db_connection import get_db_connection

subject_bp = Blueprint("subjects", __name__, url_prefix="/api/subjects")

@subject_bp.route("/by-dept-semester", methods=["GET"])
@token_required(roles=['faculty', 'admin']) # Protect this endpoint, only faculty/admin can likely fetch subjects like this
def get_subjects_by_dept_semester():
    """
    Endpoint to fetch subjects offered by a specific department and semester.
    Query params: dept_code, semester
    """
    dept_code = request.args.get("dept_code")
    semester_str = request.args.get("semester")

    if not all([dept_code, semester_str]):
        return jsonify({"success": False, "error": "Missing dept_code or semester query parameters."}), 400

    try:
        semester = int(semester_str)
    except ValueError:
        return jsonify({"success": False, "error": "'semester' must be an integer."}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # First, get dept_id
        cursor.execute("SELECT dept_id FROM departments WHERE dept_code = %s", (dept_code,))
        dept = cursor.fetchone()
        if not dept:
            return jsonify({"success": False, "error": "Department not found."}), 404
        dept_id = dept['dept_id']

        # Then, fetch subjects based on dept_id and semester via subject_offerings
        query = """
        SELECT
            s.subject_id,
            s.subject_code,
            s.subject_name
        FROM
            subjects s
        JOIN
            subject_offerings so ON s.subject_id = so.subject_id
        WHERE
            so.dept_id = %s AND so.semester = %s
        ORDER BY s.subject_name
        """
        cursor.execute(query, (dept_id, semester))
        subjects = cursor.fetchall()

        return jsonify({"success": True, "subjects": subjects}), 200

    except Exception as e:
        print(f"Error fetching subjects by department and semester: {e}")
        return jsonify({"success": False, "error": "Internal server error."}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()