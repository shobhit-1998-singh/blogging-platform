from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.UserModel import get_user_by_id, update_user_avatar
from src.utils.cloudinary_helper import upload_profile_image, delete_image
from src.utils.response import success_response, error_response


class UserProfileImageAction:

    @classmethod
    @jwt_required()
    def upload_avatar(cls):
        try:
            # Get logged-in user
            user_id = get_jwt_identity()
            user = get_user_by_id(user_id)

            if not user:
                return error_response("User not found.", 404)

            # Check file was sent 
            if "avatar" not in request.files:
                return error_response(
                    "No image file found. "
                    "Send file with field name 'avatar'.",
                    400
                )

            file = request.files["avatar"]

            # Check file is not empty 
            if file.filename == "":
                return error_response("No file selected.", 400)

            # Delete old avatar from Cloudinary if exists 
            existing_avatar = user.get("avatar_public_id")
            if existing_avatar:
                delete_image(existing_avatar)
            
            # Upload new image to Cloudinary 
            is_uploaded, result = upload_profile_image(file, user_id)

            if not is_uploaded:
                 return error_response(result, 400)

            # Save public_id to MongoDB 
            public_id = result
            update_user_avatar(user_id, public_id)

            return success_response(
                "Profile picture uploaded successfully.",
                data={
                    "avatar_public_id": public_id,
                },
                status_code=200
            )

        except Exception as e:
            print(f"[AVATAR UPLOAD ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )