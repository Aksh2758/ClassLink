# app.py
from flask import Flask, jsonify, request # Make sure 'request' is imported here
from flask_cors import CORS
from config import Config, socketio 
import os

from routes.auth_routes import auth_bp  
from routes.student_routes import student_bp
from routes.faculty_routes import faculty_bp
from routes.timetable_routes import timetable_bp
from routes.notes_routes import notes_bp
from routes.attendance_routes import attendance_bp
from routes.subject_routes import subject_bp
from routes.marks_routes import marks_bp
from routes.circulars_routes import circulars_bp 
from routes.notification_routes import notifications_bp # <--- NEW: Import notifications blueprint

# --- Initialize Flask app ---
app = Flask(__name__, static_url_path='/uploads', static_folder='uploads')
app.config.from_object(Config)
CORS(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
socketio.init_app(app)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# --- Configure UPLOAD_FOLDER ---
UPLOAD_FOLDER_BASE = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_BASE
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.static_folder = UPLOAD_FOLDER_BASE
app.static_url_path = '/uploads'
os.makedirs(UPLOAD_FOLDER_BASE, exist_ok=True)

# --- Register Blueprints (Routes Modules) ---
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(faculty_bp)
app.register_blueprint(timetable_bp)
app.register_blueprint(notes_bp, url_prefix='/api/notes')
app.register_blueprint(attendance_bp,url_prefix='/api/attendance')
app.register_blueprint(subject_bp)
app.register_blueprint(marks_bp)
app.register_blueprint(circulars_bp, url_prefix='/api/circulars')
app.register_blueprint(notifications_bp) # <--- NEW: Register notifications blueprint

# --- Root Route (for testing) ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the College Portal Backend!"}), 200

# SocketIO events
from flask_socketio import join_room, leave_room, emit 

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('registerUser')
def register_user(data):
    user_id = data.get('userId')
    if user_id:
        join_room(str(user_id)) # Join a room specific to the user
        print(f"User {user_id} registered socket with SID: {request.sid}")
    else:
        print(f"Received registerUser without userId from SID: {request.sid}")

# --- Run Server ---
if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)