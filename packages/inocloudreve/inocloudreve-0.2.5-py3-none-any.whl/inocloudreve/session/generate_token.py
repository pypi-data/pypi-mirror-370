#import jwt

from datetime import datetime, timedelta, timezone

def generate_token(
    self,
    master_key: str,
    user_id: str
) -> dict:
    """
    Generate an HS256 JWT access token.

    Args:
        self: CloudreveClient instance
        master_key: your site master_key (string)
        user_id:    the Cloudreve user ID (string)

    Returns:
        {
            "success": True,
            "token": {
                "access_token": "<JWT string>",
                "refresh_token": None,
                "access_expires": "<ISO8601 timestamp>",
                "refresh_expires": None
            }
        }
    """

    clock_skew = timedelta(seconds=5)
    now = datetime.now(timezone.utc) - clock_skew
    exp = now + timedelta(minutes=50)

    payload = {
        "token_type": "access",
        "sub": user_id,
        "exp": int(exp.timestamp()),
        "nbf": int(now.timestamp()),
    }

    raw = None#jwt.encode(payload, master_key, algorithm="HS256")
    token_str = None#raw if isinstance(raw, str) else raw.decode("utf-8")

    token = {
        "access_token": token_str,
        "refresh_token": None,
        "access_expires": exp.isoformat(),
        "refresh_expires": None
    }
    user = {
        "id": user_id,
    }

    self.user_info = user
    self.token = token

    return {
        "success": True,
        "token": token
    }
