# backend/models/notes_model.py
from utils.db_connection import get_db_connection
from datetime import datetime

class NotesModel:
    @staticmethod
    def get_faculty_id_from_user_id(user_id):
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
    def upload_new_note(offering_id, faculty_id, title, description, file_url):
        """
        Inserts a new note into the notes table.
        Uses offering_id to link to subject_offerings.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
            INSERT INTO notes (offering_id, faculty_id, title, description, file_url)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (offering_id, faculty_id, title, description, file_url))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error in upload_new_note: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_notes_by_filter(offering_id=None, student_user_id=None):
        """
        Fetches notes. Can filter by offering_id or by a student's enrolled subjects.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT
                n.note_id,
                n.title,
                n.description,
                n.file_url,
                n.uploaded_at,
                s.subject_code,
                s.subject_name,
                d.dept_code,
                d.dept_name,
                so.semester,
                fd.name AS faculty_name,
                u_faculty.email AS faculty_email
            FROM
                notes n
            JOIN
                subject_offerings so ON n.offering_id = so.offering_id
            JOIN
                subjects s ON so.subject_id = s.subject_id
            JOIN
                departments d ON so.dept_id = d.dept_id
            JOIN
                faculty_details fd ON n.faculty_id = fd.faculty_id
            JOIN
                users u_faculty ON fd.user_id = u_faculty.id
            """
            params = []
            where_clauses = []

            if offering_id:
                where_clauses.append("n.offering_id = %s")
                params.append(offering_id)
            elif student_user_id:
                # To get notes relevant to a student, we need their enrolled subject offerings
                # Find the student's dept_id, semester, and section
                cursor.execute(
                    "SELECT student_id, dept_id, semester, section FROM student_details WHERE user_id = %s",
                    (student_user_id,)
                )
                student_details = cursor.fetchone()
                if not student_details:
                    return [] # Student not found or no details

                student_dept_id = student_details['dept_id']
                student_semester = student_details['semester']

                # Get all offerings for this student's department and semester
                # A student can view notes for any subject offered in their current department/semester
                # A more restrictive approach might only show notes for subjects they are *assigned* to.
                # For now, let's assume they can view all notes relevant to their current academic context.
                where_clauses.append("so.dept_id = %s AND so.semester = %s")
                params.extend([student_dept_id, student_semester])

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " ORDER BY n.uploaded_at DESC"

            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error in get_notes_by_filter: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_note_file_url(note_id):
        """
        Fetches the file_url for a specific note.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT file_url FROM notes WHERE note_id = %s", (note_id,))
            result = cursor.fetchone()
            return result['file_url'] if result else None
        except Exception as e:
            print(f"Error in get_note_file_url: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def delete_note_by_id(note_id):
        """
        Deletes a note record from the database.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE note_id = %s", (note_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error in delete_note_by_id: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_subject_id_and_name_by_code(subject_code):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT subject_id, subject_name FROM subjects WHERE subject_code = %s", (subject_code,))
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error in get_subject_id_and_name_by_code: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_latest_offering_for_subject_and_dept(subject_id, dept_id):
        """
        Fetches the offering_id for a given subject and department.
        If multiple exist, it returns the one with the highest semester.
        This is an assumption for simplicity.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
            SELECT offering_id FROM subject_offerings 
            WHERE subject_id = %s AND dept_id = %s
            ORDER BY semester DESC, offering_id DESC -- Order by semester to get the latest, then by ID to be deterministic
            LIMIT 1
            """
            cursor.execute(query, (subject_id, dept_id))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error in get_latest_offering_for_subject_and_dept: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_subject_details_by_code(subject_code):
        """
        Looks up subject_id and subject_name for a given subject_code.
        Returns a dictionary {subject_id, subject_name} or None if not found.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True) # Use dictionary=True for named columns
            cursor.execute("SELECT subject_id, subject_name FROM subjects WHERE subject_code = %s", (subject_code,))
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error in get_subject_details_by_code: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_offering_id_for_faculty_upload(subject_id, faculty_dept_id):
        """
        Fetches the most relevant offering_id for a subject within a faculty's department.
        Assumes the latest semester offering if multiple exist within that department.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
            SELECT offering_id FROM subject_offerings 
            WHERE subject_id = %s AND dept_id = %s
            ORDER BY semester DESC, offering_id DESC -- Prioritize highest semester, then latest ID
            LIMIT 1
            """
            cursor.execute(query, (subject_id, faculty_dept_id))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error in get_offering_id_for_faculty_upload: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    @staticmethod
    def get_student_user_ids_for_offering(offering_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT u.id AS user_id
                FROM users u
                JOIN student_details sd ON u.id = sd.user_id
                JOIN subject_offerings so ON sd.dept_id = so.dept_id AND sd.semester = so.semester
                WHERE so.offering_id = %s
                """,
                (offering_id,)
            )
            return [row['user_id'] for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
    