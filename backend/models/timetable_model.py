# backend/models/timetable_model.py
from utils.db_connection import get_db_connection

def get_subject_id_or_create(subject_code, subject_name): # Added subject_name parameter
    """
    Looks up subject_id for a given subject_code.
    If subject_code doesn't exist, it creates a new entry in the subjects table.
    Returns the subject_id.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT subject_id FROM subjects WHERE subject_code = %s", (subject_code,))
        result = cursor.fetchone()

        if result:
            # If subject exists, ensure its name is updated if different (optional, but good for consistency)
            cursor.execute("UPDATE subjects SET subject_name = %s WHERE subject_id = %s", (subject_name, result[0]))
            conn.commit()
            return result[0]
        else:
            # Create a new subject entry with provided name
            cursor.execute(
                "INSERT INTO subjects (subject_code, subject_name) VALUES (%s, %s)",
                (subject_code, subject_name)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error in get_subject_id_or_create: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_dept_id_or_create(dept_name, dept_code): # Added dept_code parameter
    """
    Looks up dept_id for a given dept_name and dept_code.
    If department (by dept_code) doesn't exist, it creates a new entry in the departments table.
    Returns the dept_id.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Try to find by dept_code first (as it's UNIQUE)
        cursor.execute("SELECT dept_id FROM departments WHERE dept_code = %s", (dept_code,))
        result = cursor.fetchone()

        if result:
            # If department exists, ensure its name is updated if different (optional)
            cursor.execute("UPDATE departments SET dept_name = %s WHERE dept_id = %s", (dept_name, result[0]))
            conn.commit()
            return result[0]
        else:
            # If dept_code does not exist, insert a new department
            cursor.execute(
                "INSERT INTO departments (dept_code, dept_name) VALUES (%s, %s)",
                (dept_code, dept_name,)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error in get_dept_id_or_create: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_offering_id_or_create(subject_id, dept_id, semester):
    """
    Looks up offering_id for a given subject, department, and semester.
    If it doesn't exist, it creates a new entry in subject_offerings.
    Returns the offering_id.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT offering_id FROM subject_offerings WHERE subject_id = %s AND dept_id = %s AND semester = %s",
            (subject_id, dept_id, semester)
        )
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            cursor.execute(
                "INSERT INTO subject_offerings (subject_id, dept_id, semester) VALUES (%s, %s, %s)",
                (subject_id, dept_id, semester)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error in get_offering_id_or_create: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_assignment_id_or_create(offering_id, faculty_id, section):
    """
    Looks up assignment_id for a given offering, faculty, and section.
    If it doesn't exist, it creates a new entry in faculty_assignment.
    Returns the assignment_id.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT assignment_id FROM faculty_assignment WHERE offering_id = %s AND faculty_id = %s AND section = %s",
            (offering_id, faculty_id, section)
        )
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            cursor.execute(
                "INSERT INTO faculty_assignment (offering_id, faculty_id, section) VALUES (%s, %s, %s)",
                (offering_id, faculty_id, section)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error in get_assignment_id_or_create: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def save_timetable_entry(semester, department_name, department_code, section, day_of_week, period_number, subject_code, subject_name, faculty_id):
    """
    Saves or updates a timetable entry in the new schema.
    Handles dynamic creation/lookup of subjects, departments, offerings, and assignments.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Get or create subject_id (now using subject_name)
        subject_id = get_subject_id_or_create(subject_code.strip(), subject_name.strip())

        # 2. Get or create dept_id (now using dept_name AND dept_code)
        dept_id = get_dept_id_or_create(department_name.strip(), department_code.strip())
        if not dept_id: # Should not happen if get_dept_id_or_create handles creation correctly
            raise ValueError(f"Could not find or create department '{department_name}' with code '{department_code}'")

        # 3. Get or create offering_id
        offering_id = get_offering_id_or_create(subject_id, dept_id, semester)

        # 4. Get or create assignment_id
        if not faculty_id:
            raise ValueError("Faculty ID is required to create a faculty assignment.")

        assignment_id = get_assignment_id_or_create(offering_id, faculty_id, section.strip())

        # 5. Insert/Update into timetable_template
        query = """
        INSERT INTO timetable_template
            (assignment_id, day_of_week, period_number)
        VALUES
            (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            assignment_id = VALUES(assignment_id);
        """
        cursor.execute(query, (
            assignment_id,
            day_of_week.strip(),
            period_number
        ))
        conn.commit()
        return True
    except ValueError as ve:
        print(f"Validation error in save_timetable_entry: {ve}")
        raise
    except Exception as e:
        print(f"Database error in save_timetable_entry: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_timetable_for_class(dept_name, semester, section=None):
    """
    Fetches timetable entries for a given department, semester, and optional section
    from the new schema. Joins across multiple tables.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # We need to get dept_id from dept_name. Assuming dept_name is unique enough for lookup.
        cursor.execute("SELECT dept_id FROM departments WHERE dept_name = %s", (dept_name,))
        dept_record = cursor.fetchone()
        if not dept_record:
            return [] # Department not found

        dept_id = dept_record['dept_id']

        query = """
        SELECT
            tt.day_of_week,
            tt.period_number,
            s.subject_code,
            s.subject_name,
            fa.faculty_id,
            fd.name AS faculty_name, -- Corrected alias
            fa.section
        FROM
            timetable_template tt
        JOIN
            faculty_assignment fa ON tt.assignment_id = fa.assignment_id
        JOIN
            subject_offerings so ON fa.offering_id = so.offering_id
        JOIN
            subjects s ON so.subject_id = s.subject_id
        LEFT JOIN
            faculty_details fd ON fa.faculty_id = fd.faculty_id
        WHERE
            so.dept_id = %s AND so.semester = %s
        """
        params = [dept_id, semester]

        # Filter by section if provided
        if section and section.strip():
            query += " AND fa.section = %s"
            params.append(section.strip())

        query += " ORDER BY FIELD(tt.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), tt.period_number"

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error in get_timetable_for_class: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_student_department_semester_section(user_id): # Renamed parameter to user_id
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                dd.dept_name,
                sd.semester,
                sd.section
            FROM
                student_details sd
            JOIN
                departments dd ON sd.dept_id = dd.dept_id
            WHERE sd.user_id = %s -- Correctly uses user_id
            """,
            (user_id,)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching student details by user_id: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conn: conn.close()