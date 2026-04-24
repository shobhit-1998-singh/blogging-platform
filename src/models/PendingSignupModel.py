from datetime import datetime, timezone
from src import mongo

#Pending sign-up collection 
pending_collection = mongo.db.pending_signups

#For current timezone, Date & Time
def utcnow():
    return datetime.now(timezone.utc)

#put new signup data into collection and if any data related that mail alredy present then remove it.
def create_pending_signup(email, otp):
    pending_collection.delete_many({"email": email})

    signup_detail={
        "email": email,
        "otp": otp,
        "otp_created_at": utcnow(),
        "is_otp_verified": False,  
        "created_at": utcnow(),
    }
    return pending_collection.insert_one(signup_detail)

def get_pending_by_email(email):
    return pending_collection.find_one({"email": email})

def mark_otp_verified(email):
    return pending_collection.update_one(
        {"email": email},
        {"$set": {
            "is_otp_verified": True,
            "otp": None,
            "otp_created_at": None,
        }}
    )

#resend otp update(new otp)
def update_pending_otp(email, otp):
    return pending_collection.update_one(
        {
            "email": email
        },
        {
            "$set": 
            {
            "otp": otp,
            "otp_created_at": utcnow(),
            "is_otp_verified": False,
            }
        }
    )

#Delete pending signup account
def delete_pending_signup(email):
    return pending_collection.delete_one(
        {
        "email": email
        }
    )
