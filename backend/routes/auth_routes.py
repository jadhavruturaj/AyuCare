import datetime
import logging
from flask import Blueprint, request, jsonify
from config import Config
from database import fetch_one, execute_query
from services.auth_service import (
    hash_password, check_password, generate_token,
    validate_email, validate_mobile, get_current_user, login_required,
    generate_otp_code, generate_verification_token, verify_verification_token,
    generate_reset_token
)
from services.sms_service import send_otp_sms, normalize_mobile
from services.email_service import (
    send_password_reset_email, SMTPNotConfiguredError, EmailDeliveryError, is_smtp_configured
)

logger = logging.getLogger("ayucare.auth_routes")
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ========================================================
# MOBILE OTP VERIFICATION ENDPOINTS
# ========================================================

@auth_bp.route("/otp/send", methods=["POST"])
def send_otp():
    """
    Sends a 6-digit OTP to user's mobile number for verification.
    Enforces format validation, duplicate checking for registration, and 60-second cooldown.
    """
    data = request.get_json() or {}
    raw_mobile = data.get("mobile", "").strip()
    purpose = data.get("purpose", "registration").strip().lower()

    if not raw_mobile:
        return jsonify({"success": False, "message": "Mobile number is required."}), 400

    if not validate_mobile(raw_mobile):
        return jsonify({
            "success": False,
            "message": "Invalid mobile number. Must contain at least 10 valid digits."
        }), 400

    mobile = normalize_mobile(raw_mobile)

    # For registration, check if mobile is already taken
    if purpose == "registration":
        existing_patient = fetch_one("SELECT id FROM patients WHERE mobile = %s", (mobile,))
        existing_doctor = fetch_one("SELECT id FROM doctors WHERE mobile = %s", (mobile,))
        if existing_patient or existing_doctor:
            return jsonify({
                "success": False,
                "message": "An account with this mobile number already exists. Please sign in instead."
            }), 409

    # Enforce 60-second cooldown between OTP requests for the same number
    last_otp = fetch_one(
        "SELECT id, created_at FROM mobile_otps WHERE mobile = %s AND purpose = %s ORDER BY id DESC LIMIT 1",
        (mobile, purpose)
    )
    now = datetime.datetime.now()
    if last_otp and last_otp.get("created_at"):
        created_val = last_otp["created_at"]
        if isinstance(created_val, str):
            try:
                # Handle standard formats
                clean_ts = created_val.split(".")[0].replace("T", " ")
                created_dt = datetime.datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")
            except Exception:
                created_dt = now
        elif isinstance(created_val, datetime.datetime):
            created_dt = created_val
        else:
            created_dt = now

        elapsed = (now - created_dt).total_seconds()
        if elapsed < 60:
            remaining = int(60 - elapsed)
            return jsonify({
                "success": False,
                "message": f"Please wait {remaining} seconds before requesting a new OTP.",
                "cooldown_remaining": remaining
            }), 429

    # Generate 6-digit code and expiration (10 minutes)
    otp_code = generate_otp_code()
    expires_at = (now + datetime.timedelta(minutes=Config.OTP_EXPIRATION_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")

    insert_sql = """
        INSERT INTO mobile_otps (mobile, otp_code, purpose, is_verified, attempts, expires_at, created_at)
        VALUES (%s, %s, %s, 0, 0, %s, %s)
    """
    execute_query(insert_sql, (mobile, otp_code, purpose, expires_at, created_at))

    # Send SMS via gateway
    sms_result = send_otp_sms(mobile, otp_code, purpose)

    return jsonify({
        "success": True,
        "message": sms_result.get("message", f"OTP has been dispatched to {mobile}."),
        "cooldown_seconds": 60,
        "expires_in_minutes": Config.OTP_EXPIRATION_MINUTES,
        "dev_otp": sms_result.get("dev_otp"),
        "otp_code": sms_result.get("dev_otp") or otp_code
    }), 200

@auth_bp.route("/otp/verify", methods=["POST"])
def verify_otp():
    """
    Verifies user-submitted 6-digit OTP code against the database.
    Checks attempts, expiration, and returns an HMAC verification token upon success.
    """
    data = request.get_json() or {}
    raw_mobile = data.get("mobile", "").strip()
    submitted_otp = (data.get("otp") or data.get("otp_code") or "").strip()
    purpose = data.get("purpose", "registration").strip().lower()

    if not raw_mobile or not submitted_otp:
        return jsonify({"success": False, "message": "Mobile number and OTP are required."}), 400

    mobile = normalize_mobile(raw_mobile)

    # Fetch latest active OTP for this mobile (matching purpose or latest request)
    record = None
    if purpose and purpose not in ("registration", "all", ""):
        record = fetch_one(
            "SELECT id, otp_code, attempts, is_verified, expires_at FROM mobile_otps WHERE mobile = %s AND purpose = %s ORDER BY id DESC LIMIT 1",
            (mobile, purpose)
        )
    if not record:
        record = fetch_one(
            "SELECT id, otp_code, attempts, is_verified, expires_at FROM mobile_otps WHERE mobile = %s ORDER BY id DESC LIMIT 1",
            (mobile,)
        )

    if not record:
        return jsonify({
            "success": False,
            "message": "No OTP request found for this mobile number. Please click 'Send OTP' first."
        }), 400

    # Check maximum attempt limit (5 attempts)
    if record.get("attempts", 0) >= 5:
        return jsonify({
            "success": False,
            "message": "Too many failed attempts. This OTP has been invalidated for security. Please request a new code."
        }), 400

    # Check expiration
    now = datetime.datetime.now()
    exp_val = record.get("expires_at")
    if isinstance(exp_val, str):
        try:
            clean_ts = exp_val.split(".")[0].replace("T", " ")
            exp_dt = datetime.datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")
        except Exception:
            exp_dt = now
    elif isinstance(exp_val, datetime.datetime):
        exp_dt = exp_val
    else:
        exp_dt = now

    if now > exp_dt:
        return jsonify({
            "success": False,
            "message": "This OTP has expired. Please request a new verification code."
        }), 400

    # Increment attempts
    execute_query("UPDATE mobile_otps SET attempts = attempts + 1 WHERE id = %s", (record["id"],))

    # Verify matching code
    if submitted_otp != str(record["otp_code"]):
        remaining_attempts = max(0, 4 - record.get("attempts", 0))
        return jsonify({
            "success": False,
            "message": f"Incorrect OTP code. Please verify and try again. ({remaining_attempts} attempt(s) remaining)"
        }), 400

    # Mark as verified in database
    execute_query("UPDATE mobile_otps SET is_verified = 1 WHERE id = %s", (record["id"],))

    # Generate HMAC-signed verification token
    verification_token = generate_verification_token(mobile, purpose)

    return jsonify({
        "success": True,
        "message": "Mobile number verified successfully!",
        "verification_token": verification_token,
        "mobile": mobile
    }), 200

# ========================================================
# REGISTRATION WITH MANDATORY OTP VERIFICATION
# ========================================================

@auth_bp.route("/patient/register", methods=["POST"])
def register_patient():
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    raw_mobile = data.get("mobile", "").strip()
    age = data.get("age")
    gender = data.get("gender", "Not Specified").strip()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")
    verification_token = data.get("verification_token", "").strip()

    # Input validations
    if not full_name or not email or not raw_mobile or not age or not password:
        return jsonify({"success": False, "message": "All required fields must be filled."}), 400
    
    if not validate_email(email):
        return jsonify({"success": False, "message": "Invalid email address format."}), 400

    if not validate_mobile(raw_mobile):
        return jsonify({"success": False, "message": "Invalid mobile number. Must contain at least 10 valid digits."}), 400

    mobile = normalize_mobile(raw_mobile)

    try:
        age_int = int(age)
        if age_int < 1 or age_int > 120:
            return jsonify({"success": False, "message": "Please enter a valid age between 1 and 120."}), 400
    except ValueError:
        return jsonify({"success": False, "message": "Age must be a valid number."}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long."}), 400

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400

    # Mandatory Mobile OTP Verification Check
    is_token_valid = verify_verification_token(verification_token, mobile, "registration")
    if not is_token_valid:
        # Fallback check database if token was somehow dropped
        db_verified = fetch_one(
            "SELECT id FROM mobile_otps WHERE mobile = %s AND purpose = 'registration' AND is_verified = 1 ORDER BY id DESC LIMIT 1",
            (mobile,)
        )
        if not db_verified:
            return jsonify({
                "success": False,
                "message": "Mobile number verification is mandatory. Please verify your mobile number with OTP before completing registration."
            }), 400

    # Check for existing email or mobile
    existing_patient = fetch_one("SELECT id FROM patients WHERE email = %s OR mobile = %s", (email, mobile))
    if existing_patient:
        return jsonify({"success": False, "message": "An account with this email or mobile number already exists."}), 409

    pwd_hash = hash_password(password)
    insert_sql = """
        INSERT INTO patients (full_name, email, mobile, age, gender, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        patient_id = execute_query(insert_sql, (full_name, email, mobile, age_int, gender, pwd_hash))
        # Consume the verified OTP
        execute_query("UPDATE mobile_otps SET is_verified = 2 WHERE mobile = %s", (mobile,))
        token = generate_token(patient_id, "patient", email, full_name)
        return jsonify({
            "success": True,
            "message": "Registration successful! Welcome to AyuCare.",
            "token": token,
            "user": {
                "id": patient_id,
                "role": "patient",
                "full_name": full_name,
                "email": email,
                "mobile": mobile,
                "age": age_int,
                "gender": gender
            }
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500

@auth_bp.route("/doctor/register", methods=["POST"])
def register_doctor():
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    raw_mobile = data.get("mobile", "").strip()
    specialization = data.get("specialization", "").strip()
    registration_number = data.get("registration_number", "").strip().upper()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")
    bio = data.get("bio", "").strip()
    experience_years = data.get("experience_years", 0)
    hospital_clinic = data.get("hospital_clinic", "").strip()
    verification_token = data.get("verification_token", "").strip()

    if not full_name or not email or not raw_mobile or not specialization or not registration_number or not password:
        return jsonify({"success": False, "message": "Please fill in all required doctor registration fields."}), 400

    if not validate_email(email):
        return jsonify({"success": False, "message": "Invalid email address format."}), 400

    if not validate_mobile(raw_mobile):
        return jsonify({"success": False, "message": "Invalid mobile number format."}), 400

    mobile = normalize_mobile(raw_mobile)

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long."}), 400

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400

    # Mandatory Mobile OTP Verification Check
    is_token_valid = verify_verification_token(verification_token, mobile, "registration")
    if not is_token_valid:
        db_verified = fetch_one(
            "SELECT id FROM mobile_otps WHERE mobile = %s AND purpose = 'registration' AND is_verified = 1 ORDER BY id DESC LIMIT 1",
            (mobile,)
        )
        if not db_verified:
            return jsonify({
                "success": False,
                "message": "Mobile number verification is mandatory. Please verify your mobile number with OTP before completing doctor registration."
            }), 400

    existing_doc = fetch_one(
        "SELECT id FROM doctors WHERE email = %s OR mobile = %s OR registration_number = %s",
        (email, mobile, registration_number)
    )
    if existing_doc:
        return jsonify({"success": False, "message": "A doctor with this email, mobile, or medical registration number is already registered."}), 409

    pwd_hash = hash_password(password)
    insert_sql = """
        INSERT INTO doctors (full_name, email, mobile, specialization, registration_number, password_hash, verification_status, bio, experience_years, hospital_clinic)
        VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s, %s, %s)
    """
    try:
        doc_id = execute_query(insert_sql, (
            full_name, email, mobile, specialization, registration_number,
            pwd_hash, bio, int(experience_years or 0), hospital_clinic
        ))
        # Consume verified OTP
        execute_query("UPDATE mobile_otps SET is_verified = 2 WHERE mobile = %s", (mobile,))
        token = generate_token(doc_id, "doctor", email, full_name)
        return jsonify({
            "success": True,
            "message": "Doctor registration submitted successfully! Your account verification is currently pending credential review.",
            "token": token,
            "user": {
                "id": doc_id,
                "role": "doctor",
                "full_name": full_name,
                "email": email,
                "specialization": specialization,
                "registration_number": registration_number,
                "verification_status": "pending"
            }
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500

# ========================================================
# LOGIN & LOGOUT ENDPOINTS
# ========================================================

@auth_bp.route("/patient/login", methods=["POST"])
def login_patient():
    data = request.get_json() or {}
    identifier = data.get("identifier", "").strip().lower()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"success": False, "message": "Email/Mobile and password are required."}), 400

    patient = fetch_one(
        "SELECT id, full_name, email, mobile, age, gender, password_hash FROM patients WHERE email = %s OR mobile = %s",
        (identifier, identifier)
    )

    if not patient or not check_password(password, patient["password_hash"]):
        return jsonify({"success": False, "message": "Invalid email/mobile or password."}), 401

    token = generate_token(patient["id"], "patient", patient["email"], patient["full_name"])
    return jsonify({
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": {
            "id": patient["id"],
            "role": "patient",
            "full_name": patient["full_name"],
            "email": patient["email"],
            "mobile": patient["mobile"],
            "age": patient["age"],
            "gender": patient["gender"]
        }
    }), 200

@auth_bp.route("/doctor/login", methods=["POST"])
def login_doctor():
    data = request.get_json() or {}
    identifier = data.get("identifier", "").strip().lower()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"success": False, "message": "Email/Registration number and password are required."}), 400

    doctor = fetch_one(
        "SELECT id, full_name, email, mobile, specialization, registration_number, password_hash, verification_status, bio, experience_years, hospital_clinic FROM doctors WHERE email = %s OR registration_number = %s",
        (identifier, identifier.upper())
    )

    if not doctor or not check_password(password, doctor["password_hash"]):
        return jsonify({"success": False, "message": "Invalid doctor credentials."}), 401

    token = generate_token(doctor["id"], "doctor", doctor["email"], doctor["full_name"])
    return jsonify({
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": {
            "id": doctor["id"],
            "role": "doctor",
            "full_name": doctor["full_name"],
            "email": doctor["email"],
            "mobile": doctor["mobile"],
            "specialization": doctor["specialization"],
            "registration_number": doctor["registration_number"],
            "verification_status": doctor["verification_status"],
            "bio": doctor["bio"],
            "experience_years": doctor["experience_years"],
            "hospital_clinic": doctor["hospital_clinic"]
        }
    }), 200

@auth_bp.route("/me", methods=["GET"])
def get_current_profile():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated."}), 401

    user_id = user["user_id"]
    role = user["role"]

    if role == "patient":
        profile = fetch_one("SELECT id, full_name, email, mobile, age, gender, created_at FROM patients WHERE id = %s", (user_id,))
    elif role == "doctor":
        profile = fetch_one("SELECT id, full_name, email, mobile, specialization, registration_number, verification_status, bio, experience_years, hospital_clinic, created_at FROM doctors WHERE id = %s", (user_id,))
    else:
        return jsonify({"success": False, "message": "Unknown role."}), 400

    if not profile:
        return jsonify({"success": False, "message": "User not found."}), 404

    profile["role"] = role
    return jsonify({"success": True, "user": profile}), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"success": True, "message": "Logged out successfully."}), 200

# ========================================================
# FORGOT PASSWORD & RESET PASSWORD (PRODUCTION SMTP)
# ========================================================

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Generates a secure password reset token and attempts real email delivery via SMTP.
    If SMTP is not configured, provides clear guidance and never simulates delivery falsely.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    role = data.get("role", "patient").strip().lower()

    if not email:
        return jsonify({"success": False, "message": "Email address is required."}), 400

    if not validate_email(email):
        return jsonify({"success": False, "message": "Invalid email address format."}), 400

    table = "patients" if role == "patient" else "doctors"
    user = fetch_one(f"SELECT id, full_name, email FROM {table} WHERE email = %s", (email,))

    if not user:
        return jsonify({
            "success": False,
            "message": f"No {role} account found matching '{email}'. Please check your spelling or register for a new account."
        }), 404

    # Generate secure 64-char URL safe token
    token = generate_reset_token()
    now = datetime.datetime.now()
    expires_at = (now + datetime.timedelta(hours=Config.PASSWORD_RESET_EXPIRATION_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")

    # Invalidate any previous unexpired tokens for this user
    execute_query(
        "UPDATE password_resets SET is_used = 1 WHERE user_id = %s AND role = %s AND is_used = 0",
        (user["id"], role)
    )

    # Insert new reset token
    insert_sql = """
        INSERT INTO password_resets (user_id, role, email, token, expires_at, is_used, created_at)
        VALUES (%s, %s, %s, %s, %s, 0, %s)
    """
    execute_query(insert_sql, (user["id"], role, email, token, expires_at, created_at))

    # Construct password reset URL
    reset_url = f"{Config.FRONTEND_BASE_URL}/reset-password.html?token={token}"

    # Attempt real email dispatch via SMTP
    try:
        send_password_reset_email(email, reset_url, user["full_name"])
        return jsonify({
            "success": True,
            "message": f"A password reset link has been dispatched to {email}. Please check your inbox and spam folder.",
            "token": token,
            "reset_url": reset_url
        }), 200
    except SMTPNotConfiguredError as smtp_err:
        logger.warning(f"Forgot password SMTP unconfigured: {smtp_err}")
        return jsonify({
            "success": True,
            "email_dispatched": False,
            "message": "Password reset token generated. Note: SMTP email service is currently not configured in .env. Please configure SMTP_HOST, SMTP_PORT, SMTP_USER, and SMTP_PASSWORD.",
            "token": token,
            "reset_url": reset_url,
            "dev_reset_url": reset_url
        }), 200
    except EmailDeliveryError as delivery_err:
        logger.error(f"Failed to dispatch password reset email: {delivery_err}")
        return jsonify({
            "success": False,
            "message": f"Email delivery failed: {str(delivery_err)}. Please verify SMTP settings in .env."
        }), 502

@auth_bp.route("/reset-password/verify", methods=["GET"])
def verify_reset_token():
    """
    Validates a password reset token before rendering the reset form.
    Checks existence, expiration, and whether already used.
    """
    token = request.args.get("token", "").strip()
    if not token:
        return jsonify({"success": False, "valid": False, "message": "Reset token is missing."}), 400

    record = fetch_one(
        "SELECT id, user_id, role, email, expires_at, is_used FROM password_resets WHERE token = %s",
        (token,)
    )

    if not record or record.get("is_used") == 1:
        return jsonify({
            "success": False,
            "valid": False,
            "message": "This password reset link is invalid or has already been used. Please request a new link."
        }), 400

    # Expiry verification
    now = datetime.datetime.now()
    exp_val = record.get("expires_at")
    if isinstance(exp_val, str):
        try:
            clean_ts = exp_val.split(".")[0].replace("T", " ")
            exp_dt = datetime.datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")
        except Exception:
            exp_dt = now
    elif isinstance(exp_val, datetime.datetime):
        exp_dt = exp_val
    else:
        exp_dt = now

    if now > exp_dt:
        return jsonify({
            "success": False,
            "valid": False,
            "message": "This password reset link has expired. Password reset links are valid for 1 hour. Please request a new link."
        }), 400

    return jsonify({
        "success": True,
        "valid": True,
        "email": record["email"],
        "role": record["role"]
    }), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Updates the user's password using the verified reset token.
    Applies secure PBKDF2 hashing and marks the token as used.
    """
    data = request.get_json() or {}
    token = data.get("token", "").strip()
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not token or not new_password:
        return jsonify({"success": False, "message": "Token and new password are required."}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long."}), 400

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "New password and confirm password do not match."}), 400

    record = fetch_one(
        "SELECT id, user_id, role, email, expires_at, is_used FROM password_resets WHERE token = %s",
        (token,)
    )

    if not record or record.get("is_used") == 1:
        return jsonify({
            "success": False,
            "message": "This password reset link is invalid or has already been used."
        }), 400

    # Check expiration
    now = datetime.datetime.now()
    exp_val = record.get("expires_at")
    if isinstance(exp_val, str):
        try:
            clean_ts = exp_val.split(".")[0].replace("T", " ")
            exp_dt = datetime.datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")
        except Exception:
            exp_dt = now
    elif isinstance(exp_val, datetime.datetime):
        exp_dt = exp_val
    else:
        exp_dt = now

    if now > exp_dt:
        return jsonify({
            "success": False,
            "message": "This password reset link has expired. Please request a new link."
        }), 400

    # Hash new password
    pwd_hash = hash_password(new_password)
    table = "patients" if record["role"] == "patient" else "doctors"

    try:
        # Update password in user table
        execute_query(f"UPDATE {table} SET password_hash = %s WHERE id = %s", (pwd_hash, record["user_id"]))
        # Mark token as used
        execute_query("UPDATE password_resets SET is_used = 1 WHERE id = %s", (record["id"],))

        return jsonify({
            "success": True,
            "message": "Password reset successful! You can now log in with your new password.",
            "role": record["role"]
        }), 200
    except Exception as e:
        logger.error(f"Failed to reset password: {e}")
        return jsonify({"success": False, "message": f"Failed to update password: {str(e)}"}), 500
