# utils/notifications.py

from ..models.notification_model import (
    db_add_notification,
    db_get_user_notifications,
    db_mark_notification_as_read,
    db_mark_all_user_notifications_as_read
)

# This layer can add validation, logging, or more complex logic before/after DB calls.
# For notifications, the model layer is quite direct, so this might mostly be a pass-through
# or handle formatting.

def create_notification(user_id, message, notification_type):
    """
    Creates a new notification.
    This function could perform checks (e.g., if user_id exists) before calling the DB model.
    """
    if not user_id or not message or not notification_type:
        print("Warning: Missing data for notification creation.")
        return False
    return db_add_notification(user_id, message, notification_type)

def fetch_user_notifications(user_id, include_read=False):
    """Fetches notifications for a user, potentially transforming them for the frontend."""
    notifications = db_get_user_notifications(user_id, include_read)
    # You might want to format timestamps or other fields here before returning
    for notif in notifications:
        if 'created_at' in notif and not isinstance(notif['created_at'], str):
            notif['created_at'] = notif['created_at'].isoformat() # Convert datetime to string
    return notifications

def mark_single_notification_read(notification_id, user_id):
    """Marks a single notification as read."""
    return db_mark_notification_as_read(notification_id, user_id)

def mark_all_notifications_read_for_user(user_id):
    """Marks all unread notifications for a user as read."""
    return db_mark_all_user_notifications_as_read(user_id)

# Example of how you'd call this from other parts of your Flask app:
# from utils.notifications import create_notification
# ...
# create_notification(student_user_id, "New assignment posted!", "new_assignment")