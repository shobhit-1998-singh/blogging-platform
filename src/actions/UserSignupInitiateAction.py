import re
import secrets
from flask import request
from src.models.PendingSignupModel import create_pending_signup, get_pending_by_email, update_pending_otp
from src.models.UserModel import get_user_by_email
from src.utils.helpers import remove_white_space
from src.utils.mail import send_otp_email
from src.utils.otp_rate_limiter import check_rate_limit
from src.utils.response import success_response, error_response
from flask import jsonify


class UserSignupInitiateAction:

    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

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

            # Validate email 
            if not email:
                return error_response("Email is required.", 400)

            if not cls.EMAIL_REGEX.match(email):
                return error_response(
                    "Invalid email format. Please enter a valid email address.",
                    400
                )

            # Check not already registered 
            existing_user = get_user_by_email(email)
            if existing_user:
                return error_response(
                    "This email is already registered. Please log in instead.",
                    409
                )

            # Check rate limit 
            existing_pending = get_pending_by_email(email)
            otp_requests     = []

            if existing_pending:
                otp_requests = existing_pending.get("otp_requests", [])

            rate_limit_result = check_rate_limit(otp_requests)

            if not rate_limit_result["allowed"]:
                return jsonify({
                    "status":       "failed",
                    "message":      rate_limit_result["message"],
                    "wait_seconds": rate_limit_result["wait_seconds"],
                }), 429

            # Generate OTP 
            otp = cls._generate_otp()

            # Create or update pending record 
            if existing_pending:
                update_pending_otp(
                    email,
                    otp,
                    rate_limit_result["clean_requests"]
                )
            else:
                create_pending_signup(email, otp)

            # Send OTP email 
            email_sent = send_otp_email(email, otp)
            if not email_sent:
                return error_response(
                    "Could not send OTP email. Please try again.", 500
                )

            return success_response(
                "OTP sent to your email. Please verify to continue.",
                status_code=200
            )

        except Exception as e:
            print(f"[SIGNUP INITIATE ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )