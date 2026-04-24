"""
Configuration settings for the Flask app.
Loads secret keys and database configurations from `.env` file.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    """Application configuration settings."""
 
# Load MongoDB URI and Secret Key & JWT Secret key from environment variables
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")

# JWT_ACCESS_TOKEN_EXPIRES: how long before the token stops working.
# timedelta(days=1): user stays logged in for 24 hours.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

    # Email Configurations
    MAIL_SERVER         = "smtp.gmail.com"
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USE_SSL        = False
    MAIL_USERNAME       = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD       = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")

#Cloudinary..........
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY    = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
