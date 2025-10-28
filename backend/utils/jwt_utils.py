import jwt
from datetime import datetime, timedelta
from config import Config
from functools import wraps
from flask import request, jsonify

def create_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=2)  # expires in 2 hours
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def decode_token(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ✅ Add this
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Look for token in Authorization header
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({"message": "Missing or invalid token"}), 401

        decoded = decode_token(token)
        if not decoded:
            return jsonify({"message": "Token is invalid or expired"}), 401

        # Attach user info to request context
        request.user = {
            "user_id": decoded["user_id"],
            "role": decoded["role"]
        }

        return f(*args, **kwargs)
    return decorated
