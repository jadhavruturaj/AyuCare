import os
import re
import logging
import urllib.request
import urllib.parse
import json
from config import Config

logger = logging.getLogger("ayucare.sms")

def normalize_mobile(mobile: str) -> str:
    """Cleans phone number and strips spaces/special characters."""
    return re.sub(r'[\s\-\(\)]', '', mobile.strip())

def send_otp_sms(mobile: str, otp_code: str, purpose: str = "registration") -> dict:
    """
    Dispatches OTP via configured SMS gateway (Twilio, Fast2SMS, or Console).
    Returns dict with delivery status and friendly user message.
    """
    clean_mobile = normalize_mobile(mobile)
    sms_body = (
        f"Your आयुCare (AyuCare) verification code is {otp_code}. "
        f"Valid for {Config.OTP_EXPIRATION_MINUTES} minutes. "
        "Do not share this code with anyone for safety."
    )

    gateway = Config.SMS_GATEWAY

    # 1. Twilio Integration
    if gateway == "twilio" and Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
        try:
            to_number = clean_mobile if clean_mobile.startswith("+") else f"+91{clean_mobile}"
            url = f"https://api.twilio.com/2010-04-01/Accounts/{Config.TWILIO_ACCOUNT_SID}/Messages.json"
            
            data = urllib.parse.urlencode({
                "To": to_number,
                "From": Config.TWILIO_PHONE_NUMBER,
                "Body": sms_body
            }).encode("utf-8")

            req = urllib.request.Request(url, data=data, method="POST")
            # Basic Auth header for Twilio
            import base64
            auth_str = f"{Config.TWILIO_ACCOUNT_SID}:{Config.TWILIO_AUTH_TOKEN}"
            auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            req.add_header("Authorization", f"Basic {auth_b64}")

            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                logger.info(f"Twilio SMS dispatched to {to_number}. SID: {res_data.get('sid')}")
                return {
                    "success": True,
                    "delivered": True,
                    "channel": "twilio",
                    "message": f"Verification code sent to {to_number}."
                }
        except Exception as e:
            logger.error(f"Twilio delivery error: {e}")
            # Fallback to logging so user is informed
            return {
                "success": True,
                "delivered": False,
                "channel": "twilio-fallback",
                "message": f"SMS gateway error: {str(e)}."
            }

    # 2. Fast2SMS Integration (common Indian SMS provider)
    elif gateway == "fast2sms" and Config.FAST2SMS_API_KEY:
        try:
            digits_only = re.sub(r'^\+?91', '', clean_mobile)
            url = "https://www.fast2sms.com/dev/bulkV2"
            headers = {
                "authorization": Config.FAST2SMS_API_KEY,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = urllib.parse.urlencode({
                "variables_values": otp_code,
                "route": "otp",
                "numbers": digits_only
            }).encode("utf-8")

            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                logger.info(f"Fast2SMS dispatched to {digits_only}: {res_data}")
                return {
                    "success": True,
                    "delivered": True,
                    "channel": "fast2sms",
                    "message": f"Verification code sent to {clean_mobile}."
                }
        except Exception as e:
            logger.error(f"Fast2SMS delivery error: {e}")

    # 3. Default Console / Development mode
    logger.info("=" * 60)
    logger.info(f" [AyuCare SMS Gateway] OTP DISPATCH")
    logger.info(f" Mobile Number : {clean_mobile}")
    logger.info(f" OTP Code      : {otp_code}")
    logger.info(f" Purpose       : {purpose}")
    logger.info(f" Expiration    : {Config.OTP_EXPIRATION_MINUTES} minutes")
    logger.info("=" * 60)

    # In local/testing mode, return the generated OTP in development output for immediate testing
    is_dev = Config.DEBUG or not (Config.TWILIO_ACCOUNT_SID or Config.FAST2SMS_API_KEY)
    masked = clean_mobile[-4:] if len(clean_mobile) >= 4 else clean_mobile
    
    return {
        "success": True,
        "delivered": False,
        "channel": "console",
        "message": f"OTP has been generated for ••••••{masked}.",
        "dev_otp": otp_code if is_dev else None
    }
