import re
from database import fetch_one, fetch_all, execute_query

# Red-flag emergency phrases requiring immediate escalation
EMERGENCY_KEYWORDS = [
    "chest pain", "pressure in chest", "radiating to left arm", "radiating to jaw",
    "shortness of breath", "difficulty breathing", "cannot breathe", "gasping for air",
    "slurred speech", "facial droop", "face drooping", "sudden weakness", "paralysis",
    "coughing up blood", "vomiting blood", "black tarry stools",
    "stiff neck and fever", "unable to touch chin to chest", "convulsions", "seizure",
    "unconscious", "loss of consciousness", "fainting with chest pain",
    "throat closing", "swollen tongue", "anaphylaxis",
    "sudden loss of vision", "thunderclap headache", "worst headache of my life",
    "suicide", "self harm", "unbearable acute pain"
]

def detect_emergency_signs(symptom_name: str, severity: str, description: str, additional_details: str = "") -> dict:
    """
    Checks for high-priority emergency red flags in user input.
    Returns dict with is_emergency (bool), reasons (list), and action prompt.
    """
    text_corpus = f"{symptom_name} {description} {additional_details}".lower()
    detected_reasons = []

    for kw in EMERGENCY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_corpus):
            detected_reasons.append(kw.title())

    if severity.lower() == "severe":
        detected_reasons.append("Reported Severity is Severe")

    is_emergency = len(detected_reasons) > 0

    return {
        "is_emergency": is_emergency,
        "reasons": detected_reasons,
        "emergency_prompt": (
            "🚨 CRITICAL WARNING: Your reported symptoms contain emergency warning signs. "
            "Please call emergency healthcare services (112 / 108 / 911) or visit the nearest hospital emergency room immediately. "
            "Do NOT wait or rely on home care."
        ) if is_emergency else None
    }

def process_symptom_submission(symptom_name: str, duration: str, severity: str, description: str, additional_details: str = "", patient_id: int = None) -> dict:
    """
    Core symptom triage engine:
    1. Validates inputs.
    2. Runs emergency red-flag checks.
    3. Queries symptom dataset and guidance.
    4. Applies rule-based safety filtering.
    5. Formulates specialist recommendation.
    6. Saves record in patient history if patient_id is present.
    """
    if not symptom_name or not duration or not severity:
        raise ValueError("Symptom name, duration, and severity are required.")

    # Emergency check
    emergency_eval = detect_emergency_signs(symptom_name, severity, description, additional_details)
    is_emergency = emergency_eval["is_emergency"]

    # Search symptom dataset in database
    sql = """
        SELECT s.id, s.name, s.category, s.description, s.urgency_level, s.warning_signs,
               sp.name as specialist_name, sp.description as specialist_desc, sp.icon as specialist_icon,
               sg.preliminary_guidance, sg.mild_home_care, sg.warning_signs_details, sg.reference_source
        FROM symptoms s
        LEFT JOIN specialists sp ON s.specialist_id = sp.id
        LEFT JOIN symptom_guidance sg ON s.id = sg.symptom_id
        WHERE LOWER(s.name) = LOWER(%s)
    """
    symptom_data = fetch_one(sql, (symptom_name.strip(),))

    if not symptom_data:
        # Fallback search for partial match
        partial_sql = """
            SELECT s.id, s.name, s.category, s.description, s.urgency_level, s.warning_signs,
                   sp.name as specialist_name, sp.description as specialist_desc, sp.icon as specialist_icon,
                   sg.preliminary_guidance, sg.mild_home_care, sg.warning_signs_details, sg.reference_source
            FROM symptoms s
            LEFT JOIN specialists sp ON s.specialist_id = sp.id
            LEFT JOIN symptom_guidance sg ON s.id = sg.symptom_id
            WHERE LOWER(s.name) LIKE LOWER(%s) LIMIT 1
        """
        symptom_data = fetch_one(partial_sql, (f"%{symptom_name.strip()}%",))

    if symptom_data:
        matched_name = symptom_data["name"]
        specialist_name = symptom_data["specialist_name"] or "General Physician"
        specialist_desc = symptom_data["specialist_desc"] or "Primary care physician for comprehensive evaluation."
        specialist_icon = symptom_data["specialist_icon"] or "fa-user-doctor"
        guidance = symptom_data["preliminary_guidance"]
        warning_signs = symptom_data["warning_signs"]
        reference = symptom_data["reference_source"] or "WHO / Mayo Clinic Guidelines"
        
        # Rule: Only show mild home care if clinically safe AND user severity is 'Mild'
        if severity.lower() == "mild" and not is_emergency and symptom_data["mild_home_care"]:
            home_care = symptom_data["mild_home_care"]
        elif severity.lower() == "moderate":
            home_care = "Your symptoms are moderate. We advise prioritizing a consultation with a qualified medical specialist over home measures."
        else:
            home_care = None  # None for severe / emergency / clinically unsuitable
    else:
        # Safe fallback for unsupported/unknown symptoms
        matched_name = symptom_name.strip()
        specialist_name = "General Physician"
        specialist_desc = "Primary care healthcare doctor for comprehensive clinical examination."
        specialist_icon = "fa-user-doctor"
        guidance = (
            f"We have noted your report regarding '{symptom_name}'. Because this symptom requires tailored clinical assessment, "
            "we recommend scheduling an in-person or virtual consultation with a General Physician rather than self-managing."
        )
        home_care = None
        warning_signs = "Any rapid worsening, high fever, unbearable pain, or breathing difficulty requires urgent medical attention."
        reference = "Clinical Primary Care Protocol"

    # Determine Urgency Badge
    if is_emergency:
        urgency_badge = "Urgent / Emergency"
        urgency_color = "#D32F2F"
    elif severity.lower() == "moderate" or (symptom_data and symptom_data.get("urgency_level") == "Moderate"):
        urgency_badge = "Moderate Priority"
        urgency_color = "#F57C00"
    else:
        urgency_badge = "Mild / Routine Care"
        urgency_color = "#2E7D32"

    disclaimer = (
        "Medical Disclaimer: AyuCare (आयुCare) provides educational health guidance and navigation support only. "
        "It is NOT a diagnostic system and does not prescribe prescription medication. Always seek the advice of a qualified "
        "medical professional for diagnosis and treatment of any health condition."
    )

    result = {
        "submitted": {
            "symptom_name": matched_name,
            "duration": duration,
            "severity": severity,
            "description": description,
            "additional_details": additional_details
        },
        "is_emergency": is_emergency,
        "emergency_details": emergency_eval,
        "urgency_badge": urgency_badge,
        "urgency_color": urgency_color,
        "preliminary_guidance": guidance,
        "general_home_care": home_care,
        "warning_signs": warning_signs,
        "recommended_specialist": {
            "name": specialist_name,
            "description": specialist_desc,
            "icon": specialist_icon
        },
        "reference_source": reference,
        "disclaimer": disclaimer
    }

    # Save to symptom_history table if patient_id is provided
    if patient_id:
        try:
            insert_sql = """
                INSERT INTO symptom_history 
                (patient_id, symptom_name, duration, severity, description, additional_details, 
                 is_emergency, guidance_summary, home_care_summary, recommended_specialist)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                patient_id,
                matched_name,
                duration,
                severity,
                description,
                additional_details,
                1 if is_emergency else 0,
                guidance,
                home_care or "None (Specialist consultation recommended)",
                specialist_name
            )
            history_id = execute_query(insert_sql, params)
            result["history_id"] = history_id
        except Exception as e:
            # History save failure should not break the triage report
            result["history_error"] = str(e)

    return result
