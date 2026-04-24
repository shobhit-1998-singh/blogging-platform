
from flask_jwt_extended import get_jwt_identity
from src.models.UserModel import get_user_by_id
from datetime import timezone


def remove_white_space(data):
    """
    Removes leading and trailing whitespaces from string values in a dictionary.

    :param data: Dictionary containing key-value pairs.
    :return: Cleaned dictionary with trimmed string values.
    """
    if not isinstance(data, dict):
        return data  # Return as is if not a dictionary

    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned_data[key] = value.strip()  # Trim whitespace for strings
        else:
            cleaned_data[key] = value  # Keep other data types unchanged

    return cleaned_data


def get_current_user():
    """
    Returns the full user document for the currently logged-in user.
    """
    user_id = get_jwt_identity()   # extracts user_id string from JWT token
    return get_user_by_id(user_id) # converts to ObjectId, queries MongoDB

def make_aware(dt):
    """
    Ensures a datetime from MongoDB is timezone-aware (UTC).

    PyMongo strips tzinfo on read — this reattaches it safely.
    Use this every time you compare a MongoDB datetime with
    datetime.now(timezone.utc).

    Usage:
      created_at = make_aware(document.get("created_at"))
    """
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt