import httpx

async def create_download_url(
    self,
    uris: list[str],
    download: bool | None = None,
    redirect: bool | None = None,
    entity: str | None = None,
    use_primary_site_url: bool | None = None,
    skip_error: bool | None = None,
    archive: bool | None = None,
    no_cache: bool | None = None,
    init_uri: str = "cloudreve://my/"
) -> dict:
    """
    Create signed download URLs via POST /file/url.

    Args:
        self: CloudreveClient instance
        uris: list of file URI strings
        download: whether to force download (bool, optional)
        redirect: whether to return a redirect URL (bool, optional)
        entity: entity string (optional)
        use_primary_site_url: use primary site URL (bool, optional)
        skip_error: skip missing files silently (bool, optional)
        archive: archive files into zip (bool, optional)
        no_cache: disable CDN caching (bool, optional)
        init_uri: initial URI (string, default "cloudreve://my/")

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str,
            "code": int | None,
            "urls": list[{"url": str}],
            "expires": str
        }
    """

    if not await self.validate_token():
        return {
            "success": False,
            "status_code": None,
            "msg": "Access token expired"
        }

    file_names: list[str] = []
    extensions: list[str] = []
    for uri in uris:
        name = uri.rstrip('/').split('/')[-1]

        if '.' in name and not name.startswith('.'):
            base, ext = name.rsplit('.', 1)
            file_names.append(base)
            extensions.append(f'.{ext}')
        else:
            file_names.append(name)
            extensions.append('.zip')

    uris = [f"{init_uri}{u}" for u in uris]

    payload = {}

    payload["uris"] = uris

    if download is not None:
        payload["download"] = download
    if redirect is not None:
        payload["redirect"] = redirect
    if entity is not None:
        payload["entity"] = entity
    if use_primary_site_url is not None:
        payload["use_primary_site_url"] = use_primary_site_url
    if skip_error is not None:
        payload["skip_error"] = skip_error
    if archive is not None:
        payload["archive"] = archive
    if no_cache is not None:
        payload["no_cache"] = no_cache

    try:
        resp = await self.api_conn.post("/file/url", json=payload, headers=self.get_headers())
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

    return {
        "success": code == 0,
        "status_code": resp.status_code,
        "msg": payload.get("msg", ""),
        "code": code,
        "urls": data.get("urls", {}),
        "file_names": file_names,
        "extensions": extensions,
        "expires": data.get("expires", "")
    }
