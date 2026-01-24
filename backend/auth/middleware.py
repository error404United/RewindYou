from functools import wraps
from flask import request, jsonify
from auth.jwt_utils import verify_access_token
import jwt

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing token"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = verify_access_token(token)
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated
