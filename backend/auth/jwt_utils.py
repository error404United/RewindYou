import jwt
from datetime import datetime, timedelta
import os

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")

def generate_access_token(user_id, username):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def generate_refresh_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm="HS256")

def verify_access_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

def verify_refresh_token(token):
    return jwt.decode(token, JWT_REFRESH_SECRET, algorithms=["HS256"])
