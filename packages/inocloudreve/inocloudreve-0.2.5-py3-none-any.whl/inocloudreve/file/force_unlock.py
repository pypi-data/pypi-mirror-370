import httpx

async def force_unlock(
    self,
    tokens: list[str]
) -> dict:
    """
    Force-unlock files via DELETE /file/lock.

    Args:
        self: CloudreveClient instance
        tokens: list of lock tokens (strings)

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "code": int | None,
            "msg": str
        }
    """

    if not await self.validate_token():
        return {
            "success": False,
            "status_code": None,
            "code": None,
            "msg": "Access token expired"
        }

    payload = {"tokens": tokens}

    try:
        resp = await self.api_conn.request("DELETE", "/file/lock", json=payload, headers=self.get_headers(False, True))
        resp.raise_for_status()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "status_code": None,
            "code": None,
            "msg": f"Request error: {exc}"
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "status_code": exc.response.status_code,
            "code": None,
            "msg": f"HTTP error: {exc.response.status_code}"
        }

    # 3) Parse JSON response
    try:
        payload = resp.json()
    except ValueError:
        return {
            "success": False,
            "status_code": resp.status_code,
            "code": None,
            "msg": "Invalid JSON response"
        }

    code = payload.get("code", -1)
    return {
        "success": code == 0,
        "status_code": resp.status_code,
        "code": code,
        "msg": payload.get("msg", "")
    }
