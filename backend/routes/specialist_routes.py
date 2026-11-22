from flask import Blueprint, request, jsonify
from database import fetch_all, fetch_one

specialist_bp = Blueprint("specialists", __name__, url_prefix="/api")

@specialist_bp.route("/specialists", methods=["GET"])
def get_specialists():
    """Returns all 11 specialist categories."""
    specialists = fetch_all("SELECT id, name, description, common_conditions, icon FROM specialists ORDER BY name ASC")
    return jsonify({
        "success": True,
        "specialists": specialists
    }), 200

@specialist_bp.route("/specialists/<int:specialist_id>", methods=["GET"])
def get_specialist_detail(specialist_id):
    """Returns a specific specialist category with doctors."""
    spec = fetch_one("SELECT id, name, description, common_conditions, icon FROM specialists WHERE id = %s", (specialist_id,))
    if not spec:
        return jsonify({"success": False, "message": "Specialist category not found."}), 404

    # Fetch verified doctors in this category
    docs = fetch_all(
        "SELECT id, full_name, email, specialization, registration_number, verification_status, bio, experience_years, hospital_clinic FROM doctors WHERE specialization = %s AND verification_status = 'verified'",
        (spec["name"],)
    )
    spec["doctors"] = docs
    return jsonify({"success": True, "specialist": spec}), 200

@specialist_bp.route("/doctors", methods=["GET"])
def get_doctors():
    """
    Returns verified doctors.
    Optional query params:
    ?specialization=Dermatologist
    ?verified_only=true (default true per prompt requirements)
    """
    specialization = request.args.get("specialization", "").strip()
    verified_only = request.args.get("verified_only", "true").lower() == "true"

    conditions = []
    params = []

    if verified_only:
        conditions.append("verification_status = 'verified'")

    if specialization:
        conditions.append("LOWER(specialization) = LOWER(%s)")
        params.append(specialization)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"""
        SELECT id, full_name, specialization, registration_number, verification_status,
               bio, experience_years, hospital_clinic
        FROM doctors
        {where_clause}
        ORDER BY experience_years DESC, full_name ASC
    """
    doctors = fetch_all(sql, tuple(params))
    return jsonify({
        "success": True,
        "count": len(doctors),
        "doctors": doctors
    }), 200

@specialist_bp.route("/doctors/<int:doctor_id>", methods=["GET"])
def get_doctor_profile(doctor_id):
    """Returns public profile of a doctor."""
    doctor = fetch_one(
        "SELECT id, full_name, specialization, registration_number, verification_status, bio, experience_years, hospital_clinic FROM doctors WHERE id = %s",
        (doctor_id,)
    )
    if not doctor:
        return jsonify({"success": False, "message": "Doctor not found."}), 404
    return jsonify({"success": True, "doctor": doctor}), 200
