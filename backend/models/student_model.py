# backend/models/student_model.py
from utils.db_connection import get_db_connection

class StudentModel:
    @staticmethod
    def get_student_by_user_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Modified to fetch data from relevant tables and match schema
        cursor.execute(
            """
            SELECT 
                sd.name, 
                sd.usn, 
                sd.semester,
                sd.section, 
                u.email, 
                d.dept_name, 
                d.dept_code,
                sd.student_id -- Include student_id for other operations if needed
            FROM student_details sd
            JOIN users u ON sd.user_id = u.id
            JOIN departments d ON sd.dept_id = d.dept_id
            WHERE sd.user_id = %s
            """,
            (user_id,)
        )
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        return student

    @staticmethod
    def get_notifications_for_student(student_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Your schema uses 'circulars' for notifications.
        # We need to fetch circulars relevant to the student.
        # This is a more complex query, considering 'all', 'students', 'specific_dept' audience.
        cursor.execute(
            """
            SELECT c.*
            FROM circulars c
            LEFT JOIN student_details sd ON c.dept_id = sd.dept_id AND c.audience = 'specific_dept'
            WHERE 
                (c.audience = 'all') OR
                (c.audience = 'students') OR
                (c.audience = 'specific_dept' AND sd.student_id = %s)
            ORDER BY c.posted_at DESC
            """,
            (student_id,) # This student_id here is for filtering by specific_dept
                          # Need to rethink this query slightly to truly filter by student's department.
                          # Let's refine this to correctly fetch *all* relevant circulars.
        )
        # A student should see:
        # 1. Circulars for 'all'
        # 2. Circulars for 'students'
        # 3. Circulars for their specific department
        # To do this, we first need the student's dept_id.
        
        # Re-doing the get_notifications_for_student for accuracy with 'circulars' table
        cursor.execute(
            """
            SELECT sd.dept_id FROM student_details sd WHERE sd.student_id = %s
            """, (student_id,)
        )
        student_dept = cursor.fetchone()
        
        if student_dept:
            student_dept_id = student_dept['dept_id']
            cursor.execute(
                """
                SELECT c.*, fd.name as faculty_name, d.dept_name
                FROM circulars c
                LEFT JOIN faculty_details fd ON c.faculty_id = fd.faculty_id
                LEFT JOIN departments d ON c.dept_id = d.dept_id
                WHERE 
                    c.audience = 'all' OR
                    c.audience = 'students' OR
                    (c.audience = 'specific_dept' AND c.dept_id = %s)
                ORDER BY c.posted_at DESC
                """,
                (student_dept_id,)
            )
            data = cursor.fetchall()
        else:
            data = [] # No student or department found

        cursor.close()
        conn.close()
        return data