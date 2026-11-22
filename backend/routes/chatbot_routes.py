from flask import Blueprint, request, jsonify
from database import fetch_all
from services.chatbot_service import analyze_chatbot_query, DEFAULT_SUGGESTED_QUESTIONS

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")

@chatbot_bp.route("/faqs", methods=["GET"])
def get_chatbot_faqs():
    """Returns FAQ list for suggested questions and knowledge base."""
    faqs = fetch_all("SELECT id, category, question, answer FROM chatbot_faqs ORDER BY id ASC")
    return jsonify({
        "success": True,
        "faqs": faqs,
        "suggested_questions": DEFAULT_SUGGESTED_QUESTIONS
    }), 200

@chatbot_bp.route("/message", methods=["POST"])
def send_chatbot_message():
    """
    Receives user message, analyzes with safety checks and FAQ matching,
    and returns friendly informational response.
    """
    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "success": False,
            "message": "Message text is required."
        }), 400

    response = analyze_chatbot_query(message)
    return jsonify({
        "success": True,
        "data": response
    }), 200
