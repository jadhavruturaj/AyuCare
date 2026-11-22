from flask import Blueprint, request, jsonify
from database import fetch_one, execute_query
from services.auth_service import (
    hash_password, check_password, generate_token,
    validate_email, validate_mobile, get_current_user, login_required
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/patient/register", methods=["POST"])
def register_patient():
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    mobile = data.get("mobile", "").strip()
    age = data.get("age")
    gender = data.get("gender", "Not Specified").strip()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    # Input validations
    if not full_name or not email or not mobile or not age or not password:
        return jsonify({"success": False, "message": "All required fields must be filled."}), 400
    
    if not validate_email(email):
        return jsonify({"success": False, "message": "Invalid email address format."}), 400

    if not validate_mobile(mobile):
        return jsonify({"success": False, "message": "Invalid mobile number. Must be 10-15 digits."}), 400

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

@auth_bp.route("/patient/login", methods=["POST"])
def login_patient():
    data = request.get_json() or {}
    identifier = data.get("identifier", "").strip().lower()  # Email or mobile
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

@auth_bp.route("/doctor/register", methods=["POST"])
def register_doctor():
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    mobile = data.get("mobile", "").strip()
    specialization = data.get("specialization", "").strip()
    registration_number = data.get("registration_number", "").strip().upper()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")
    bio = data.get("bio", "").strip()
    experience_years = data.get("experience_years", 0)
    hospital_clinic = data.get("hospital_clinic", "").strip()

    if not full_name or not email or not mobile or not specialization or not registration_number or not password:
        return jsonify({"success": False, "message": "Please fill in all required doctor registration fields."}), 400

    if not validate_email(email):
        return jsonify({"success": False, "message": "Invalid email address format."}), 400

    if not validate_mobile(mobile):
        return jsonify({"success": False, "message": "Invalid mobile number format."}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long."}), 400

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400

    existing_doc = fetch_one(
        "SELECT id FROM doctors WHERE email = %s OR mobile = %s OR registration_number = %s",
        (email, mobile, registration_number)
    )
    if existing_doc:
        return jsonify({"success": False, "message": "A doctor with this email, mobile, or medical registration number is already registered."}), 409

    pwd_hash = hash_password(password)
    # Doctor accounts start in 'pending' verification status per prompt requirements
    insert_sql = """
        INSERT INTO doctors (full_name, email, mobile, specialization, registration_number, password_hash, verification_status, bio, experience_years, hospital_clinic)
        VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s, %s, %s)
    """
    try:
        doc_id = execute_query(insert_sql, (
            full_name, email, mobile, specialization, registration_number,
            pwd_hash, bio, int(experience_years or 0), hospital_clinic
        ))
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

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    role = data.get("role", "patient")

    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400

    # In this student/educational prototype, we verify email existence and return a simulated reset token / success message
    table = "patients" if role == "patient" else "doctors"
    user = fetch_one(f"SELECT id, full_name FROM {table} WHERE email = %s", (email,))
    
    if user:
        return jsonify({
            "success": True,
            "message": f"Password reset instructions have been simulated for {email}. In a production environment, an email with a secure reset link would be sent."
        }), 200
    else:
        # Return generic safe message to prevent email enumeration
        return jsonify({
            "success": True,
            "message": "If this email is registered in our system, you will receive password reset instructions."
        }), 200
