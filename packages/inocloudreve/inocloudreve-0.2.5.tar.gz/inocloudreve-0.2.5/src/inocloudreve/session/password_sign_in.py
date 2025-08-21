import httpx

async def password_sign_in(
        self,
        email: str,
        password: str,
        captcha: str = None,
        ticket: str = None,
) -> dict:
    """
    Authenticate via POST /session/token.
    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str,
            "code": int,
            "user": dict,
            "token": dict
        }
    """

    self.email = email
    self.password = password

    payload = {"email": email, "password": password}

    if captcha is not None:
        payload["captcha"] = captcha
    if ticket is not None:
        payload["ticket"] = ticket

    try:
        resp = await self.api_conn.post("/session/token", json=payload)
        resp.raise_for_status()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "status_code": None,
            "msg": f"Request error: {exc}"
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "status_code": exc.response.status_code,
            "msg": f"HTTP error: {exc.response.status_code}"
        }

    try:
        payload = resp.json()
    except ValueError:
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": "Invalid JSON response"
        }

    code = payload.get("code", -1)
    data = payload.get("data", {})
    user = data.get("user", {})
    token = data.get("token", {})

    self.user_info = user
    self.token = token

    return {
        "success": code == 0,
        "status_code": resp.status_code,
        "msg": payload.get("msg", ""),
        "code": code,
        "user": user,
        "token": token,
    }