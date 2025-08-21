def get_headers(
    self,
    include_auth: bool = True,
    include_content_type: bool = True
) -> dict:
    """
    Build common request headers.

    Args:
        include_auth: if True, include the Authorization header
        include_content_type: if True, include Content-Type: application/json

    Returns:
        A dict of headers.
    """
    headers = {}

    if include_auth:
        token = self.token.get("access_token", "")
        headers["Authorization"] = f"Bearer {token}"

    if include_content_type:
        headers["Content-Type"] = "application/json"

    return headers
