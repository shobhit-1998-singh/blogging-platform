
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
        return data  

    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned_data[key] = value.strip()  
        else:
            cleaned_data[key] = value  

    return cleaned_data


def get_current_user():
    """
    Returns the full user document for the currently logged-in user.
    """
    user_id = get_jwt_identity()   
    return get_user_by_id(user_id)

def make_aware(dt):
    """
    Ensures a datetime from MongoDB is timezone-aware (UTC).
    """
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt