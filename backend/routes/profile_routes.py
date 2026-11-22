from flask import Blueprint, request, jsonify
from database import fetch_one, fetch_all, execute_query
from services.auth_service import login_required, validate_mobile

profile_bp = Blueprint("profile", __name__, url_prefix="/api")

@profile_bp.route("/patient/dashboard", methods=["GET"])
@login_required(role="patient")
def patient_dashboard():
    """Returns dashboard summary data for patient."""
    user = request.user
    patient_id = user["user_id"]

    patient = fetch_one("SELECT id, full_name, email, mobile, age, gender, created_at FROM patients WHERE id = %s", (patient_id,))
    
    # Counts
    sym_count = fetch_one("SELECT COUNT(*) as cnt FROM symptom_history WHERE patient_id = %s", (patient_id,))
    consult_count = fetch_one("SELECT COUNT(*) as cnt FROM consultations WHERE patient_id = %s", (patient_id,))
    pending_consult_count = fetch_one("SELECT COUNT(*) as cnt FROM consultations WHERE patient_id = %s AND status = 'Pending'", (patient_id,))

    # Recent symptoms
    recent_symptoms = fetch_all(
        "SELECT id, symptom_name, severity, duration, recommended_specialist, is_emergency, created_at FROM symptom_history WHERE patient_id = %s ORDER BY created_at DESC LIMIT 5",
        (patient_id,)
    )

    # Recent consultations
    recent_consultations = fetch_all(
        """
        SELECT c.id, c.preferred_date, c.preferred_time, c.status, c.created_at,
               d.full_name as doctor_name, d.specialization as doctor_specialization
        FROM consultations c
        JOIN doctors d ON c.doctor_id = d.id
        WHERE c.patient_id = %s
        ORDER BY c.created_at DESC LIMIT 5
        """,
        (patient_id,)
    )

    return jsonify({
        "success": True,
        "profile": patient,
        "stats": {
            "total_symptom_checks": sym_count["cnt"] if sym_count else 0,
            "total_consultations": consult_count["cnt"] if consult_count else 0,
            "pending_consultations": pending_consult_count["cnt"] if pending_consult_count else 0
        },
        "recent_symptoms": recent_symptoms,
        "recent_consultations": recent_consultations
    }), 200

@profile_bp.route("/doctor/dashboard", methods=["GET"])
@login_required(role="doctor")
def doctor_dashboard():
    """Returns dashboard summary data for doctor."""
    user = request.user
    doctor_id = user["user_id"]

    doctor = fetch_one(
        "SELECT id, full_name, email, mobile, specialization, registration_number, verification_status, bio, experience_years, hospital_clinic, created_at FROM doctors WHERE id = %s",
        (doctor_id,)
    )

    # Counts
    total_requests = fetch_one("SELECT COUNT(*) as cnt FROM consultations WHERE doctor_id = %s", (doctor_id,))
    pending_requests = fetch_one("SELECT COUNT(*) as cnt FROM consultations WHERE doctor_id = %s AND status = 'Pending'", (doctor_id,))
    accepted_requests = fetch_one("SELECT COUNT(*) as cnt FROM consultations WHERE doctor_id = %s AND status = 'Accepted'", (doctor_id,))
    completed_requests = fetch_one("SELECT COUNT(*) as cnt FROM consultations WHERE doctor_id = %s AND status = 'Completed'", (doctor_id,))

    # Recent consultations
    recent_consultations = fetch_all(
        """
        SELECT c.id, c.symptom_summary, c.preferred_date, c.preferred_time, c.notes,
               c.status, c.doctor_notes, c.created_at,
               p.full_name as patient_name, p.age as patient_age, p.gender as patient_gender,
               p.mobile as patient_mobile
        FROM consultations c
        JOIN patients p ON c.patient_id = p.id
        WHERE c.doctor_id = %s
        ORDER BY c.created_at DESC
        """,
        (doctor_id,)
    )

    return jsonify({
        "success": True,
        "profile": doctor,
        "stats": {
            "total_requests": total_requests["cnt"] if total_requests else 0,
            "pending_requests": pending_requests["cnt"] if pending_requests else 0,
            "accepted_requests": accepted_requests["cnt"] if accepted_requests else 0,
            "completed_requests": completed_requests["cnt"] if completed_requests else 0
        },
        "consultations": recent_consultations
    }), 200

@profile_bp.route("/patient/profile", methods=["PUT"])
@login_required(role="patient")
def update_patient_profile():
    user = request.user
    patient_id = user["user_id"]
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    mobile = data.get("mobile", "").strip()
    age = data.get("age")
    gender = data.get("gender", "Not Specified").strip()

    if not full_name or not mobile or not age:
        return jsonify({"success": False, "message": "Name, mobile, and age are required."}), 400

    if not validate_mobile(mobile):
        return jsonify({"success": False, "message": "Invalid mobile number."}), 400

    sql = "UPDATE patients SET full_name = %s, mobile = %s, age = %s, gender = %s WHERE id = %s"
    try:
        execute_query(sql, (full_name, mobile, int(age), gender, patient_id))
        return jsonify({"success": True, "message": "Profile updated successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Update failed: {str(e)}"}), 500

@profile_bp.route("/doctor/profile", methods=["PUT"])
@login_required(role="doctor")
def update_doctor_profile():
    user = request.user
    doctor_id = user["user_id"]
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    mobile = data.get("mobile", "").strip()
    bio = data.get("bio", "").strip()
    experience_years = data.get("experience_years", 0)
    hospital_clinic = data.get("hospital_clinic", "").strip()

    if not full_name or not mobile:
        return jsonify({"success": False, "message": "Full name and mobile are required."}), 400

    sql = """
        UPDATE doctors
        SET full_name = %s, mobile = %s, bio = %s, experience_years = %s, hospital_clinic = %s
        WHERE id = %s
    """
    try:
        execute_query(sql, (full_name, mobile, bio, int(experience_years or 0), hospital_clinic, doctor_id))
        return jsonify({"success": True, "message": "Doctor profile updated successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Update failed: {str(e)}"}), 500
