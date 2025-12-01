# models/notification_models.py

from datetime import datetime
from utils.db_connection import get_db_connection # <--- THIS IS THE CHANGE

def db_add_notification(user_id, message, notification_type):
    """Adds a new notification to the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO notifications (user_id, message, notification_type)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_id, message, notification_type))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error adding notification to DB: {e}")
        conn.rollback()
        return False

def db_get_user_notifications(user_id, include_read=False):
    """Retrieves notifications for a specific user from the database."""
    conn = get_db_connection()
    notifications = []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT notification_id, user_id, message, notification_type, is_read, created_at FROM notifications WHERE user_id = %s"
        if not include_read:
            query += " AND is_read = FALSE"
        query += " ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        notifications = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Error getting notifications from DB: {e}")
    return notifications

def db_mark_notification_as_read(notification_id, user_id):
    """Marks a specific notification as read for a specific user in the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            UPDATE notifications
            SET is_read = TRUE
            WHERE notification_id = %s AND user_id = %s
        """
        cursor.execute(query, (notification_id, user_id))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error marking notification as read in DB: {e}")
        conn.rollback()
        return False

def db_mark_all_user_notifications_as_read(user_id):
    """Marks all unread notifications for a user as read in the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            UPDATE notifications
            SET is_read = TRUE
            WHERE user_id = %s AND is_read = FALSE
        """
        cursor.execute(query, (user_id,))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error marking all notifications as read in DB: {e}")
        conn.rollback()
        return False

