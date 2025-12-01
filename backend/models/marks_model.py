# backend/models/marks_model.py
from utils.db_connection import get_db_connection
from models.timetable_model import ( # Reusing helpers from timetable model
    get_dept_id_or_create,
    get_subject_id_or_create,
    get_offering_id_or_create
)
from models.attendance_model import AttendanceModel # Reusing _get_entity_ids for student/faculty IDs

class MarksModel:

    @staticmethod
    def get_ia_type_id_or_create(ia_name):
        """
        Gets the ia_type_id for a given IA name (e.g., 'IA1', 'Quiz'), creating it if it doesn't exist.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Try to find existing IA type
            cursor.execute("SELECT ia_type_id FROM internal_assessment_types WHERE ia_name = %s", (ia_name,))
            result = cursor.fetchone()
            if result:
                return result[0]

            # If not found, create a new one
            cursor.execute("INSERT INTO internal_assessment_types (ia_name) VALUES (%s)", (ia_name,))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error in get_ia_type_id_or_create: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    @staticmethod
    def get_user_id_from_student_id(student_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM student_details WHERE student_id = %s", (student_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error in get_user_id_from_student_id: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_subject_name_by_offering_id(offering_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT s.subject_name
                FROM subject_offerings so
                JOIN subjects s ON so.subject_id = s.subject_id
                WHERE so.offering_id = %s
                """,
                (offering_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else "Unknown Subject"
        except Exception as e:
            print(f"Error in get_subject_name_by_offering_id: {e}")
            return "Unknown Subject"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_students_for_class_with_marks(dept_code, semester, section, subject_code):
        """
        Retrieves students enrolled in a specific class and their existing marks
        for a given subject across all IA types.
        Used for the faculty "Enter Marks" dashboard.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 1. Get dept_id
            dept_ids = AttendanceModel._get_entity_ids(dept_code=dept_code)
            dept_id = dept_ids.get('dept_id')
            if not dept_id: return []

            # 2. Get subject_id
            subject_ids = AttendanceModel._get_entity_ids(subject_code=subject_code)
            subject_id = subject_ids.get('subject_id')
            if not subject_id: return []

            # 3. Get offering_id
            cursor.execute(
                "SELECT offering_id FROM subject_offerings WHERE subject_id = %s AND dept_id = %s AND semester = %s",
                (subject_id, dept_id, semester)
            )
            offering_record = cursor.fetchone()
            if not offering_record: return []
            offering_id = offering_record['offering_id']

            # 4. Fetch students for the specified class (dept, sem, section)
            # 5. LEFT JOIN marks and internal_assessment_types to get existing scores
            query = """
            SELECT
                sd.student_id,
                sd.name AS student_name,
                sd.usn AS roll_no,
                GROUP_CONCAT(
                    CONCAT(iat.ia_name, ':', m.score)
                    ORDER BY iat.ia_name ASC
                    SEPARATOR ';'
                ) AS marks_data
            FROM
                student_details sd
            LEFT JOIN
                marks m ON sd.student_id = m.student_id AND m.offering_id = %s
            LEFT JOIN
                internal_assessment_types iat ON m.ia_type_id = iat.ia_type_id
            WHERE
                sd.dept_id = %s AND sd.semester = %s AND sd.section = %s
            GROUP BY
                sd.student_id, sd.name, sd.usn
            ORDER BY
                sd.usn ASC
            """
            cursor.execute(query, (offering_id, dept_id, semester, section))
            students_with_raw_marks = cursor.fetchall()

            # Process raw marks_data into a dictionary for easier consumption
            processed_students = []
            for student in students_with_raw_marks:
                student_data = {
                    'student_id': student['student_id'],
                    'student_name': student['student_name'],
                    'roll_no': student['roll_no'],
                    'ia_scores': {}
                }
                if student['marks_data']:
                    ia_entries = student['marks_data'].split(';')
                    for entry in ia_entries:
                        if ':' in entry:
                            ia_name, score = entry.split(':')
                            student_data['ia_scores'][ia_name] = float(score) if score else None
                processed_students.append(student_data)
            
            return processed_students

        except Exception as e:
            print(f"Error in get_students_for_class_with_marks: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update_student_marks(offering_id, student_id, ia_type_id, score):
        """
        Inserts or updates a student's mark for a specific IA type in a subject offering.
        Uses ON DUPLICATE KEY UPDATE.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
            INSERT INTO marks (student_id, offering_id, ia_type_id, score)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE score = VALUES(score)
            """
            cursor.execute(query, (student_id, offering_id, ia_type_id, score))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error in update_student_marks: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_student_all_ia_scores(student_user_id):
        """
        Retrieves all IA scores for a given student across all their subjects.
        Used for the student "Internal Marks" dashboard.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 1. Get student_id
            student_ids = AttendanceModel._get_entity_ids(student_user_id=student_user_id)
            student_id = student_ids.get('student_id')
            if not student_id: return []

            # 2. Fetch marks
            query = """
            SELECT
                s.subject_code,
                s.subject_name,
                iat.ia_name,
                m.score
            FROM
                marks m
            JOIN
                student_details sd ON m.student_id = sd.student_id
            JOIN
                subject_offerings so ON m.offering_id = so.offering_id
            JOIN
                subjects s ON so.subject_id = s.subject_id
            JOIN
                internal_assessment_types iat ON m.ia_type_id = iat.ia_type_id
            WHERE
                sd.student_id = %s
            ORDER BY
                s.subject_code, iat.ia_name
            """
            cursor.execute(query, (student_id,))
            raw_scores = cursor.fetchall()

            # Group scores by subject for the frontend
            grouped_scores = {}
            for row in raw_scores:
                subject_code = row['subject_code']
                if subject_code not in grouped_scores:
                    grouped_scores[subject_code] = {
                        'subject_code': subject_code,
                        'subject_name': row['subject_name'],
                        'scores': {}
                    }
                grouped_scores[subject_code]['scores'][row['ia_name']] = row['score']
            
            # Convert to list of dictionaries for consistent API response
            return list(grouped_scores.values())

        except Exception as e:
            print(f"Error in get_student_all_ia_scores: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()