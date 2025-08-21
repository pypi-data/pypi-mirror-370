import httpx

async def delete_file(
    self,
    uris: list[str],
    unlink: bool | None = None,
    skip_soft_delete: bool | None = None,
    init_uri: str = "cloudreve://my/"
) -> dict:
    """
    Delete one or more files via DELETE /file.

    Args:
        self: CloudreveClient instance
        uris: list of file URIs (strings)
        unlink: if True, permanently remove the files (bool, optional)
        skip_soft_delete: if True, bypass soft-delete and hard-delete immediately (bool, optional)
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

    full_uris = [f"{init_uri}{u}" for u in uris]

    payload = {"uris": full_uris}
    if unlink is not None:
        payload["unlink"] = unlink
    if skip_soft_delete is not None:
        payload["skip_soft_delete"] = skip_soft_delete

    try:
        resp = await self.api_conn.request("DELETE", "/file", json=payload, headers=self.get_headers())
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
