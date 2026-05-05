import secrets
from flask import request, jsonify
from src.models.UserModel import get_user_by_email, set_reset_otp
from src.utils.helpers import remove_white_space
from src.utils.mail import send_reset_otp_email
from src.utils.otp_rate_limiter import check_rate_limit
from src.utils.response import success_response, error_response


class ForgotPasswordAction:

    @classmethod
    def _generate_otp(cls):
        """Cryptographically secure 6-digit OTP."""
        return str(secrets.randbelow(900000) + 100000)

    @classmethod
    def run(cls, obj):
        try:
            # Parse input 
            data = request.get_json(force=True)
            if not data:
                return error_response("Request body missing or invalid JSON.", 400)

            data  = remove_white_space(data)
            email = data.get("email", "").lower()

            if not email:
                return error_response("Email is required.", 400)

            # Fetch user 
            user = get_user_by_email(email)

            # Generic response if not found 
            if not user:
                return success_response(
                    "If this email is registered, "
                    "you will receive a reset OTP shortly.",
                    status_code=200
                )

            if not user.get("is_verified"):
                return error_response(
                    "This account is not verified. "
                    "Please complete email verification first.",
                    403
                )

            # Check rate limit
            otp_requests      = user.get("reset_otp_requests", [])
            rate_limit_result = check_rate_limit(otp_requests)

            if not rate_limit_result["allowed"]:
                return jsonify({
                    "status":       "failed",
                    "message":      rate_limit_result["message"],
                    "wait_seconds": rate_limit_result["wait_seconds"],
                }), 429

            # Generate OTP and save 
            otp = cls._generate_otp()
            set_reset_otp(
                email,
                otp,
                rate_limit_result["clean_requests"]
            )

            # Send reset OTP email 
            email_sent = send_reset_otp_email(email, otp)
            if not email_sent:
                return error_response(
                    "Could not send reset OTP email. Please try again.", 500
                )

            # Same generic message as user-not-found case
            return success_response(
                "If this email is registered, "
                "you will receive a reset OTP shortly.",
                status_code=200
            )

        except Exception as e:
            print(f"[FORGOT PASSWORD ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )