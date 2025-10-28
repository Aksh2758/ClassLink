from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.auth_routes import auth_bp  
from routes.student_routes import student_bp
# from routes.faculty_routes import faculty_bp

# --- Initialize Flask app ---
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# --- Register Blueprints (Routes Modules) ---
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
# app.register_blueprint(faculty_bp)

# --- Root Route (for testing) ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the College Portal Backend!"}), 200

# --- Run Server ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
