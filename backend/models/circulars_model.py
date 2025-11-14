# backend/models/circulars_model.py
from utils.db_connection import get_db_connection
from models.attendance_model import AttendanceModel # Reusing _get_entity_ids for faculty/student dept

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
    def create_circular(faculty_id, title, content, audience, dept_id=None):
        """
        Creates a new circular.
        dept_id is optional and only relevant if audience is 'specific_dept'.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO circulars (faculty_id, title, content, audience, dept_id)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (faculty_id, title, content, audience, dept_id))
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
    def get_circulars_for_user(user_id, role):
        """
        Fetches circulars relevant to a specific user based on their role and department.
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
                fd.name AS posted_by_faculty
            FROM
                circulars c
            LEFT JOIN
                departments d ON c.dept_id = d.dept_id
            LEFT JOIN
                faculty_details fd ON c.faculty_id = fd.faculty_id
            WHERE 1=1
            """
            params = []
            
            # Everyone sees 'all' circulars
            where_clauses = ["c.audience = 'all'"]

            if role == 'student':
                # Students also see circulars for 'students' and their specific department
                student_ids = AttendanceModel._get_entity_ids(student_user_id=user_id)
                student_dept_id = student_ids.get('student_dept_id')

                where_clauses.append("c.audience = 'students'")
                if student_dept_id:
                    where_clauses.append("(c.audience = 'specific_dept' AND c.dept_id = %s)")
                    params.append(student_dept_id)
            
            elif role == 'faculty':
                # Faculty also see circulars for 'faculty' and their specific department
                faculty_ids = AttendanceModel._get_entity_ids(faculty_user_id=user_id)
                faculty_dept_id = faculty_ids.get('dept_id') # Note: _get_entity_ids returns dept_id for faculty_user_id if department exists
                
                where_clauses.append("c.audience = 'faculty'")
                if faculty_dept_id:
                    where_clauses.append("(c.audience = 'specific_dept' AND c.dept_id = %s)")
                    params.append(faculty_dept_id)

            elif role == 'admin':
                # Admins see all circulars (no additional filtering beyond 'all' or explicit audience)
                # Admins essentially have permission to view everything posted regardless of audience targeting
                # If an admin posts a circular for 'students', an admin should still see it in their list
                # So we just ensure they see all specific audiences as well
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
        """Fetches a single circular by its ID."""
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
                c.faculty_id # Include original faculty_id for auth checks
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
    def update_circular(circular_id, title, content, audience, dept_id=None):
        """Updates an existing circular."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
            UPDATE circulars
            SET title = %s, content = %s, audience = %s, dept_id = %s
            WHERE circular_id = %s
            """
            cursor.execute(query, (title, content, audience, dept_id, circular_id))
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
        """Fetches a limited number of most recent circulars, for general view."""
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
                d.dept_name
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