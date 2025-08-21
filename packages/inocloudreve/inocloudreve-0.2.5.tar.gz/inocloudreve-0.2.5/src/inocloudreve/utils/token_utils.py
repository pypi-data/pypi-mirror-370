from datetime import datetime

def is_token_valid(self, type: str = "Access") -> bool:
    """
    Check whether the stored access token is still valid.
    Returns False if no token is set, the timestamp is malformed, or it's expired.
    """
    expires_str = None
    if self.token and isinstance(self.token, dict):
        if type == "Access":
            expires_str = self.token.get("access_expires")
        elif type == "Refresh":
            expires_str = self.token.get("refresh_expires")
    if not expires_str:
        return False

    try:
        expires_dt = datetime.fromisoformat(expires_str)
    except ValueError:
        return False

    now = datetime.now(expires_dt.tzinfo)
    return now < expires_dt

async def validate_token(self) -> bool:
    """
    Check whether the stored access token is still valid.
    if not will refresh it
    """

    if self.is_token_valid():
        return True

    refresh_token = await self.refresh_token()
    if refresh_token["success"]:
        return True

    return False