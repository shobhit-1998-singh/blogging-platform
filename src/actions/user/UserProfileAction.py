from datetime import datetime, timezone
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.UserModel import get_user_by_id, update_user_profile, update_social_links,sanitize_user
from src.utils.constants import ALLOWED_INTERESTS, MIN_INTERESTS, MAX_INTERESTS, SOCIAL_LINK_PREFIXES
from src.utils.helpers import remove_white_space
from src.utils.response import success_response, error_response


class UserProfileAction:

    # ── Validation constants
    MAX_BIO_LENGTH = 300
    MIN_EXPERIENCE_YEARS = 0
    MAX_EXPERIENCE_YEARS = 60
    DOB_FORMAT = "%Y-%m-%d"

    # PRIVATE VALIDATORS

    @classmethod
    def _validate_dob(cls, dob):
        if not dob:
            return True, None 

        try:
            dob_date = datetime.strptime(dob, cls.DOB_FORMAT).date()
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD (e.g. 1998-05-21)."

        today = datetime.now(timezone.utc).date()

        if dob_date >= today:
            return False, "Date of birth cannot be today or a future date."

        age = (
            today.year - dob_date.year
            - ((today.month, today.day) < (dob_date.month, dob_date.day))
        )

        if age < 13:
            return False, "You must be at least 13 years old to use this platform."

        return True, None

    @classmethod
    def _validate_experience(cls, experience_years):
        """
        Validates experience_years is a non-negative integer.
        Returns (True, None) or (False, error_message).
        """
        if experience_years is None:
            return True, None   # optional

        if not isinstance(experience_years, int):
            return False, "Experience years must be a whole number (e.g. 3)."

        if experience_years < cls.MIN_EXPERIENCE_YEARS:
            return False, "Experience years cannot be negative."

        if experience_years > cls.MAX_EXPERIENCE_YEARS:
            return False, f"Experience years cannot exceed {cls.MAX_EXPERIENCE_YEARS}."

        return True, None

    @classmethod
    def _validate_expertise(cls, expertise):
        """
        Validates expertise is a non-empty list of strings.

        Example valid:   ["Python", "MongoDB", "Flask"]
        Example invalid: "Python"  or  [1, 2, 3]

        Returns (True, cleaned_list or None) or (False, error_message).
        """
        if expertise is None:
            return True, None   # optional

        if not isinstance(expertise, list):
            return False, 'Expertise must be a list e.g. ["Python", "Flask"].'

        if len(expertise) == 0:
            return False, "Expertise list cannot be empty if provided."

        if not all(isinstance(skill, str) for skill in expertise):
            return False, "Each expertise item must be a string."

        cleaned = [skill.strip() for skill in expertise if skill.strip()]
        if not cleaned:
            return False, "Expertise list cannot contain only empty strings."

        return True, cleaned

    @classmethod
    def _validate_bio(cls, bio):
        """
        Validates bio does not exceed max length.
        Returns (True, None) or (False, error_message).
        """
        if not bio:
            return True, None   # optional

        if len(bio.strip()) > cls.MAX_BIO_LENGTH:
            return False, f"Bio cannot exceed {cls.MAX_BIO_LENGTH} characters."

        return True, None

    @classmethod
    def _validate_interests(cls, interests):
        if not interests:
            return True, None   # optional — user can set later

        if not isinstance(interests, list):
            return False, 'Interests must be a list e.g. ["backend", "dsa"].'

        if len(interests) < MIN_INTERESTS:
            return False, f"Please select at least {MIN_INTERESTS} interest."

        if len(interests) > MAX_INTERESTS:
            return False, (
                f"You can select maximum {MAX_INTERESTS} interests. "
                f"Be specific — it improves your feed quality."
            )

        # Normalize to lowercase and strip whitespace
        cleaned = [i.strip().lower() for i in interests if i.strip()]

        # Check for duplicates
        if len(cleaned) != len(set(cleaned)):
            return False, "Interests list cannot contain duplicates."

        # Validate each against allowed list
        invalid = [i for i in cleaned if i not in ALLOWED_INTERESTS]
        if invalid:
            return False, (
                f"Invalid interests: {', '.join(invalid)}. "
                f"Allowed interests: {', '.join(ALLOWED_INTERESTS)}."
            )

        return True, cleaned

    @classmethod
    def _validate_social_links(cls, social_links):
        if not social_links:
            return True, None   # optional entirely

        if not isinstance(social_links, dict):
            return False, "Social links must be an object."

        # Only allow known platforms
        unknown_keys = [
            k for k in social_links
            if k not in SOCIAL_LINK_PREFIXES
        ]
        if unknown_keys:
            return False, (
                f"Unknown social platform(s): {', '.join(unknown_keys)}. "
                f"Allowed: {', '.join(SOCIAL_LINK_PREFIXES.keys())}."
            )

        # Validate each provided URL starts with correct prefix
        for platform, url in social_links.items():
            if not url:
                continue   # empty string = user clearing the link, allowed

            expected_prefix = SOCIAL_LINK_PREFIXES[platform]
            if not url.startswith(expected_prefix):
                return False, (
                    f"Invalid {platform} URL. "
                    f"Must start with: {expected_prefix}"
                )

        return True, social_links

    
    # PUBLIC METHODS

    @classmethod
    @jwt_required()
    def save_profile(cls):
        
        try:
            #  Get logged-in user from JWT
            user_id = get_jwt_identity()
            user    = get_user_by_id(user_id)

            if not user:
                return error_response("User not found.", 404)

            # Parse input 
            data = request.get_json(force=True)
            if not data:
                return error_response("Request body missing or invalid JSON.", 400)

            data = remove_white_space(data)

            # Extract all fields
            name             = data.get("name")
            dob              = data.get("dob")
            job_title        = data.get("job_title")
            company          = data.get("company")
            experience_years = data.get("experience_years")
            expertise        = data.get("expertise")
            college          = data.get("college")
            bio              = data.get("bio")
            interests        = data.get("interests")
            social_links     = data.get("social_links")

            # Name is required 
            if not name or not name.strip():
                return error_response("Name is required.", 400)

            # Validate all fields
            is_valid, dob_error = cls._validate_dob(dob)
            if not is_valid:
                return error_response(dob_error, 400)

            is_valid, exp_error = cls._validate_experience(experience_years)
            if not is_valid:
                return error_response(exp_error, 400)

            is_valid, expertise_result = cls._validate_expertise(expertise)
            if not is_valid:
                return error_response(expertise_result, 400)
            if isinstance(expertise_result, list):
                expertise = expertise_result  

            is_valid, bio_error = cls._validate_bio(bio)
            if not is_valid:
                return error_response(bio_error, 400)

            is_valid, interests_result = cls._validate_interests(interests)
            if not is_valid:
                return error_response(interests_result, 400)
            if isinstance(interests_result, list):
                interests = interests_result  

            is_valid, social_result = cls._validate_social_links(social_links)
            if not is_valid:
                return error_response(social_result, 400)

            # ── 5. Check if first time completing profile ──────────────────────
            # Used to send welcome email once only
            is_first_time = not user.get("profile_completed", False)

            # ── 6. Build and save profile data ─────────────────────────────────
            profile_data = {
                "name":             name.strip(),
                "dob":              dob,
                "job_title":        job_title,
                "company":          company,
                "experience_years": experience_years,
                "expertise":        expertise,
                "college":          college,
                "bio":              bio.strip() if bio else None,
                "interests":        interests,
            }

            update_user_profile(user_id, profile_data)

            # Save social links separately
            if social_result:
                update_social_links(user_id, social_result)

            # Send welcome email on first completion
            if is_first_time:
                from src.utils.mail import send_welcome_email
                send_welcome_email(
                    recipient=user["email"],
                    name=name.strip()
                )

            return success_response(
                "Profile saved successfully.",
                data={"profile_completed": True},
                status_code=200
            )

        except Exception as e:
            print(f"[PROFILE SAVE ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )

    @classmethod
    @jwt_required()
    def get_profile(cls):
        try:
            user_id = get_jwt_identity()
            user    = get_user_by_id(user_id)

            if not user:
                return error_response("User not found.", 404)

            sanitized = sanitize_user(user)

            return success_response(
                "Profile retrieved successfully.",
                data={"user": sanitized},
                status_code=200
            )

        except Exception as e:
            print(f"[PROFILE GET ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )

    @classmethod
    def get_public_profile(cls, user_id):
        try:
            user = get_user_by_id(user_id)

            if not user:
                return error_response("User not found.", 404)

            sanitized = sanitize_user(user)

            sanitized.pop("is_verified", None)
            sanitized.pop("profile_completed", None)
            sanitized.pop("created_at", None)

            return success_response(
                "Profile retrieved successfully.",
                data={"user": sanitized},
                status_code=200
            )

        except Exception as e:
            print(f"[PUBLIC PROFILE ERROR] {str(e)}")
            return error_response(
                "An unexpected error occurred. Please try again.", 500
            )