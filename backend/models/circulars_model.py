# backend/models/circulars_model.py
from utils.db_connection import get_db_connection
from models.attendance_model import AttendanceModel 

class CircularsModel:
    @staticmethod
    def get_faculty_id_from_user_id(user_id):
        """Helper to get faculty_id from user_id."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT faculty_id FROM faculty_details WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error in get_faculty_id_from_user_id: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def create_circular(faculty_id, title, content, audience, dept_id=None, attachment_path=None):
        """
        Creates a new circular, including an optional attachment path.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO circulars (faculty_id, title, content, audience, dept_id, attachment_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (faculty_id, title, content, audience, dept_id, attachment_path))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error in create_circular: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_all_student_user_ids():
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM student_details")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting all student user IDs: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    @staticmethod
    def get_all_faculty_user_ids():
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM faculty_details")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting all faculty user IDs: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    @staticmethod
    def get_student_user_ids_by_department(dept_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM student_details WHERE dept_id = %s", (dept_id,))
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting student user IDs by department: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_faculty_user_ids_by_department(dept_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM faculty_details WHERE dept_id = %s", (dept_id,))
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting faculty user IDs by department: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    @staticmethod
    def get_circulars_for_user(user_id, role):
        """
        Fetches circulars relevant to a specific user, including attachment path.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT
                c.circular_id,
                c.title,
                c.content,
                c.posted_at,
                c.audience,
                d.dept_name,
                d.dept_code,
                fd.name AS posted_by_faculty,
                c.attachment_path # Include attachment path
            FROM
                circulars c
            LEFT JOIN
                departments d ON c.dept_id = d.dept_id
            LEFT JOIN
                faculty_details fd ON c.faculty_id = fd.faculty_id
            WHERE 1=1
            """
            params = []
            
            where_clauses = ["c.audience = 'all'"]

            if role == 'student':
                student_ids = AttendanceModel._get_entity_ids(student_user_id=user_id)
                student_dept_id = student_ids.get('student_dept_id')

                where_clauses.append("c.audience = 'students'")
                if student_dept_id:
                    where_clauses.append("(c.audience = 'specific_dept' AND c.dept_id = %s)")
                    params.append(student_dept_id)
            
            elif role == 'faculty':
                faculty_ids = AttendanceModel._get_entity_ids(faculty_user_id=user_id)
                faculty_dept_id = faculty_ids.get('dept_id')
                
                where_clauses.append("c.audience = 'faculty'")
                if faculty_dept_id:
                    where_clauses.append("(c.audience = 'specific_dept' AND c.dept_id = %s)")
                    params.append(faculty_dept_id)

            elif role == 'admin':
                where_clauses.append("c.audience IN ('students', 'faculty', 'specific_dept')")


            query += " AND (" + " OR ".join(where_clauses) + ")"
            query += " ORDER BY c.posted_at DESC"

            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error in get_circulars_for_user: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_circular_by_id(circular_id):
        """Fetches a single circular by its ID, including attachment path."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT
                c.circular_id,
                c.title,
                c.content,
                c.posted_at,
                c.audience,
                d.dept_name,
                d.dept_code,
                fd.name AS posted_by_faculty,
                c.faculty_id,
                c.attachment_path # Include attachment path
            FROM
                circulars c
            LEFT JOIN
                departments d ON c.dept_id = d.dept_id
            LEFT JOIN
                faculty_details fd ON c.faculty_id = fd.faculty_id
            WHERE c.circular_id = %s
            """
            cursor.execute(query, (circular_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error in get_circular_by_id: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update_circular(circular_id, title, content, audience, dept_id=None, attachment_path=None):
        """Updates an existing circular, including attachment path."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
            UPDATE circulars
            SET title = %s, content = %s, audience = %s, dept_id = %s, attachment_path = %s
            WHERE circular_id = %s
            """
            cursor.execute(query, (title, content, audience, dept_id, attachment_path, circular_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error in update_circular: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def delete_circular(circular_id):
        """Deletes a circular by its ID."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM circulars WHERE circular_id = %s", (circular_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error in delete_circular: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_recent_circulars(limit=5):
        """Fetches a limited number of most recent circulars, for general view, including attachment path."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT
                c.circular_id,
                c.title,
                c.posted_at,
                c.audience,
                d.dept_name,
                c.attachment_path # Include attachment path
            FROM circulars c
            LEFT JOIN departments d ON c.dept_id = d.dept_id
            ORDER BY c.posted_at DESC
            LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error in get_recent_circulars: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()