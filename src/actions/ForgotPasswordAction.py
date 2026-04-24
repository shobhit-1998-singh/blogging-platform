"""
ForgotPasswordAction.py — Step 1 of password reset flow.

Accepts email only.
Checks user exists, generates OTP, sends to email.
Does NOT ask for new password yet.
"""

import secrets

from flask import request

from src.models.UserModel import get_user_by_email, set_reset_otp
from src.utils.helpers import remove_white_space
from src.utils.mail import send_reset_otp_email
from src.utils.response import success_response, error_response


class ForgotPasswordAction:

    @classmethod
    def _generate_otp(cls):
        """Cryptographically secure 6-digit OTP."""
        return str(secrets.randbelow(900000) + 100000)

    @classmethod
    def run(cls, obj):
        try:
            # ── 1. Parse input ─────────────────────────────────────────────────
            data = request.get_json(force=True)
            if not data:
                return error_response("Request body missing or invalid JSON.", 400)

            data  = remove_white_space(data)
            email = data.get("email", "").lower()

            if not email:
                return error_response("Email is required.", 400)

            # ── 2. Check user exists ───────────────────────────────────────────
            # IMPORTANT: We return the same message whether email exists or not.
            # This prevents email enumeration attacks — attacker can't use this
            # endpoint to check which emails are registered in your system.
            user = get_user_by_email(email)
            if not user:
                return success_response(
                    "If this email is registered, you will receive a reset OTP shortly.",
                    status_code=200
                )

            # ── 3. Check account is verified ───────────────────────────────────
            # Unverified accounts have no confirmed email — can't reset password.
            if not user.get("is_verified"):
                return error_response(
                    "This account is not verified. "
                    "Please complete email verification first.",
                    403
                )

            # ── 4. Generate and store OTP ──────────────────────────────────────
            otp = cls._generate_otp()
            set_reset_otp(email, otp)

            # ── 5. Send OTP email ──────────────────────────────────────────────
            email_sent = send_reset_otp_email(email, otp)
            if not email_sent:
                return error_response(
                    "Could not send reset OTP email. Please try again.", 500
                )

            # Same message as "user not found" case — prevents enumeration
            return success_response(
                "If this email is registered, you will receive a reset OTP shortly.",
                status_code=200
            )

        except Exception as e:
            print(f"[FORGOT PASSWORD ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )