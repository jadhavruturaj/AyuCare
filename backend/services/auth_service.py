import hashlib
import hmac
import secrets
import json
import base64
import time
import re
from functools import wraps
from flask import request, jsonify
from config import Config

def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a secure salt."""
    salt = secrets.token_hex(16)
    iterations = 600000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations
    ).hex()
    return f"pbkdf2:sha256:{iterations}${salt}${derived}"

def check_password(password: str, stored_hash: str) -> bool:
    """Verifies a plain password against stored PBKDF2 hash."""
    if not stored_hash or not isinstance(stored_hash, str):
        return False
    try:
        parts = stored_hash.split("$")
        if len(parts) == 3 and parts[0].startswith("pbkdf2:sha256:"):
            iterations = int(parts[0].split(":")[2])
            salt = parts[1]
            target_hash = parts[2]
            computed = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                iterations
            ).hex()
            return hmac.compare_digest(target_hash, computed)
    except Exception:
        return False
    return False

def generate_token(user_id: int, role: str, email: str, full_name: str) -> str:
    """Generates an HMAC-signed secure bearer token with expiration."""
    exp = int(time.time()) + (Config.TOKEN_EXPIRATION_HOURS * 3600)
    payload = {
        "user_id": user_id,
        "role": role,
        "email": email,
        "name": full_name,
        "exp": exp
    }
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8").rstrip("=")
    
    signature = hmac.new(
        Config.SECRET_KEY.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return f"{payload_b64}.{signature}"

def verify_token(token: str):
    """Verifies HMAC signature and expiration of bearer token. Returns payload dict or None."""
    if not token or "." not in token:
        return None
    try:
        payload_b64, signature = token.split(".", 1)
        # Verify HMAC signature
        expected_sig = hmac.new(
            Config.SECRET_KEY.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            return None
        
        # Add padding back if necessary
        padding = 4 - (len(payload_b64) % 4)
        if padding != 4:
            payload_b64 += "=" * padding
        
        payload_bytes = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
        payload = json.loads(payload_bytes.decode("utf-8"))
        
        # Check expiry
        if payload.get("exp", 0) < int(time.time()):
            return None
        
        return payload
    except Exception:
        return None

def get_current_user():
    """Extracts bearer token from Authorization header and verifies it."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    return verify_token(token)

def login_required(role=None):
    """Decorator ensuring request has valid authentication and optional required role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({
                    "success": False,
                    "message": "Authentication required. Please log in."
                }), 401
            
            if role and user.get("role") != role:
                return jsonify({
                    "success": False,
                    "message": f"Access denied. Required role: {role}"
                }), 403
            
            # Pass user info into kwargs or request context
            request.user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_email(email: str) -> bool:
    """Validates email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_mobile(mobile: str) -> bool:
    """Validates mobile number format (supports Indian and international digits)."""
    cleaned = re.sub(r'[\s\-\(\)\+]', '', mobile.strip())
    return len(cleaned) >= 10 and len(cleaned) <= 15 and cleaned.isdigit()

def generate_otp_code() -> str:
    """Generates a cryptographically random 6-digit numeric OTP."""
    return f"{secrets.randbelow(900000) + 100000:06d}"

def generate_verification_token(mobile: str, purpose: str) -> str:
    """Generates a time-limited HMAC signed token proving mobile verification."""
    exp = int(time.time()) + 900  # 15 minutes validity
    payload = {
        "mobile": mobile,
        "purpose": purpose,
        "exp": exp
    }
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8").rstrip("=")
    sig = hmac.new(
        Config.SECRET_KEY.encode("utf-8"),
        f"mobile_verify:{payload_b64}".encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{payload_b64}.{sig}"

def verify_verification_token(token: str, expected_mobile: str, expected_purpose: str) -> bool:
    """Verifies the HMAC signed verification token."""
    if not token or "." not in token:
        return False
    try:
        payload_b64, sig = token.split(".", 1)
        expected_sig = hmac.new(
            Config.SECRET_KEY.encode("utf-8"),
            f"mobile_verify:{payload_b64}".encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return False

        padding = 4 - (len(payload_b64) % 4)
        if padding != 4:
            payload_b64 += "=" * padding
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))

        if payload.get("exp", 0) < int(time.time()):
            return False
        if payload.get("mobile") != expected_mobile:
            return False
        if payload.get("purpose") != expected_purpose:
            return False
        return True
    except Exception:
        return False

def generate_reset_token() -> str:
    """Generates a secure, cryptographically random password reset token."""
    return secrets.token_urlsafe(48)
