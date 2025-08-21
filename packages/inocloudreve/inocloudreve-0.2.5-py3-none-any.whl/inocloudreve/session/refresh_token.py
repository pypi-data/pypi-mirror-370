import httpx

async def refresh_token(self) -> dict:
    """
    Refresh the access token via POST /session/token/refresh.
    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "code": int,
            "msg": str,
            "token": str
        }
    """
    try:
        resp = await self.api_conn.post(
            "/session/token/refresh", json={"refresh_token": self.token.get("refresh_token")}
        )
        resp.raise_for_status()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "status_code": None,
            "msg": f"Request error: {exc}",
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "status_code": exc.response.status_code,
            "msg": f"HTTP error: {exc.response.status_code}",
        }

    try:
        payload = resp.json()
    except ValueError:
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": "Invalid JSON response",
        }

    code = payload.get("code", -1)
    data = payload.get("data", {})

    self.token = data

    return {
        "success": code == 0,
        "status_code": resp.status_code,
        "msg": payload.get("msg", ""),
        "code": code,
        "token": data
    }
