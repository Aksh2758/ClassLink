# routes/notifications_routes.py
from flask import Blueprint, jsonify, request
from utils.db_connection import get_db_connection
from utils.jwt_utils import token_required # Assuming you have a token_required decorator
from flask_socketio import emit
from config import socketio # Import socketio instance

notifications_bp = Blueprint('notifications_bp', __name__, url_prefix='/api/notifications')

# Helper function to fetch notifications for a user
def get_user_notifications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT notification_id, type, message, related_id, is_read, created_at "
            "FROM notifications WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        notifications = cursor.fetchall()
        return notifications
    finally:
        cursor.close()
        conn.close()

# API to get all notifications for the authenticated user
@notifications_bp.route('/', methods=['GET'])
@token_required
def get_notifications(current_user):
    user_id = current_user['id']
    notifications = get_user_notifications(user_id)
    return jsonify(notifications), 200

# API to mark a notification as read
@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@token_required
def mark_notification_read(current_user, notification_id):
    user_id = current_user['id']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE notifications SET is_read = TRUE WHERE notification_id = %s AND user_id = %s",
            (notification_id, user_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Notification not found or not authorized"}), 404
        return jsonify({"message": "Notification marked as read"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error marking notification as read: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# --- Socket.IO emission helper (can be used by other routes) ---
def emit_notification_to_user(user_id, notification_data):
    """Emits a notification to a specific user's socket room."""
    # Store in DB first
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO notifications (user_id, type, message, related_id) VALUES (%s, %s, %s, %s)",
            (notification_data['user_id'], notification_data['type'], notification_data['message'], notification_data.get('related_id'))
        )
        conn.commit()
        new_notification_id = cursor.lastrowid

        # Emit to the user's room
        # Add the ID and created_at for immediate client display
        notification_data['notification_id'] = new_notification_id
        notification_data['is_read'] = False
        notification_data['created_at'] = socketio.emit('new_notification', notification_data, room=str(user_id))
        print(f"Emitted notification to user {user_id}: {notification_data['message']}")
    except Exception as e:
        conn.rollback()
        print(f"Error saving or emitting notification: {e}")
    finally:
        cursor.close()
        conn.close()

def get_students_in_department_and_semester(dept_id, semester):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT u.id AS user_id FROM users u "
            "JOIN student_details sd ON u.id = sd.user_id "
            "WHERE sd.dept_id = %s AND sd.semester = %s",
            (dept_id, semester)
        )
        return [row['user_id'] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

def get_all_students_user_ids():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT u.id AS user_id FROM users u JOIN student_details sd ON u.id = sd.user_id")
        return [row['user_id'] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

def get_all_faculty_user_ids():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT u.id AS user_id FROM users u JOIN faculty_details fd ON u.id = fd.user_id")
        return [row['user_id'] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()