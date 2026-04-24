import re
from flask import request
from werkzeug.security import generate_password_hash
from src.models.PendingSignupModel import get_pending_by_email, delete_pending_signup
from src.models.UserModel import create_user, get_user_by_email
from src.utils.helpers import remove_white_space
from src.utils.mail import send_welcome_email
from src.utils.response import success_response, error_response


class UserSignupCompleteAction:

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

            data     = remove_white_space(data)
            email    = data.get("email", "").lower()
            password = data.get("password")

            if not email:
                return error_response("Email is required.", 400)

            # Validate password 
            is_valid, password_error = cls._validate_password(password)
            if not is_valid:
                return error_response(password_error, 400)

            # Check pending record exists and OTP was verified
            pending = get_pending_by_email(email)

            if not pending:
                return error_response(
                    "No signup in progress for this email. "
                    "Please start from Step 1.",
                    400
                )

            if not pending.get("is_otp_verified"):
                # User skipped OTP verification and tried to jump to Step 3.
                return error_response(
                    "Email not verified. "
                    "Please complete OTP verification before setting a password.",
                    403
                )

            #Check user doesn't already exist 
            # Edge case: user completed signup elsewhere between steps.
            if get_user_by_email(email):
                delete_pending_signup(email)   # clean up stale pending record
                return error_response(
                    "This email is already registered. Please log in instead.",
                    409
                )

            # Hash password and create user 
            password_hash = generate_password_hash(password)

            # create_user sets is_verified=True directly since email is already
            create_user(email, password_hash, otp=None, is_verified=True)

            # Clean up pending record 
            delete_pending_signup(email)

            # Send welcome email 
            send_welcome_email(email, name=email.split("@")[0])
            # name fallback: use part before @ until profile is filled

            return success_response(
                "Account created successfully. You can now log in.",
                status_code=201
            )

        except Exception as e:
            print(f"[SIGNUP COMPLETE ERROR] {str(e)}")
            return error_response("An unexpected error occurred. Please try again.", 500)