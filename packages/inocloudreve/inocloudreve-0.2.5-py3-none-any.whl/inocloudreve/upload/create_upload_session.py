import httpx

async def create_upload_session(
    self,
    uri: str,
    size: int,
    policy_id: str,
    last_modified: int | None = None,
    mime_type: str | None = None,
    metadata: str | None = None,
    entity_type: str | None = None,
    init_uri: str = "cloudreve://my/"
) -> dict:
    """
    Create an upload session via POST /file/upload.

    Args:
        self: CloudreveClient instance
        uri: the target URI (string)
        size: file size in bytes (integer)
        policy_id: storage policy ID (string)
        last_modified: timestamp of last modification (integer, optional)
        mime_type: MIME type of the file (string, optional)
        metadata: custom metadata (string, optional)
        entity_type: entity type (string, optional)
        init_uri: initial URI (string, default "cloudreve://my/")

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str,
            "code": int | None,
            "session_id": str,
            "upload_id": str,
            "chunk_size": int,
            "expires": int,
            "storage_policy": dict,
            "uri": str,
            "callback_secret": str
        }
    """
    if not await self.validate_token():
        return {
            "success": False,
            "status_code": None,
            "msg": "Access token expired",
            "code": None,
            "session_id": "",
            "upload_id": "",
            "chunk_size": 0,
            "expires": 0,
            "storage_policy": {},
            "uri": "",
            "callback_secret": ""
        }

    payload = {"uri": init_uri + uri, "size": size, "policy_id": policy_id}

    if last_modified is not None:
        payload["last_modified"] = last_modified
    if mime_type is not None:
        payload["mime_type"] = mime_type
    if metadata is not None:
        payload["metadata"] = metadata
    if entity_type is not None:
        payload["entity_type"] = entity_type

    try:
        resp = await self.api_conn.put("/file/upload", json=payload, headers=self.get_headers())
        resp.raise_for_status()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "status_code": None,
            "msg": f"Request error: {exc}",
            "code": None,
            "session_id": "",
            "upload_id": "",
            "chunk_size": 0,
            "expires": 0,
            "storage_policy": {},
            "uri": "",
            "callback_secret": ""
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "status_code": exc.response.status_code,
            "msg": f"HTTP error: {exc.response.status_code}",
            "code": None,
            "session_id": "",
            "upload_id": "",
            "chunk_size": 0,
            "expires": 0,
            "storage_policy": {},
            "uri": "",
            "callback_secret": ""
        }

    try:
        body = resp.json()
    except ValueError:
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": "Invalid JSON response",
            "code": None,
            "session_id": "",
            "upload_id": "",
            "chunk_size": 0,
            "expires": 0,
            "storage_policy": {},
            "uri": "",
            "callback_secret": ""
        }

    code = body.get("code", -1)
    data = body.get("data", {})

    return {
        "success": code == 0,
        "status_code": resp.status_code,
        "msg": body.get("msg", ""),
        "code": code,
        "data": data,
        "session_id": data.get("session_id", ""),
        "upload_id": data.get("upload_id", ""),
        "chunk_size": data.get("chunk_size", 0),
        "expires": data.get("expires", 0),
        "upload_urls": data.get("upload_urls", []),
        "credential": data.get("credential", ""),
        "completeURL": data.get("completeURL", ""),
        "storage_policy": data.get("storage_policy", {}),
        "uri": data.get("uri", ""),
        "callback_secret": data.get("callback_secret", "")
    }
