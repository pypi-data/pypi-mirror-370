import httpx

async def ping(self) -> dict:
    try:
        resp = await self.api_conn.get("/site/ping")
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

    return {
        "success": True,
        "status_code": resp.status_code,
        "msg": payload.get("msg", ""),
        "code": payload.get("code", 0),
        "data": payload.get("data", "")
    }