from flask import request
from flask_jwt_extended import create_access_token

from src.models.UserModel import authenticate_user
from src.utils.helpers import remove_white_space
from src.utils.response import success_response, error_response


class UserLoginAction:

    @classmethod
    def run(cls):
        try:
            # Parse and clean input 
            data = request.get_json(force=True)
            if not data:
                return error_response("Request body missing or invalid JSON.", 400)

            data     = remove_white_space(data)
            email    = data.get("email", "").lower()
            password = data.get("password")

            # Validate input present 
            if not email or not password:
                return error_response("Email and password are required.", 400)

            # Authenticate against DB 
            user = authenticate_user(email, password)

            if not user:
                return error_response("Invalid email or password.", 401)

            # Generate JWT token 
            user_id      = str(user["_id"])
            access_token = create_access_token(identity=user_id)

            # Return token + basic user info 
            return success_response(
                "Login successful.",
                data={
                    "token": access_token,
                    "user": {
                        "id":                user_id,
                        "email":             user["email"],
                        "profile_completed": user.get("profile_completed", False),
                    }
                },
                status_code=200
            )

        except Exception as e:
            print(f"[LOGIN ERROR] {str(e)}")
            return error_response("An unexpected error occurred. Please try again.", 500)