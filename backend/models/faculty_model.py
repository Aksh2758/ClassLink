# backend/models/faculty_model.py
from utils.db_connection import get_db_connection

class FacultyModel:
    @staticmethod
    def get_faculty_by_user_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Select all fields from faculty_details
        cursor.execute(
            """
            SELECT fd.*, d.dept_name, d.dept_code, u.email
            FROM faculty_details fd
            JOIN departments d ON fd.dept_id = d.dept_id
            JOIN users u ON fd.user_id = u.id
            WHERE fd.user_id = %s
            """,
            (user_id,)
        )
        faculty = cursor.fetchone()
        cursor.close()
        conn.close()
        return faculty
