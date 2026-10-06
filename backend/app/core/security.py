"""Small dependency-free authentication primitives for the MVP.

Passwords use PBKDF2-HMAC-SHA256 with a unique random salt. Access tokens are
short-lived, HMAC-signed JWT-shaped tokens so the project does not need another
runtime dependency. Replace with an established identity provider/JWT library
before a large production deployment if desired.
"""
import base64
import hashlib
import hmac
import json
import secrets
import time
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.database import get_db
from backend.app.models.user import User

PASSWORD_ITERATIONS = 310_000
TOKEN_TTL_SECONDS = 60 * 60 * 8
ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(user: User) -> str:
    secret = settings.auth_secret
    if not secret:
        raise RuntimeError("AUTH_SECRET is not configured")
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "business_id": user.business_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    head = _b64(json.dumps(header, separators=(",", ":")).encode())
    body = _b64(json.dumps(payload, separators=(",", ":")).encode())
    signature = _b64(hmac.new(secret.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest())
    return f"{head}.{body}.{signature}"


def decode_access_token(token: str) -> dict:
    secret = settings.auth_secret
    if not secret:
        raise HTTPException(status_code=500, detail="Authentication is not configured", headers={"X-Error-Code": "AUTH_NOT_CONFIGURED"})
    try:
        head, body, signature = token.split(".", 2)
        expected = _b64(hmac.new(secret.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("bad signature")
        header = json.loads(_unb64(head))
        payload = json.loads(_unb64(body))
        if header.get("alg") != ALGORITHM or int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired token")
        if not payload.get("sub"):
            raise ValueError("missing subject")
        return payload
    except (ValueError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired authentication token", headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "INVALID_TOKEN"})


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "AUTH_REQUIRED"})
    payload = decode_access_token(credentials.credentials)
    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User account is inactive or unavailable", headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "USER_INACTIVE"})
    request.state.current_user = user
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required", headers={"X-Error-Code": "ADMIN_REQUIRED"})
    return user


def require_business_owner(user: User = Depends(get_current_user)) -> User:
    if user.role != "BUSINESS_OWNER":
        raise HTTPException(status_code=403, detail="Business owner access required", headers={"X-Error-Code": "BUSINESS_OWNER_REQUIRED"})
    if user.business_id is None:
        raise HTTPException(status_code=403, detail="Business owner is not linked to a business", headers={"X-Error-Code": "BUSINESS_NOT_LINKED"})
    return user
