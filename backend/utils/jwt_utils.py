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
def token_required(roles=None): # roles can be a list of strings, e.g., ['faculty', 'admin']
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None

            # Look for token in Authorization header
            if "Authorization" in request.headers:
                parts = request.headers["Authorization"].split()
                if len(parts) == 2 and parts[0] == "Bearer":
                    token = parts[1]

            if not token:
                return jsonify({"message": "Authorization token is missing or invalid"}), 401

            decoded = decode_token(token)
            if not decoded:
                return jsonify({"message": "Token is invalid or expired"}), 401

            # Attach user info to request context
            request.user = {
                "user_id": decoded["user_id"],
                "role": decoded["role"]
            }

            # --- Role-based access control check ---
            if roles: # If roles are specified for this endpoint
                user_role = request.user.get('role')
                if user_role not in roles:
                    return jsonify({"message": f"Access denied: Requires one of {', '.join(roles)} role(s)"}), 403
            # --- End Role-based access control check ---

            return decorated_function(*args, **kwargs)
        return decorated_function
    return decorator