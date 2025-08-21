import httpx

async def delete_upload_session(
    self,
    session_id: str,
    uri: str,
    init_uri: str = "cloudreve://my/"
) -> dict:
    """
    Delete an upload session via DELETE /file/upload.

    Args:
        self: CloudreveClient instance
        session_id: the upload session ID (string)
        uri: the file URI (string)
        init_uri: initial URI (string, default "cloudreve://my/")

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

    payload = {"id": session_id, "uri": init_uri + uri}

    try:
        resp = await self.api_conn.request("DELETE", "/file/upload", json=payload, headers=self.get_headers())
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
