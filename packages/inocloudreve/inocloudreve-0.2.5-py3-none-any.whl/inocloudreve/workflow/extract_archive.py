import httpx

async def extract_archive(
    self,
    src: list[str],
    dst: str,
    preferred_node_id: str | None = None,
    encoding: str | None = None,
    init_uri: str = "cloudreve://my/"
) -> dict:
    """
    Extract one or more archives on the server.

    Calls POST /file/extract.

    Args:
        self: CloudreveClient instance
        src: list of archive URIs to extract (e.g. ["cloudreve://my/path/archive.zip"])
        dst: destination folder URI (string)
        preferred_node_id: which storage node to run the extraction on (optional)
        encoding: filename encoding inside the archive (optional)
        init_uri: initial URI (string, default "cloudreve://my/")

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "code": int | None,
            "msg": str,
            "data": {
                "created_at": str,
                "updated_at": str,
                "id": str,
                "status": str,
                "type": str,
                "summary": dict
            }
        }
    """
    if not await self.validate_token():
        return {
            "success": False,
            "status_code": None,
            "code": None,
            "msg": "Access token expired",
        }
    src = [f"{init_uri}{u}" for u in src]
    dst = f"{init_uri}{dst}"
    payload: dict = {"src": src, "dst": dst}
    if preferred_node_id is not None:
        payload["preferred_node_id"] = preferred_node_id
    if encoding is not None:
        payload["encoding"] = encoding

    headers = self.get_headers()
    try:
        resp = await self.api_conn.post("/workflow/extract", json=payload, headers=headers)
        resp.raise_for_status()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "status_code": None,
            "code": None,
            "msg": f"Request error: {exc}",
            "data": {}
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "status_code": exc.response.status_code,
            "code": None,
            "msg": f"HTTP error: {exc.response.status_code}",
            "data": {}
        }

    try:
        result = resp.json()
    except ValueError:
        return {
            "success": False,
            "status_code": resp.status_code,
            "code": None,
            "msg": "Invalid JSON response",
            "data": {}
        }

    code = result.get("code", -1)
    data = result.get("data", {})
    return {
        "success": code == 0,
        "status_code": resp.status_code,
        "code": code,
        "msg": result.get("msg", ""),
        "data": data,
        "id": data.get("id", None)
    }
