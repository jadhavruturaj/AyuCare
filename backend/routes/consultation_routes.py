from flask import Blueprint, request, jsonify
from database import fetch_all, fetch_one, execute_query
from services.auth_service import login_required

consultation_bp = Blueprint("consultations", __name__, url_prefix="/api/consultations")

@consultation_bp.route("", methods=["POST"])
@login_required(role="patient")
def create_consultation():
    """
    Patient submits a consultation request to a specific doctor.
    """
    patient = request.user
    data = request.get_json() or {}
    doctor_id = data.get("doctor_id")
    symptom_summary = data.get("symptom_summary", "").strip()
    preferred_date = data.get("preferred_date", "").strip()
    preferred_time = data.get("preferred_time", "").strip()
    notes = data.get("notes", "").strip()

    if not doctor_id:
        return jsonify({"success": False, "message": "Doctor ID is required."}), 400

    # Ensure doctor exists and is verified
    doctor = fetch_one("SELECT id, full_name, verification_status FROM doctors WHERE id = %s", (doctor_id,))
    if not doctor:
        return jsonify({"success": False, "message": "Selected doctor does not exist."}), 404

    sql = """
        INSERT INTO consultations (patient_id, doctor_id, symptom_summary, preferred_date, preferred_time, notes, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
    """
    try:
        consultation_id = execute_query(sql, (
            patient["user_id"], doctor_id, symptom_summary, preferred_date, preferred_time, notes
        ))
        return jsonify({
            "success": True,
            "message": f"Consultation request successfully submitted to Dr. {doctor['full_name']}!",
            "consultation_id": consultation_id,
            "status": "Pending"
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to submit consultation: {str(e)}"}), 500

@consultation_bp.route("/patient", methods=["GET"])
@login_required(role="patient")
def get_patient_consultations():
    """
    Returns all consultation requests submitted by the logged-in patient.
    """
    patient = request.user
    sql = """
        SELECT c.id, c.symptom_summary, c.preferred_date, c.preferred_time, c.notes,
               c.status, c.doctor_notes, c.created_at,
               d.full_name as doctor_name, d.specialization as doctor_specialization,
               d.hospital_clinic as doctor_clinic, d.email as doctor_email
        FROM consultations c
        JOIN doctors d ON c.doctor_id = d.id
        WHERE c.patient_id = %s
        ORDER BY c.created_at DESC
    """
    consultations = fetch_all(sql, (patient["user_id"],))
    return jsonify({
        "success": True,
        "count": len(consultations),
        "consultations": consultations
    }), 200

@consultation_bp.route("/doctor", methods=["GET"])
@login_required(role="doctor")
def get_doctor_consultations():
    """
    Returns consultation requests submitted ONLY to this logged-in doctor.
    Protects patient privacy: only displays patient info authorized for this doctor.
    """
    doctor = request.user
    sql = """
        SELECT c.id, c.patient_id, c.symptom_summary, c.preferred_date, c.preferred_time, c.notes,
               c.status, c.doctor_notes, c.created_at,
               p.full_name as patient_name, p.age as patient_age, p.gender as patient_gender,
               p.mobile as patient_mobile, p.email as patient_email
        FROM consultations c
        JOIN patients p ON c.patient_id = p.id
        WHERE c.doctor_id = %s
        ORDER BY c.created_at DESC
    """
    consultations = fetch_all(sql, (doctor["user_id"],))
    return jsonify({
        "success": True,
        "count": len(consultations),
        "consultations": consultations
    }), 200

@consultation_bp.route("/<int:consultation_id>/status", methods=["PATCH"])
@login_required(role="doctor")
def update_consultation_status(consultation_id):
    """
    Doctor updates consultation status (Accepted, Rejected, Completed) and adds clinical doctor notes.
    """
    doctor = request.user
    data = request.get_json() or {}
    new_status = data.get("status", "").strip().capitalize()
    doctor_notes = data.get("doctor_notes", "").strip()

    valid_statuses = ["Pending", "Accepted", "Rejected", "Completed"]
    if new_status not in valid_statuses:
        return jsonify({
            "success": False,
            "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }), 400

    # Ensure this consultation belongs to the requesting doctor
    consultation = fetch_one(
        "SELECT id, patient_id FROM consultations WHERE id = %s AND doctor_id = %s",
        (consultation_id, doctor["user_id"])
    )
    if not consultation:
        return jsonify({
            "success": False,
            "message": "Consultation not found or you are not authorized to update it."
        }), 404

    sql = """
        UPDATE consultations
        SET status = %s, doctor_notes = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND doctor_id = %s
    """
    try:
        execute_query(sql, (new_status, doctor_notes, consultation_id, doctor["user_id"]))
        return jsonify({
            "success": True,
            "message": f"Consultation status successfully updated to {new_status}."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to update status: {str(e)}"}), 500
