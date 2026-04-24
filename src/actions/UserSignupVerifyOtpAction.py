from flask import request
from datetime import datetime, timezone
from src.utils.helpers import remove_white_space
from src.utils.response import success_response, error_response
from src.models.PendingSignupModel import get_pending_by_email, mark_otp_verified


class UserSignupVerifyOtpAction:

    OTP_EXPIRY_MINUTES = 10
    OTP_LENGTH = 6

    @classmethod
    def _is_otp_expired(cls, otp_created_at):
        """
        Checks if OTP has passed its 10-minute window.
        Returns True if expired, False if still valid.
        """
        if not otp_created_at:
            return True
        if otp_created_at.tzinfo is None:
           otp_created_at = otp_created_at.replace(tzinfo=timezone.utc)
           
        elapsed = (datetime.now(timezone.utc) - otp_created_at).total_seconds()
        expiry_secs = cls.OTP_EXPIRY_MINUTES * 60
        return elapsed > expiry_secs

    @classmethod
    def run(cls, obj):
        try:
            # Parse input
            data = request.get_json(force=True)
            if not data:
                return error_response("Request body missing or invalid JSON.", 400)

            data  = remove_white_space(data)
            email = data.get("email", "").lower()
            otp   = str(data.get("otp", "")).strip()

            # Validate format
            if not email:
                return error_response("Email is required.", 400)

            if not otp or not otp.isdigit() or len(otp) != cls.OTP_LENGTH:
                return error_response(
                    f"OTP must be a {cls.OTP_LENGTH}-digit number.", 400
                )

            # Fetch pending record
            pending = get_pending_by_email(email)
            if not pending:
                # Generic message — don't reveal whether email exists
                return error_response(
                    "Invalid email or OTP. Please restart signup.", 400
                )

            # Check OTP match
            if str(pending.get("otp", "")) != otp:
                return error_response(
                    "Invalid OTP. Please check the code and try again.", 400
                )

            # Check OTP expiry
            if cls._is_otp_expired(pending.get("otp_created_at")):
                return error_response(
                    f"OTP has expired. OTPs are valid for "
                    f"{cls.OTP_EXPIRY_MINUTES} minutes only. "
                    f"Please request a new OTP.",
                    410
                )

            # Mark OTP as verified
            mark_otp_verified(email)

            return success_response(
                "Email verified successfully. Please set your password to complete signup.",
                status_code=200
            )

        except Exception as e:
            print(f"[SIGNUP OTP ERROR] {str(e)}")
            return error_response("An unexpected error occurred. Please try again.", 500)