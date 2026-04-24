"""
utils/mail.py — Email sending utilities.

Rule: All email-related functions live here.
      New email types (welcome, password reset, etc.)
      get added as new functions in this file.

Why separate from actions?
  - Actions decide WHEN to send email
  - This file decides HOW to send email
  - If you switch from Gmail to SendGrid tomorrow,
    you only change this file — nothing else.

Error handling strategy:
  - SMTPAuthenticationError  → credentials wrong (.env issue)
  - SMTPConnectError         → can't reach Gmail server (network issue)
  - SMTPRecipientsRefused    → recipient email is invalid/rejected
  - ConnectionRefusedError   → wrong port or server config
  - Exception                → unexpected fallback catch

  We catch specific exceptions first (most specific → least specific)
  so we know EXACTLY what went wrong instead of a generic "something failed".
"""

import smtplib

from flask_mail import Message

from src import mail


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _send_email(subject, recipient, body):
    """
    Internal base function that actually sends the email.

    Why private (underscore prefix)?
      This is a low-level function — only used by other functions
      in this file. External code should call send_otp_email(),
      send_welcome_email() etc., not this directly.

    Why separate from the public functions?
      All public functions share the same send + error handling logic.
      Keeping it here avoids repeating try/except in every function.

    Returns:
      (True, None)           on success
      (False, error_message) on failure
    """
    try:
        msg = Message(subject=subject, recipients=[recipient], body=body)
        mail.send(msg)
        return True, None

    except smtplib.SMTPAuthenticationError:
        # Wrong Gmail credentials in .env
        # MAIL_USERNAME or MAIL_PASSWORD is incorrect,
        # or Gmail App Password was not generated correctly.
        error = (
            "Email authentication failed. "
            "Check MAIL_USERNAME and MAIL_PASSWORD in your .env file. "
            "Make sure you are using a Gmail App Password, not your account password."
        )
        print(f"[EMAIL ERROR - AUTH] {error}")
        return False, error

    except smtplib.SMTPConnectError:
        # Can't establish connection to Gmail's SMTP server.
        # Usually a network issue or wrong MAIL_SERVER / MAIL_PORT in config.
        error = (
            "Could not connect to the email server. "
            "Check MAIL_SERVER and MAIL_PORT in config.py. "
            "Expected: smtp.gmail.com on port 587."
        )
        print(f"[EMAIL ERROR - CONNECTION] {error}")
        return False, error

    except smtplib.SMTPRecipientsRefused:
        # Gmail accepted the connection but refused to deliver to this address.
        # The recipient's email address is invalid or doesn't exist.
        error = (
            f"Email delivery failed — recipient address '{recipient}' "
            "was refused by the mail server. "
            "The email address may be invalid or not exist."
        )
        print(f"[EMAIL ERROR - RECIPIENT] {error}")
        return False, error

    except smtplib.SMTPException as e:
        # Catch-all for any other SMTP-level errors not covered above.
        error = f"An SMTP error occurred while sending email: {str(e)}"
        print(f"[EMAIL ERROR - SMTP] {error}")
        return False, error

    except ConnectionRefusedError:
        # The server actively refused the connection.
        # Usually means wrong port — e.g. using 465 with TLS instead of SSL.
        error = (
            "Connection refused by the email server. "
            "If using TLS, ensure MAIL_PORT=587 and MAIL_USE_TLS=True. "
            "If using SSL, ensure MAIL_PORT=465 and MAIL_USE_SSL=True."
        )
        print(f"[EMAIL ERROR - REFUSED] {error}")
        return False, error

    except Exception as e:
        # Last resort — something completely unexpected happened.
        # Log the full error for debugging.
        error = f"Unexpected error while sending email: {str(e)}"
        print(f"[EMAIL ERROR - UNKNOWN] {error}")
        return False, error


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC EMAIL FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def send_otp_email(recipient, otp):
    """
    Sends an OTP verification email.

    Called during:
      - Signup        → verify new account
      - Resend OTP    → user requests a new code

    Args:
      recipient (str): User's email address
      otp       (str): 6-digit OTP code

    Returns:
      True  → email sent successfully
      False → email failed (action layer handles gracefully)
    """
    subject = "Your OTP Code — Blogging Platform"

    body = (
        f"Hello,\n\n"
        f"Your OTP verification code is:\n\n"
        f"    {otp}\n\n"
        f"This code expires in 10 minutes.\n"
        f"Do not share this code with anyone.\n\n"
        f"If you didn't request this, please ignore this email.\n\n"
        f"— The Blogging Platform Team"
    )

    success, error = _send_email(subject, recipient, body)

    if not success:
        # Error already printed inside _send_email with specific reason.
        # We just return False so the action can respond to the user.
        print(f"[OTP EMAIL FAILED] Could not send OTP to {recipient}. Reason: {error}")

    return success


def send_welcome_email(recipient, name):
    """
    Sends a welcome email after the user completes profile setup.

    Called during:
      - UserProfileAction → after profile is saved successfully

    Args:
      recipient (str): User's email address
      name      (str): User's display name
    """
    subject = "Welcome to the Blogging Platform!"

    body = (
        f"Hi {name},\n\n"
        f"Welcome! Your profile is all set up.\n"
        f"You can now write blogs, follow authors, and explore content.\n\n"
        f"Get started by writing your first blog post.\n\n"
        f"— The Blogging Platform Team"
    )

    success, error = _send_email(subject, recipient, body)

    if not success:
        print(f"[WELCOME EMAIL FAILED] Could not send welcome email to {recipient}. Reason: {error}")

    return success

#Forgot Password/Reset Password OTP mail--------------------------------------------------------------------

def send_reset_otp_email(recipient, otp):
    """
    Sends a password reset OTP email.

    Called during Step 1 of forgot password flow.
    Separate from send_otp_email so subject and body
    are clearly different — user knows it's a reset, not signup.
    """
    subject = "Password Reset OTP — Blogging Platform"

    body = (
        f"Hello,\n\n"
        f"You requested a password reset. Your OTP is:\n\n"
        f"    {otp}\n\n"
        f"This code expires in 10 minutes.\n"
        f"Do not share this code with anyone.\n\n"
        f"If you did not request a password reset, "
        f"please ignore this email. Your password will not change.\n\n"
        f"— The Blogging Platform Team"
    )

    success, error = _send_email(subject, recipient, body)

    if not success:
        print(f"[RESET OTP EMAIL FAILED] Could not send to {recipient}. Reason: {error}")

    return success