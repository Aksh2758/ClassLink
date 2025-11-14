# backend/models/profile_model.py
from utils.db_connection import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from models.attendance_model import AttendanceModel # For _get_entity_ids (student/faculty details)

class ProfileModel:

    @staticmethod
    def get_user_profile(user_id, role):
        """
        Fetches the complete profile details for a user based on their role.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            profile_data = {}

            # Always fetch basic user info
            cursor.execute("SELECT id, email, role FROM users WHERE id = %s", (user_id,))
            user_info = cursor.fetchone()
            if not user_info:
                return None # User not found
            profile_data.update(user_info)

            # Fetch role-specific details
            if role == 'student':
                query = """
                SELECT
                    sd.student_id,
                    sd.name,
                    sd.usn,
                    sd.semester,
                    sd.section,
                    d.dept_code,
                    d.dept_name
                FROM
                    student_details sd
                JOIN
                    departments d ON sd.dept_id = d.dept_id
                WHERE
                    sd.user_id = %s
                """
                cursor.execute(query, (user_id,))
                student_details = cursor.fetchone()
                if student_details:
                    profile_data.update(student_details)
            
            elif role == 'faculty':
                query = """
                SELECT
                    fd.faculty_id,
                    fd.name,
                    fd.designation,
                    d.dept_code,
                    d.dept_name
                FROM
                    faculty_details fd
                JOIN
                    departments d ON fd.dept_id = d.dept_id
                WHERE
                    fd.user_id = %s
                """
                cursor.execute(query, (user_id,))
                faculty_details = cursor.fetchone()
                if faculty_details:
                    profile_data.update(faculty_details)
            
            elif role == 'admin':
                # Admins might just have basic user info, or an admin_details table if needed
                pass # No additional details for admin in current schema

            return profile_data
        except Exception as e:
            print(f"Error in get_user_profile: {e}")
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update_student_profile(user_id, name, usn=None, semester=None, section=None, dept_code=None):
        """
        Updates specific fields for a student's profile.
        Note: semester, section, dept_code are typically managed by admin, but allowing here for flexibility.
        Real-world systems might restrict these updates from the user side.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clauses = ["name = %s"]
            params = [name]

            if usn:
                set_clauses.append("usn = %s")
                params.append(usn)
            if semester is not None:
                set_clauses.append("semester = %s")
                params.append(semester)
            if section:
                set_clauses.append("section = %s")
                params.append(section)
            if dept_code:
                # Need to get dept_id from dept_code
                dept_ids_info = AttendanceModel._get_entity_ids(dept_code=dept_code)
                dept_id = dept_ids_info.get('dept_id')
                if not dept_id:
                    raise ValueError(f"Department with code '{dept_code}' not found.")
                set_clauses.append("dept_id = %s")
                params.append(dept_id)

            if not set_clauses: # If only user_id was passed, no update
                return False

            query = f"UPDATE student_details SET {', '.join(set_clauses)} WHERE user_id = %s"
            params.append(user_id)
            
            cursor.execute(query, tuple(params))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error in update_student_profile: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    @staticmethod
    def update_faculty_profile(user_id, name, designation=None, dept_code=None):
        """
        Updates specific fields for a faculty's profile.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clauses = ["name = %s"]
            params = [name]

            if designation:
                set_clauses.append("designation = %s")
                params.append(designation)
            if dept_code:
                # Need to get dept_id from dept_code
                dept_ids_info = AttendanceModel._get_entity_ids(dept_code=dept_code)
                dept_id = dept_ids_info.get('dept_id')
                if not dept_id:
                    raise ValueError(f"Department with code '{dept_code}' not found.")
                set_clauses.append("dept_id = %s")
                params.append(dept_id)
            
            if not set_clauses: # If only user_id was passed, no update
                return False

            query = f"UPDATE faculty_details SET {', '.join(set_clauses)} WHERE user_id = %s"
            params.append(user_id)
            
            cursor.execute(query, tuple(params))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error in update_faculty_profile: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def change_user_password(user_id, current_password, new_password):
        """
        Changes a user's password after verifying the current password.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. Get current password hash
            cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                return False, "User not found"
            
            stored_password_hash = result[0]

            # 2. Verify current password
            if not check_password_hash(stored_password_hash, current_password):
                return False, "Current password does not match"
            
            # 3. Hash new password and update
            new_password_hash = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_password_hash, user_id))
            conn.commit()
            return True, "Password changed successfully"
        except Exception as e:
            print(f"Error in change_user_password: {e}")
            conn.rollback()
            raise
        finally:
            if cursor: cursor.close()
            if conn: conn.close()