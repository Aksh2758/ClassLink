from flask import Flask, jsonify
from flask_cors import CORS
from config import Config, socketio 

from routes.auth_routes import auth_bp  
from routes.student_routes import student_bp
from routes.faculty_routes import faculty_bp
from routes.timetable_routes import timetable_bp
from routes.notes_routes import notes_bp
from routes.attendance_routes import attendance_bp

# --- Initialize Flask app ---
app = Flask(__name__, static_url_path='/uploads', static_folder='uploads')
app.config.from_object(Config)
CORS(app)
socketio.init_app(app)

# --- Register Blueprints (Routes Modules) ---
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(faculty_bp)
app.register_blueprint(timetable_bp)
app.register_blueprint(notes_bp, url_prefix='/api/notes')
app.register_blueprint(attendance_bp)

# --- Root Route (for testing) ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the College Portal Backend!"}), 200

# SocketIO events
@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# --- Run Server ---
if __name__ == "__main__":
    socketio.run(app)

