"""
UserLoginAction.py — Handles user login.

Responsibilities:
  1. Validate input
  2. Authenticate email + password
  3. Generate JWT token
  4. Return token + user data to client

What it does NOT do:
  - Verify OTP        ← handled in signup flow
  - Hash password     ← handled in signup flow
  - Query DB directly ← UserModel.py's job
"""

from flask import request
from flask_jwt_extended import create_access_token

from src.models.UserModel import authenticate_user
from src.utils.helpers import remove_white_space
from src.utils.response import success_response, error_response


class UserLoginAction:

    @classmethod
    def run(cls):
        try:
            # ── 1. Parse and clean input ───────────────────────────────────────
            data = request.get_json(force=True)
            if not data:
                return error_response("Request body missing or invalid JSON.", 400)

            data     = remove_white_space(data)
            email    = data.get("email", "").lower()
            password = data.get("password")

            # ── 2. Validate input present ──────────────────────────────────────
            if not email or not password:
                return error_response("Email and password are required.", 400)

            # ── 3. Authenticate against DB ─────────────────────────────────────
            # authenticate_user() checks password hash and is_verified=True.
            # Returns sanitized user dict (no password/otp) or None.
            user = authenticate_user(email, password)

            if not user:
                # Generic message — don't reveal whether email exists or
                # whether it was the password that was wrong.
                return error_response("Invalid email or password.", 401)

            # ── 4. Generate JWT token ──────────────────────────────────────────
            # identity = user_id string embedded inside the token.
            # Every protected route calls get_jwt_identity() to get this back.
            # str() converts MongoDB ObjectId → plain string for JSON safety.
            user_id      = str(user["_id"])
            access_token = create_access_token(identity=user_id)

            # ── 5. Return token + basic user info ─────────────────────────────
            # Frontend stores this token and sends it as:
            #   Authorization: Bearer <access_token>
            # on every protected request.
            return success_response(
                "Login successful.",
                data={
                    "token": access_token,
                    "user": {
                        "id":                user_id,
                        "email":             user["email"],
                        "profile_completed": user.get("profile_completed", False),
                        # profile_completed tells frontend whether to show
                        # profile setup screen or go straight to home feed
                    }
                },
                status_code=200
            )

        except Exception as e:
            print(f"[LOGIN ERROR] {str(e)}")
            return error_response("An unexpected error occurred. Please try again.", 500)