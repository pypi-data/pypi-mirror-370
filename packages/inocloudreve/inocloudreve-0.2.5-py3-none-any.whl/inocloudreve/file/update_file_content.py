import httpx

async def update_file_content(
    self,
    file_uri: str,
    content: bytes,
    previous: str | None = None,
) -> dict:
    """
    Upload new content to an existing file via the /file/content endpoint.

    Args:
        self: CloudreveClient instance
        file_uri: the file URI (string)
        content: the binary content to upload (bytes)
        previous: the previous version identifier (string, optional)

    Returns a dict:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str,
            "code": int | None,
            "data": dict
        }
    """

    if not await self.validate_token():
        return {
            "success": False,
            "status_code": None,
            "msg": "Access token expired",
            "code": None,
            "data": {},
        }

    headers = self.get_headers(True, False)
    headers["Content-Length"] = str(len(content))

    params = {"uri": "cloudreve://my/" + file_uri}

    if previous:
        params["previous"] = previous

    try:
        resp = await self.api_conn.put(
            "/file/content",
            params=params,
            headers=headers,
            content=content,
        )
        resp.raise_for_status()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "status_code": None,
            "msg": f"Request error: {exc}",
            "code": None,
            "data": {},
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "status_code": exc.response.status_code,
            "msg": f"HTTP error: {exc.response.status_code}",
            "code": None,
            "data": {},
        }

    try:
        payload = resp.json()
    except ValueError:
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": "Invalid JSON response",
            "code": None,
            "data": {},
        }

    code = payload.get("code", -1)
    data = payload.get("data", {})

    return {
        "success": code == 0,
        "status_code": resp.status_code,
        "msg": payload.get("msg", ""),
        "code": code,
        "data": data,
    }
