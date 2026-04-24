import secrets
from flask import request
from src.utils.helpers import remove_white_space
from src.utils.mail import send_reset_otp_email
from src.utils.response import success_response, error_response
from src.models.UserModel import get_user_by_email, set_reset_otp


class ForgotPasswordAction:

    @classmethod
    def _generate_otp(cls):
        return str(secrets.randbelow(900000) + 100000)

    @classmethod
    def run(cls, obj):
        try:
            # Parse input ...........................................
            data = request.get_json(force=True)
            if not data:
                return error_response("Request body missing or invalid JSON.", 400)

            data  = remove_white_space(data)
            email = data.get("email", "").lower()

            if not email:
                return error_response("Email is required.", 400)

            # Check user exists..................................................
            user = get_user_by_email(email)
            if not user:
                return success_response(
                    "If this email is registered, you will receive a reset OTP shortly.",
                    status_code=200
                )

            # Check account is verified ......................................
            if not user.get("is_verified"):
                return error_response(
                    "This account is not verified. "
                    "Please complete email verification first.",
                    403
                )

            # Generate and store OTP .........................................
            otp = cls._generate_otp()
            set_reset_otp(email, otp)

            # Send OTP email .......................................
            email_sent = send_reset_otp_email(email, otp)
            if not email_sent:
                return error_response(
                    "Could not send reset OTP email. Please try again.", 500
                )

            # Same message as "user not found" caseprevents enumeration
            return success_response(
                "If this email is registered, you will receive a reset OTP shortly.",
                status_code=200
            )

        except Exception as e:
            print(f"[FORGOT PASSWORD ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )