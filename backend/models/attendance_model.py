# backend/models/attendance_model.py
from utils.db_connection import get_db_connection
from datetime import datetime

class AttendanceModel:
    @staticmethod
    def _get_entity_ids(dept_code=None, semester=None, subject_code=None, faculty_user_id=None, section=None, student_user_id=None):
        """
        Helper to fetch various IDs needed for attendance operations,
        given higher-level identifiers.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            ids = {}

            if faculty_user_id:
                cursor.execute("SELECT faculty_id FROM faculty_details WHERE user_id = %s", (faculty_user_id,))
                result = cursor.fetchone()
                if result: ids['faculty_id'] = result['faculty_id']

            if student_user_id:
                cursor.execute("SELECT student_id, dept_id, semester, section FROM student_details WHERE user_id = %s", (student_user_id,))
                result = cursor.fetchone()
                if result:
                    ids['student_id'] = result['student_id']
                    ids['student_dept_id'] = result['dept_id']
                    ids['student_semester'] = result['semester']
                    ids['student_section'] = result['section']


            if dept_code:
                cursor.execute("SELECT dept_id FROM departments WHERE dept_code = %s", (dept_code,))
                result = cursor.fetchone()
                if result: ids['dept_id'] = result['dept_id']

            if subject_code:
                cursor.execute("SELECT subject_id FROM subjects WHERE subject_code = %s", (subject_code,))
                result = cursor.fetchone()
                if result: ids['subject_id'] = result['subject_id']

            return ids
        except Exception as e:
            print(f"Error in _get_entity_ids: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_class_session_by_details(date_str, period_number, dept_code, semester, subject_code, faculty_user_id, section):
        """
        Fetches an existing class_session_id based on a specific set of class details.
        This is crucial before marking attendance.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            ids = AttendanceModel._get_entity_ids(
                dept_code=dept_code,
                semester=semester, # Not directly used here, but for offering
                subject_code=subject_code,
                faculty_user_id=faculty_user_id
            )

            if not all(k in ids for k in ['dept_id', 'subject_id', 'faculty_id']):
                return None # Missing fundamental IDs

            dept_id = ids['dept_id']
            subject_id = ids['subject_id']
            faculty_id = ids['faculty_id']

            # First, find the offering_id
            cursor.execute(
                "SELECT offering_id FROM subject_offerings WHERE subject_id = %s AND dept_id = %s AND semester = %s",
                (subject_id, dept_id, semester)
            )
            offering = cursor.fetchone()
            if not offering: return None
            offering_id = offering['offering_id']

            # Then, find the assignment_id
            cursor.execute(
                "SELECT assignment_id FROM faculty_assignment WHERE offering_id = %s AND faculty_id = %s AND section = %s",
                (offering_id, faculty_id, section)
            )
            assignment = cursor.fetchone()
            if not assignment: return None
            assignment_id = assignment['assignment_id']
            
            # Now, find the class_session
            # We need the day_of_week for class_sessions table
            session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            day_of_week = session_date.strftime('%A') # e.g., 'Monday'

            cursor.execute(
                """
                SELECT session_id
                FROM class_sessions
                WHERE assignment_id = %s AND session_date = %s AND period_number = %s
                """,
                (assignment_id, session_date, period_number)
            )
            session = cursor.fetchone()
            return session['session_id'] if session else None

        except Exception as e:
            print(f"Error in get_class_session_by_details: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def create_class_session_from_template(assignment_id, session_date_str, period_number):
        """
        Creates a new class_session entry if it doesn't already exist,
        typically invoked by a faculty for the first time marking attendance,
        or by an automated timetable generation process.
        Returns the session_id.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
            day_of_week = session_date.strftime('%A')

            # Check if session already exists
            cursor.execute(
                "SELECT session_id FROM class_sessions WHERE assignment_id = %s AND session_date = %s AND period_number = %s",
                (assignment_id, session_date, period_number)
            )
            existing_session = cursor.fetchone()
            if existing_session:
                return existing_session[0]

            # If not, create it
            query = """
            INSERT INTO class_sessions
                (assignment_id, session_date, day_of_week, period_number)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (assignment_id, session_date, day_of_week, period_number))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error in create_class_session_from_template: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def submit_attendance_for_session(session_id, attendance_data):
        """
        Submits/updates attendance for multiple students for a given class session.
        attendance_data is a list of {'student_id': <id>, 'status': 'present'/'absent'}
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            processed_count = 0
            for entry in attendance_data:
                student_id = entry.get('student_id')
                status = entry.get('status')
                if not student_id or not status:
                    print(f"Skipping invalid attendance entry: {entry}")
                    continue

                # UPSERT logic for attendance: insert or update if exists
                query = """
                INSERT INTO attendance (session_id, student_id, status)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE status = VALUES(status)
                """
                cursor.execute(query, (session_id, student_id, status))
                processed_count += 1
            conn.commit()
            return processed_count
        except Exception as e:
            print(f"Error in submit_attendance_for_session: {e}")
            conn.rollback() # Rollback if any part of the batch fails
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_student_ids_for_section(dept_id, semester, section):
        """
        Fetches all student_ids for a given department, semester, and section.
        Useful for faculty to get a list of students to mark attendance for.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT sd.student_id, sd.name, sd.usn
                FROM student_details sd
                WHERE sd.dept_id = %s AND sd.semester = %s AND sd.section = %s
                ORDER BY sd.usn
                """,
                (dept_id, semester, section)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error in get_student_ids_for_section: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


    @staticmethod
    def get_attendance_history_for_class(dept_code, semester, section, subject_code=None, start_date=None, end_date=None):
        """
        Fetches attendance records (class_sessions) for a class.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            ids = AttendanceModel._get_entity_ids(
                dept_code=dept_code,
                subject_code=subject_code # subject_code is optional here
            )
            if 'dept_id' not in ids:
                return []

            dept_id = ids['dept_id']
            subject_id = ids.get('subject_id')

            query = """
            SELECT
                cs.session_id,
                cs.session_date,
                cs.day_of_week,
                cs.period_number,
                s.subject_code,
                s.subject_name,
                fd.name AS faculty_name,
                fa.section
            FROM
                class_sessions cs
            JOIN
                faculty_assignment fa ON cs.assignment_id = fa.assignment_id
            JOIN
                subject_offerings so ON fa.offering_id = so.offering_id
            JOIN
                subjects s ON so.subject_id = s.subject_id
            JOIN
                faculty_details fd ON fa.faculty_id = fd.faculty_id
            WHERE
                so.dept_id = %s AND so.semester = %s AND fa.section = %s
            """
            params = [dept_id, semester, section]

            if subject_id:
                query += " AND s.subject_id = %s"
                params.append(subject_id)
            if start_date:
                query += " AND cs.session_date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND cs.session_date <= %s"
                params.append(end_date)

            query += " ORDER BY cs.session_date DESC, cs.period_number ASC"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error in get_attendance_history_for_class: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_attendance_details_for_session(session_id):
        """
        Fetches individual student attendance for a specific class session.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT
                a.attendance_id,
                a.status,
                sd.student_id,
                sd.name AS student_name,
                sd.usn
            FROM
                attendance a
            JOIN
                student_details sd ON a.student_id = sd.student_id
            WHERE
                a.session_id = %s
            ORDER BY sd.usn
            """
            cursor.execute(query, (session_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error in get_attendance_details_for_session: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    @staticmethod
    def update_single_attendance_status(attendance_id, new_status):
        """
        Updates the status of a single attendance record.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
            UPDATE attendance
            SET status = %s
            WHERE attendance_id = %s
            """
            cursor.execute(query, (new_status, attendance_id))
            conn.commit()
            return cursor.rowcount > 0 # Return True if updated, False otherwise
        except Exception as e:
            print(f"Error in update_single_attendance_status: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_student_overall_attendance(student_user_id):
        """
        Calculates overall attendance percentage for a student across all their subjects.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            ids = AttendanceModel._get_entity_ids(student_user_id=student_user_id)
            if 'student_id' not in ids:
                return None # Student not found

            student_id = ids['student_id']

            query = """
            SELECT
                COUNT(a.attendance_id) AS total_sessions,
                SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_sessions,
                s.subject_code,
                s.subject_name,
                so.semester
            FROM
                attendance a
            JOIN
                class_sessions cs ON a.session_id = cs.session_id
            JOIN
                faculty_assignment fa ON cs.assignment_id = fa.assignment_id
            JOIN
                subject_offerings so ON fa.offering_id = so.offering_id
            JOIN
                subjects s ON so.subject_id = s.subject_id
            WHERE
                a.student_id = %s
            GROUP BY s.subject_id, so.semester
            ORDER BY so.semester, s.subject_name
            """
            cursor.execute(query, (student_id,))
            results = cursor.fetchall()

            for res in results:
                total = res['total_sessions']
                present = res['present_sessions']
                res['attendance_percentage'] = (present / total * 100) if total > 0 else 0

            return results
        except Exception as e:
            print(f"Error in get_student_overall_attendance: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()