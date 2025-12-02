import jwt
from datetime import datetime, timedelta
from config import Config # Make sure Config is accessible and has SECRET_KEY
from functools import wraps
from flask import request, jsonify

def create_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=2)  # expires in 2 hours
    }
    # Ensure Config.SECRET_KEY is defined and accessible
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def decode_token(token):
    try:
        # Ensure Config.SECRET_KEY is defined and accessible
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print("Token has expired.") # For debugging, remove in production
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.") # For debugging, remove in production
        return None

# ✅ MODIFIED token_required to accept roles
def token_required(roles=None):

    # --- Case 1: @token_required (no parentheses) ---
    if callable(roles):
        f = roles
        roles = None

        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None

            if "Authorization" in request.headers:
                parts = request.headers["Authorization"].split()
                if len(parts) == 2 and parts[0] == "Bearer":
                    token = parts[1]

            if not token:
                return jsonify({"message": "Authorization token is missing or invalid"}), 401

            decoded = decode_token(token)
            if not decoded:
                return jsonify({"message": "Token is invalid or expired"}), 401

            request.user = {
                "user_id": decoded["user_id"],
                "role": decoded["role"]
            }

            return f(*args, **kwargs)

        return decorated_function

    # --- Case 2: @token_required(roles=[...]) ---
    def wrapper(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None

            if "Authorization" in request.headers:
                parts = request.headers["Authorization"].split()
                if len(parts) == 2 and parts[0] == "Bearer":
                    token = parts[1]

            if not token:
                return jsonify({"message": "Authorization token is missing or invalid"}), 401

            decoded = decode_token(token)
            if not decoded:
                return jsonify({"message": "Token is invalid or expired"}), 401

            request.user = {
                "user_id": decoded["user_id"],
                "role": decoded["role"]
            }

            # Role check only if roles parameter is provided
            if roles:
                if request.user["role"] not in roles:
                    return jsonify({"message": "Access denied"}), 403

            return f(*args, **kwargs)

        return decorated_function

    return wrapper
