import re
from database import fetch_all, fetch_one

EMERGENCY_TRIGGERS = [
    "chest pain", "heart attack", "can't breathe", "cannot breathe", "stroke",
    "slurred speech", "vomiting blood", "coughing blood", "unconscious",
    "severe bleeding", "overdose", "suicide", "dying"
]

DEFAULT_SUGGESTED_QUESTIONS = [
    "How does AyuCare work?",
    "How do I check my symptoms?",
    "Which specialist should I consult?",
    "What information should I enter?",
    "How can I request a consultation?",
    "Is AyuCare a diagnosis tool?"
]

def analyze_chatbot_query(user_message: str) -> dict:
    """
    Evaluates user message:
    1. Checks for life-threatening emergency words.
    2. Searches predefined chatbot_faqs table with keyword scoring.
    3. Returns structured answer, recommended actions, and suggested questions.
    """
    clean_msg = user_message.strip()
    msg_lower = clean_msg.lower()

    # 1. Emergency detection
    for trigger in EMERGENCY_TRIGGERS:
        if trigger in msg_lower:
            return {
                "sender": "AyuBot",
                "message": (
                    "⚠️ **IMMEDIATE EMERGENCY WARNING**: Your message mentions severe symptoms or urgent distress. "
                    "AyuCare is an informational tool and cannot manage medical emergencies. "
                    "**Please call your local emergency service (112 / 108 / 911) or visit the nearest hospital emergency room right now.**"
                ),
                "is_emergency": True,
                "action_link": None,
                "suggested_questions": ["How do I check my symptoms?", "Which specialist should I consult?"]
            }

    # 2. Query chatbot_faqs from DB
    faqs = fetch_all("SELECT id, category, keywords, question, answer FROM chatbot_faqs")
    best_match = None
    highest_score = 0

    user_words = set(re.findall(r'\b\w+\b', msg_lower))

    for faq in faqs:
        keywords = [k.strip().lower() for k in faq["keywords"].split(",")]
        score = 0
        for kw in keywords:
            if kw in msg_lower:
                score += 3
            # Check individual word overlaps
            kw_words = set(re.findall(r'\b\w+\b', kw))
            overlap = len(user_words.intersection(kw_words))
            score += overlap

        if score > highest_score:
            highest_score = score
            best_match = faq

    # 3. Formulate response
    if best_match and highest_score >= 2:
        answer_text = best_match["answer"]
        action_link = None
        if "symptom" in best_match["category"].lower() or "check" in msg_lower:
            action_link = {"label": "Go to Symptom Checker", "url": "symptom-checker.html"}
        elif "specialist" in best_match["category"].lower() or "doctor" in msg_lower:
            action_link = {"label": "Explore Specialists", "url": "specialists.html"}
        elif "account" in best_match["category"].lower() or "register" in msg_lower:
            action_link = {"label": "Patient Registration", "url": "register.html"}

        return {
            "sender": "AyuBot",
            "message": answer_text,
            "is_emergency": False,
            "category": best_match["category"],
            "action_link": action_link,
            "suggested_questions": DEFAULT_SUGGESTED_QUESTIONS[:4]
        }
    else:
        # Fallback friendly response
        fallback_msg = (
            "Hello! I am **AyuBot**, your AyuCare health guide. "
            "I can explain how to use our Symptom Checker, how to connect with specialists, "
            "or help you navigate the platform.\n\n"
            "*(Reminder: AyuCare provides educational guidance and is not a substitute for professional medical advice.)*"
        )
        return {
            "sender": "AyuBot",
            "message": fallback_msg,
            "is_emergency": False,
            "action_link": {"label": "Check Symptoms Now", "url": "symptom-checker.html"},
            "suggested_questions": DEFAULT_SUGGESTED_QUESTIONS
        }
