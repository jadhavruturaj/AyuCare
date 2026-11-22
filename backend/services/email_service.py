import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

logger = logging.getLogger("ayucare.email")

class SMTPNotConfiguredError(Exception):
    """Raised when SMTP credentials are not configured."""
    pass

class EmailDeliveryError(Exception):
    """Raised when sending email fails."""
    pass

def is_smtp_configured() -> bool:
    """Returns True if the required SMTP settings are present."""
    return bool(Config.SMTP_HOST and Config.SMTP_USER and Config.SMTP_PASSWORD)

def send_password_reset_email(to_email: str, reset_url: str, user_name: str = "User"):
    """
    Sends a secure password reset email with AyuCare branding.
    If SMTP is not configured, raises SMTPNotConfiguredError (never simulates successful delivery).
    """
    if not is_smtp_configured():
        logger.warning(
            f"[SMTP NOT CONFIGURED] Cannot dispatch email to {to_email}. "
            f"Set SMTP_HOST, SMTP_PORT, SMTP_USER, and SMTP_PASSWORD in .env. "
            f"Reset Link: {reset_url}"
        )
        raise SMTPNotConfiguredError(
            "Email delivery service is not configured. Please set SMTP_HOST, SMTP_PORT, "
            "SMTP_USER, and SMTP_PASSWORD in your .env environment file to enable outgoing emails."
        )

    # Build MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Password Reset Request — आयुCare (AyuCare)"
    from_header = f'"{Config.SMTP_FROM_NAME}" <{Config.SMTP_FROM_EMAIL}>'
    msg["From"] = from_header
    msg["To"] = to_email

    # Plaintext fallback
    text_content = f"""Hello {user_name},

We received a request to reset your password for your AyuCare healthcare account.

Please open the link below in your browser to choose a new password:
{reset_url}

This link is valid for {Config.PASSWORD_RESET_EXPIRATION_HOURS} hour(s). If you did not request this password reset, please ignore this email. Your account remains completely secure.

Best regards,
The AyuCare Health Platform Team
https://ayu-care-rho.vercel.app
"""

    # Responsive HTML template matching AyuCare brand
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset Your AyuCare Password</title>
</head>
<body style="margin: 0; padding: 0; background-color: #F0F7FD; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #2C3E50;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #F0F7FD; padding: 30px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 560px; background-color: #FFFFFF; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(13, 49, 88, 0.08);">
          <!-- Header Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #0D3158 0%, #1565C0 100%); padding: 32px 30px; text-align: center;">
              <h1 style="margin: 0; color: #FFFFFF; font-size: 26px; font-weight: 700; letter-spacing: -0.5px;">
                आयु<span style="color: #66BB6A;">Care</span>
              </h1>
              <p style="margin: 6px 0 0; color: #EAF5FF; font-size: 13px; font-weight: 500;">
                Health Today, Better Tomorrow
              </p>
            </td>
          </tr>

          <!-- Body Content -->
          <tr>
            <td style="padding: 36px 32px;">
              <h2 style="margin: 0 0 16px; color: #0D3158; font-size: 20px; font-weight: 700;">
                Password Reset Request
              </h2>
              <p style="margin: 0 0 16px; font-size: 15px; line-height: 1.6; color: #4A5568;">
                Hello <strong>{user_name}</strong>,
              </p>
              <p style="margin: 0 0 24px; font-size: 15px; line-height: 1.6; color: #4A5568;">
                We received a request to reset the password associated with this email address on the <strong>आयुCare (AyuCare)</strong> healthcare guidance platform.
              </p>

              <!-- Action Button -->
              <table role="presentation" cellspacing="0" cellpadding="0" style="margin: 28px 0;">
                <tr>
                  <td align="center" style="border-radius: 10px; background: linear-gradient(135deg, #1565C0 0%, #2E7D32 100%);">
                    <a href="{reset_url}" target="_blank" style="display: inline-block; padding: 14px 32px; color: #FFFFFF; text-decoration: none; font-size: 15px; font-weight: 600; border-radius: 10px; letter-spacing: 0.3px;">
                      Create New Password
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin: 0 0 14px; font-size: 13px; line-height: 1.5; color: #718096;">
                Or copy and paste this link into your web browser:
              </p>
              <p style="margin: 0 0 24px; font-size: 12px; line-height: 1.4; color: #1565C0; word-break: break-all; background-color: #F7FAFC; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0;">
                <a href="{reset_url}" style="color: #1565C0; text-decoration: underline;">{reset_url}</a>
              </p>

              <div style="background-color: #FFFBEB; border-left: 4px solid #F59E0B; padding: 14px 16px; border-radius: 6px; margin: 24px 0 16px;">
                <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #92400E;">
                  <strong>Note:</strong> This link will expire in <strong>{Config.PASSWORD_RESET_EXPIRATION_HOURS} hour(s)</strong>. If you did not make this request, you can safely ignore this email; your account and password remain untouched.
                </p>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #F8FAFC; border-top: 1px solid #EDF2F7; padding: 22px 30px; text-align: center;">
              <p style="margin: 0; font-size: 12px; color: #718096; line-height: 1.5;">
                आयुCare • Smart Symptom Guidance & Specialist Recommendation Platform<br>
                For technical support, contact your AyuCare administrator.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    msg.attach(MIMEText(text_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        if Config.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT, timeout=12)
        else:
            server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=12)
            if Config.SMTP_USE_TLS:
                server.starttls()

        server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
        server.sendmail(Config.SMTP_FROM_EMAIL, [to_email], msg.as_string())
        server.quit()
        logger.info(f"Password reset email dispatched to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise EmailDeliveryError(f"Email delivery failed: {str(e)}")
