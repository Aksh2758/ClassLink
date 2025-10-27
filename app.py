from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash # Added generate_password_hash

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# MySQL Configuration
# IMPORTANT: Ensure your MySQL server is running and credentials are correct.
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Aksh@2758",
        database="college_portal"
    )
    cursor = db.cursor(dictionary=True) # dictionary=True makes rows accessible by column name
    print("Successfully connected to MySQL database!")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    # You might want to exit or handle this more gracefully in a production app
    exit(1)

# --- Routes ---

@app.route('/', methods=['GET'])
def home():
    """A simple root route to confirm the backend is running."""
    return jsonify({"message": "Welcome to the College Portal Backend!"}), 200

@app.route('/register', methods=['POST'])
def register():
    """Example registration route (you'd integrate this with a frontend form)."""
    data = request.json
    user_id = data.get('id') # USN or Email
    password = data.get('password')
    role = data.get('role')

    if not all([user_id, password, role]):
        return jsonify({"message": "Missing ID, password, or role"}), 400

    hashed_password = generate_password_hash(password)

    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone():
        return jsonify({"message": "User with this ID already exists"}), 409 # Conflict

    try:
        insert_query = "INSERT INTO users (id, password_hash, role) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (user_id, hashed_password, role))
        db.commit() # Commit changes to the database
        return jsonify({"message": f"{role.capitalize()} registered successfully!"}), 201 # Created
    except mysql.connector.Error as err:
        db.rollback() # Rollback if any error occurs
        print(f"Error during registration: {err}")
        return jsonify({"message": "Registration failed due to a database error."}), 500


@app.route('/login', methods=['POST'])
def login():
    """Handles user login."""
    data = request.json
    user_id = data.get('id') # This is the USN or Email from the frontend
    password = data.get('password')
    role = data.get('role')

    if not all([user_id, password, role]):
        return jsonify({"message": "Missing ID, password, or role"}), 400

    query = "SELECT id, password_hash, role FROM users WHERE id = %s AND role = %s"

    try:
        # Corrected: Pass parameters as a tuple
        cursor.execute(query, (user_id, role))
        user = cursor.fetchone()

        if user:
            # If using hashed password
            if user['password_hash']==password:
                # Optionally, you might return a JWT or session token here
                return jsonify({"message": f"{user['role'].capitalize()} login successful!"}), 200
            else:
                return jsonify({"message": "Invalid password!"}), 401
        else:
            return jsonify({"message": "Invalid credentials or role!"}), 401
    except mysql.connector.Error as err:
        print(f"Error during login: {err}")
        return jsonify({"message": "Login failed due to a database error."}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) # host='0.0.0.0' makes it accessible from network