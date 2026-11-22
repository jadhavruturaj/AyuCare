from flask import Blueprint, request, jsonify
from database import execute_query
from services.auth_service import validate_email

contact_bp = Blueprint("contact", __name__, url_prefix="/api/contact")

@contact_bp.route("", methods=["POST"])
def submit_contact_message():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()
    feedback_type = data.get("feedback_type", "General Inquiry").strip()

    if not name or not email or not subject or not message:
        return jsonify({
            "success": False,
            "message": "All fields (Name, Email, Subject, Message) are required."
        }), 400

    if not validate_email(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    sql = """
        INSERT INTO contact_messages (name, email, subject, message, feedback_type)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        msg_id = execute_query(sql, (name, email, subject, message, feedback_type))
        return jsonify({
            "success": True,
            "message": "Thank you for reaching out! Your message has been received and our team will get back to you shortly.",
            "message_id": msg_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to submit message: {str(e)}"}), 500
