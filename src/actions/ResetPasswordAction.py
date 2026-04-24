import re
from flask import request
from werkzeug.security import generate_password_hash
from src.models.UserModel import get_user_by_email, reset_user_password
from src.utils.helpers import remove_white_space
from src.utils.response import success_response, error_response


class ResetPasswordAction:

    MIN_PASSWORD_LENGTH = 8

    @classmethod
    def _validate_password(cls, password):
        if not password:
            return False, "Password is required."

        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return False, (
                f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters."
            )

        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter."

        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter."

        if not re.search(r'\d', password):
            return False, "Password must contain at least one number."

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, (
                "Password must contain at least one special character "
                "(!@#$%^&* etc.)."
            )

        return True, None

    @classmethod
    def run(cls, obj):
        try:
            # Parse input 
            data = request.get_json(force=True)
            if not data:
                return error_response("Request body missing or invalid JSON.", 400)

            data         = remove_white_space(data)
            email        = data.get("email", "").lower()
            new_password = data.get("password")

            if not email:
                return error_response("Email is required.", 400)

            # Validate password strength 
            is_valid, password_error = cls._validate_password(new_password)
            if not is_valid:
                return error_response(password_error, 400)

            # Fetch user 
            user = get_user_by_email(email)
            if not user:
                return error_response(
                    "Invalid request. Please restart the reset flow.", 400
                )

            # Check reset OTP was verified 
            if not user.get("reset_otp_verified"):
                return error_response(
                    "OTP not verified. "
                    "Please complete OTP verification before resetting password.",
                    403   # 403 Forbidden — not allowed to skip Step 2
                )

            # Hash and save new password 
            new_password_hash = generate_password_hash(new_password)
            reset_user_password(email, new_password_hash)
            # reset_user_password also clears all reset_otp fields from DB

            return success_response(
                "Password reset successfully. You can now log in with your new password.",
                status_code=200
            )

        except Exception as e:
            print(f"[RESET PASSWORD ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )