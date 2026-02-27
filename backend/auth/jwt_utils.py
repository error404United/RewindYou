"""JWT helpers with rotation support."""
from dotenv import load_dotenv

import os
from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "15"))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))


def generate_access_token(user_id: str, username: str, email: str, token_version: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "token_version": token_version,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def generate_refresh_token(user_id: str, token_version: str) -> str:
    payload = {
        "user_id": user_id,
        "token_version": token_version,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS),
    }
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm="HS256")


def verify_access_token(token: str) -> Dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


def verify_refresh_token(token: str) -> Dict:
    return jwt.decode(token, JWT_REFRESH_SECRET, algorithms=["HS256"])


__all__ = [
    "generate_access_token",
    "generate_refresh_token",
    "verify_access_token",
    "verify_refresh_token",
    "ACCESS_TOKEN_MINUTES",
    "REFRESH_TOKEN_DAYS",
]
