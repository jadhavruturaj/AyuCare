from flask import Blueprint, request, jsonify
from database import fetch_all, fetch_one
from services.symptom_service import process_symptom_submission
from services.auth_service import get_current_user, login_required

symptom_bp = Blueprint("symptoms", __name__, url_prefix="/api/symptoms")

@symptom_bp.route("", methods=["GET"])
def get_all_symptoms():
    """Returns list of all available symptoms with categories and specialist mapping."""
    sql = """
        SELECT s.id, s.name, s.category, s.description, s.urgency_level,
               sp.name as specialist_name, sp.icon as specialist_icon
        FROM symptoms s
        LEFT JOIN specialists sp ON s.specialist_id = sp.id
        ORDER BY s.name ASC
    """
    symptoms = fetch_all(sql)
    return jsonify({
        "success": True,
        "count": len(symptoms),
        "symptoms": symptoms
    }), 200

@symptom_bp.route("/<int:symptom_id>", methods=["GET"])
def get_symptom_detail(symptom_id):
    """Returns full guidance for a single symptom."""
    sql = """
        SELECT s.id, s.name, s.category, s.description, s.urgency_level, s.warning_signs,
               sp.name as specialist_name, sp.description as specialist_desc, sp.icon as specialist_icon,
               sg.preliminary_guidance, sg.mild_home_care, sg.reference_source
        FROM symptoms s
        LEFT JOIN specialists sp ON s.specialist_id = sp.id
        LEFT JOIN symptom_guidance sg ON s.id = sg.symptom_id
        WHERE s.id = %s
    """
    symptom = fetch_one(sql, (symptom_id,))
    if not symptom:
        return jsonify({"success": False, "message": "Symptom not found."}), 404
    return jsonify({"success": True, "symptom": symptom}), 200

@symptom_bp.route("/check", methods=["POST"])
def check_symptoms():
    """
    Processes symptom submission form:
    Checks emergency red-flags, queries database, applies rule-based logic,
    and returns report with preliminary guidance and recommended specialist.
    """
    data = request.get_json() or {}
    symptom_name = data.get("symptom_name", "").strip()
    duration = data.get("duration", "").strip()
    severity = data.get("severity", "Mild").strip()
    description = data.get("description", "").strip()
    additional_details = data.get("additional_details", "").strip()

    if not symptom_name or not duration or not severity:
        return jsonify({
            "success": False,
            "message": "Symptom name, duration, and severity level are required."
        }), 400

    # Determine if a patient is logged in to associate with history
    user = get_current_user()
    patient_id = user["user_id"] if user and user.get("role") == "patient" else None

    try:
        report = process_symptom_submission(
            symptom_name=symptom_name,
            duration=duration,
            severity=severity,
            description=description,
            additional_details=additional_details,
            patient_id=patient_id
        )
        return jsonify({
            "success": True,
            "report": report
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error evaluating symptoms: {str(e)}"
        }), 500

@symptom_bp.route("/history", methods=["GET"])
@login_required(role="patient")
def get_patient_history():
    """Returns patient's previous symptom submissions."""
    user = request.user
    patient_id = user["user_id"]
    sql = """
        SELECT id, symptom_name, duration, severity, description,
               is_emergency, guidance_summary, home_care_summary,
               recommended_specialist, created_at
        FROM symptom_history
        WHERE patient_id = %s
        ORDER BY created_at DESC
    """
    history = fetch_all(sql, (patient_id,))
    return jsonify({
        "success": True,
        "history": history
    }), 200

@symptom_bp.route("/history/<int:history_id>", methods=["GET"])
@login_required(role="patient")
def get_patient_history_item(history_id):
    """Returns a specific past symptom submission for the authenticated patient."""
    user = request.user
    patient_id = user["user_id"]
    sql = """
        SELECT * FROM symptom_history
        WHERE id = %s AND patient_id = %s
    """
    item = fetch_one(sql, (history_id, patient_id))
    if not item:
        return jsonify({"success": False, "message": "History record not found."}), 404
    return jsonify({"success": True, "record": item}), 200
