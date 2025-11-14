# routes/upload_students.py
from flask import Blueprint, request, jsonify
import pandas as pd
from utils.db_connection import get_db_connection

upload_bp = Blueprint("upload_bp", __name__)

@upload_bp.route("/api/upload/students", methods=["POST"])
def upload_students():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    # Only accept Excel files
    if not file.filename.endswith((".xlsx", ".xls")):
        return jsonify({"error": "Invalid file format"}), 400

    try:
        df = pd.read_excel(file)

        required_columns = [
            "user_id", "name", "usn", "email",
            "semester", "department", "section"
        ]

        # Validate columns
        for col in required_columns:
            if col not in df.columns:
                return jsonify({"error": f"Missing column: {col}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO student_details 
            (user_id, name, usn, email, semester, department, section)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        rows = []
        for _, row in df.iterrows():
            rows.append((
                str(row["user_id"]),
                str(row["name"]),
                str(row["usn"]),
                str(row["email"]),
                int(row["semester"]),
                str(row["department"]),
                str(row["section"])
            ))

        cursor.executemany(query, rows)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Students uploaded successfully",
            "uploaded_count": len(rows)
        }), 201

    except Exception as e:
        print("Upload error:", e)
        return jsonify({"error": "Failed to process file"}), 500
