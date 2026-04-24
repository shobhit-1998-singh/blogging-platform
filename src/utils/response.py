from flask import jsonify

def make_json_response(response_data, status_code=200):
    """
    Base response function. Wraps any dict into a JSON response.
    Used for custom response structures.
    """
    return jsonify(response_data), status_code


def success_response(message, data=None, status_code=200):
    """
    Standard success response.

    Usage:
      return success_response("Login successful.", data={"token": "..."})

    Output:
      {
        "status":  "success",
        "message": "Login successful.",
        "data":    { "token": "..." }
      }

    data=None is fine — some success responses have no data
    e.g. "OTP sent successfully" doesn't need to return anything extra.
    """
    response = {
        "status":  "success",
        "message": message,
    }

    if data is not None:
        response["data"] = data

    return jsonify(response), status_code


def error_response(message, status_code=400):
    """
    Standard error response.

    Usage:
      return error_response("Email already exists.", 409)

    Output:
      {
        "status":  "failed",
        "message": "Email already exists."
      }

    Why no data field on errors?
      Error responses only need a message — no data to return.
      Keeping it minimal avoids accidentally leaking internal details.
    """
    response = {
        "status":  "failed",
        "message": message,
    }

    return jsonify(response), status_code