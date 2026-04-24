"""
VerifyResetOtpAction.py — Step 2 of password reset flow.

Accepts email + OTP.
Verifies OTP, marks reset as verified.
Unlocks Step 3 — new password can now be submitted.
"""

from datetime import datetime, timezone

from flask import request

from src.models.UserModel import get_user_by_email, verify_reset_otp
from src.utils.helpers import remove_white_space, make_aware
from src.utils.response import success_response, error_response


class ForgotPasswordVerifyResetOtpAction :

    OTP_EXPIRY_MINUTES = 10
    OTP_LENGTH         = 6

    @classmethod
    def _is_otp_expired(cls, otp_created_at):
        """
        Checks if reset OTP has passed its 10-minute window.
        Handles naive datetimes returned by PyMongo.
        """
        if not otp_created_at:
            return True

        # Reattach UTC timezone if PyMongo stripped it
        otp_created_at = make_aware(otp_created_at)

        elapsed     = (datetime.now(timezone.utc) - otp_created_at).total_seconds()
        expiry_secs = cls.OTP_EXPIRY_MINUTES * 60
        return elapsed > expiry_secs

    @classmethod
    def run(cls, obj):
        try:
            # ── 1. Parse input ─────────────────────────────────────────────────
            data = request.get_json(force=True)
            if not data:
                return error_response("Request body missing or invalid JSON.", 400)

            data  = remove_white_space(data)
            email = data.get("email", "").lower()
            otp   = str(data.get("otp", "")).strip()

            # ── 2. Validate format ─────────────────────────────────────────────
            if not email:
                return error_response("Email is required.", 400)

            if not otp or not otp.isdigit() or len(otp) != cls.OTP_LENGTH:
                return error_response(
                    f"OTP must be a {cls.OTP_LENGTH}-digit number.", 400
                )

            # ── 3. Fetch user ──────────────────────────────────────────────────
            user = get_user_by_email(email)
            if not user or not user.get("reset_otp"):
                # Generic message — don't reveal account existence
                return error_response(
                    "Invalid email or OTP. Please request a new reset OTP.", 400
                )

            # ── 4. Check OTP match ─────────────────────────────────────────────
            stored_otp = str(user.get("reset_otp", ""))
            if stored_otp != otp:
                return error_response(
                    "Invalid OTP. Please check the code and try again.", 400
                )

            # ── 5. Check OTP expiry ────────────────────────────────────────────
            if cls._is_otp_expired(user.get("reset_otp_created_at")):
                return error_response(
                    f"OTP has expired. OTPs are valid for "
                    f"{cls.OTP_EXPIRY_MINUTES} minutes only. "
                    f"Please request a new reset OTP.",
                    410
                )

            # ── 6. Mark OTP as verified ────────────────────────────────────────
            verify_reset_otp(email)

            return success_response(
                "OTP verified. Please submit your new password.",
                status_code=200
            )

        except Exception as e:
            print(f"[VERIFY RESET OTP ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )