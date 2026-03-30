from functools import wraps
from flask import request, jsonify, g
import jwt

from auth.jwt_utils import verify_access_token
from db.mongodb import get_users_collection, get_sessions_collection


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing bearer token"}), 401

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = verify_access_token(token)
            session_id = payload.get("sid")
            user_id = payload.get("user_id")

            if not session_id or not user_id:
                return jsonify({"error": "Invalid access token"}), 401

            session = get_sessions_collection().find_one(
                {"_id": session_id, "user_id": user_id, "revoked_at": None}
            )
            if not session:
                return jsonify({"error": "Session no longer valid"}), 401

            user = get_users_collection().find_one({"_id": user_id})
            if not user:
                return jsonify({"error": "User not found"}), 401

            request.user = {
                "user_id": str(user.get("_id")),
                "username": user.get("username"),
                "email": user.get("email"),
            }
            request.auth = {"sid": session_id}
            g.rate_user_key = str(user.get("_id"))
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Access token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid access token"}), 401

        return f(*args, **kwargs)

    return decorated
