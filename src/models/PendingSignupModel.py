from datetime import datetime, timezone
from src import mongo


# Collection reference
pending_collection = mongo.db.pending_signups

def utcnow():
    return datetime.now(timezone.utc)


# TTL Index 
pending_collection.create_index(
    "created_at",
    expireAfterSeconds=7200,
    name="pending_signup_ttl"
)


# ─────────────────────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────────────────────

def create_pending_signup(email, otp):
    pending_collection.delete_many({"email": email})

    record = {
        "email":           email,
        "otp":             otp,
        "otp_created_at":  utcnow(),
        "is_otp_verified": False,
        "otp_requests":    [utcnow()],   
        "created_at":      utcnow(),  
    }
    return pending_collection.insert_one(record)


# ─────────────────────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────────────────────

def get_pending_by_email(email):
    """Fetches pending signup record by email."""
    return pending_collection.find_one({"email": email})


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────────────────────────────────────

def update_pending_otp(email, otp, clean_requests):
    return pending_collection.update_one(
        {"email": email},
        {"$set": {
            "otp":             otp,
            "otp_created_at":  utcnow(),
            "is_otp_verified": False,
            "otp_requests":    clean_requests,
        }}
    )


def mark_otp_verified(email):
    return pending_collection.update_one(
        {"email": email},
        {"$set": {
            "is_otp_verified": True,
            "otp":             None,
            "otp_created_at":  None,
        }}
    )

def delete_pending_signup(email):
    return pending_collection.delete_one({"email": email})