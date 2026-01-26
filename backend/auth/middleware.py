from functools import wraps
from flask import request, jsonify, g
import jwt

from auth.jwt_utils import verify_access_token
from db.mongodb import get_users_collection


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing bearer token"}), 401

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = verify_access_token(token)
            user = get_users_collection().find_one({"_id": payload.get("user_id")})
            if not user or user.get("token_version") != payload.get("token_version"):
                return jsonify({"error": "Token no longer valid"}), 401

            request.user = {
                "user_id": str(user.get("_id")),
                "username": user.get("username"),
                "email": user.get("email"),
            }
            g.rate_user_key = str(user.get("_id"))
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Access token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid access token"}), 401

        return f(*args, **kwargs)

    return decorated
