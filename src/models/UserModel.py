from datetime import datetime, timezone
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash
from src import mongo


# ── Collection reference ───────────────────────────────────────────────────────
# Single place to change if collection is ever renamed.
users_collection = mongo.db.users


# ── UTC helper ─────────────────────────────────────────────────────────────────
def utcnow():
    """
    Returns current UTC time as a timezone-aware datetime object.
    """
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────────────────────

def create_user(email, password_hash, otp=None, is_verified=False):
    """
    Inserts a new unverified user into the database.
    """
    user = {
        "email": email,
        "password": password_hash,
        "otp": otp,
        "otp_created_at": utcnow(),   # used to enforce OTP expiry
        "is_verified": is_verified,
        "profile_completed": False,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    return users_collection.insert_one(user)


# ─────────────────────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────────────────────

def get_user_by_email(email):
    """
    Fetches a user document by email.
    """
    return users_collection.find_one({"email": email})


def get_user_by_id(user_id):
    """
    Fetches a user document by MongoDB ObjectId.
    """
    try:
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE — OTP
# ─────────────────────────────────────────────────────────────────────────────

def update_user_otp(email, otp):
    """
    Updates OTP and refreshes otp_created_at timestamp.
    """
    return users_collection.update_one(
        {"email": email},
        {"$set": {
            "otp":            otp,
            "otp_created_at": utcnow(),   # fresh expiry window
            "updated_at": utcnow(),
        }}
    )


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE — VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def verify_user(email):
    """
    Marks a user as verified after successful OTP validation.
    $set → sets is_verified to True
    $unset → completely removes otp and otp_created_at fields.
    """
    return users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "is_verified": True,
                "updated_at": utcnow(),
            },
            "$unset": {
                "otp": "",
                "otp_created_at": "",
            }
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE — PROFILE
# ─────────────────────────────────────────────────────────────────────────────

def update_user_profile(user_id, profile_data):
    """
    Updates a user's profile fields after login.
    profile_completed → True once this is saved.
    updated_at → refreshed on every profile update.
    """
    profile_fields = {
        "name": profile_data.get("name"),
        "dob": profile_data.get("dob"),
        "job_title": profile_data.get("job_title"),
        "company": profile_data.get("company"),
        "experience_years": profile_data.get("experience_years"),
        "expertise": profile_data.get("expertise"),
        "college": profile_data.get("college"),
        "bio": profile_data.get("bio"),
        "profile_completed": True,      
        "updated_at": utcnow(),
    }

    # Strip out keys where value is None.
    # Only update fields that were actually sent in the request.
    profile_fields = {
        key: value
        for key, value in profile_fields.items()
        if value is not None
    }

    return users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": profile_fields}
    )


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────

def authenticate_user(email, password):
    """
    Verifies email + password combination.
    """
    user = users_collection.find_one({
        "email":       email,
        "is_verified": True
    })

    if user and check_password_hash(user["password"], password):
        # Strip sensitive fields before returning to action layer.
        # pop() with default None is safe even if field doesn't exist.
        user.pop("password",None)
        user.pop("otp",None)
        user.pop("otp_created_at",None)
        return user

    return None


# SANITIZE HELPER------------------------------------------------------------------------------------

#Removes sensitive fields from a user document before returning it
def sanitize_user(user):
    if not user:
        return None

    # Remove sensitive fields
    user.pop("password",None)
    user.pop("otp",None)
    user.pop("otp_created_at",None)

    # Convert ObjectId to string for JSON serialization
    if "_id" in user:
        user["_id"] = str(user["_id"])
    return user


# RESET PASSWORD or Forgot Password---------------------------------------------------------------

#otp for reset/forgot password
def set_reset_otp(email, otp):
    return users_collection.update_one(
        {"email": email},
        {"$set": {
            "reset_otp": otp,
            "reset_otp_created_at": utcnow(),
            "reset_otp_verified": False,
            "updated_at": utcnow(),
        }}
    )

#OTP verification for reset/forgot password
def verify_reset_otp(email):
    return users_collection.update_one(
        {"email": email},
        {"$set": {
            "reset_otp_verified": True,
            "reset_otp": None,
            "reset_otp_created_at": None,
            "updated_at": utcnow(),
        }}
    )

# Set new password Clear all reset otp field
def reset_user_password(email, new_password_hash):
    return users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "password": new_password_hash,
                "updated_at": utcnow(),
            },
            "$unset": {
                "reset_otp": "",
                "reset_otp_created_at": "",
                "reset_otp_verified": "",
            }
        }
    )