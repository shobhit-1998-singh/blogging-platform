from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_mail import Mail
from config import Config 
from flask_jwt_extended import JWTManager

# Initialize Flask app
app = Flask(__name__)


# Load ALL config values from Config class in one line.
app.config.from_object(Config)


# Initialize MongoDB and Mail
mongo = PyMongo(app)
mail = Mail(app)
jwt   = JWTManager(app)


# ── JWT error handlers 

@jwt.unauthorized_loader
def missing_token_callback(error):
    """Fired when Authorization header is completely missing."""
    return jsonify({
        "status":  "failed",
        "message": "Authorization token is missing. Please log in."
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Fired when the token exists but signature is wrong / malformed."""
    return jsonify({
        "status":  "failed",
        "message": "Invalid token. Please log in again."
    }), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Fired when the token is valid but has passed its expiry time."""
    return jsonify({
        "status":  "failed",
        "message": "Token has expired. Please log in again."
    }), 401