from datetime import datetime, timezone, timedelta


# Configuration 
COOLDOWN_SECONDS = 120    # 2 minutes between requests
WINDOW_SECONDS   = 7200   # 2 hour sliding window
MAX_REQUESTS     = 5      # max OTPs per window


def utcnow():
    """Returns current UTC timezone-aware datetime."""
    return datetime.now(timezone.utc)


def _make_aware(dt):
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def check_rate_limit(otp_requests):
    """
    Checks if a new OTP request is allowed.
    """
    now          = utcnow()
    window_start = now - timedelta(seconds=WINDOW_SECONDS)

    # Normalize and filter to 2 hour window 
    recent_requests = []
    for req in (otp_requests or []):
        aware_req = _make_aware(req)
        if aware_req and aware_req > window_start:
            recent_requests.append(aware_req)

    # Sort oldest to newest for accurate calculations
    recent_requests.sort()

    # Check rate limit (5 per 2 hours) 
    if len(recent_requests) >= MAX_REQUESTS:
        oldest_in_window = recent_requests[0]
        window_resets_at = oldest_in_window + timedelta(seconds=WINDOW_SECONDS)
        wait_seconds     = int((window_resets_at - now).total_seconds())

        return {
            "allowed":        False,
            "reason":         "rate_limit",
            "message":        "Too many OTP requests. Please try again later.",
            "wait_seconds":   wait_seconds,
            "clean_requests": recent_requests,
        }

    # Check cooldown (2 minutes since last request) 
    if recent_requests:
        last_request     = recent_requests[-1]
        cooldown_ends_at = last_request + timedelta(seconds=COOLDOWN_SECONDS)

        if now < cooldown_ends_at:
            wait_seconds = int((cooldown_ends_at - now).total_seconds())

            return {
                "allowed":        False,
                "reason":         "cooldown",
                "message":        "Please wait before requesting a new OTP.",
                "wait_seconds":   wait_seconds,
                "clean_requests": recent_requests,
            }

    # Allowed — append new timestamp 
    recent_requests.append(now)

    return {
        "allowed":        True,
        "reason":         None,
        "message":        None,
        "wait_seconds":   0,
        "clean_requests": recent_requests,
    }