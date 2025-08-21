import os
import httpx
import aiofiles

async def save_url_as_file(
    self,
    url: str,
    save_dir: str,
    filename: str,
    extension: str,
    overwrite: bool = True
) -> dict:
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{filename}{extension}")

    if not overwrite and os.path.exists(file_path):
        return {
            "success": False,
            "status_code": None,
            "code": None,
            "msg": f"File already exists at {file_path}",
            "path": file_path
        }

    try:
        resp = await self.download_conn.get(url)
        resp.raise_for_status()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "status_code": None,
            "msg": f"Request error: {exc}",
            "path": ""
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "status_code": exc.response.status_code,
            "msg": f"HTTP error: {exc.response.status_code}",
            "path": ""
        }

    content = resp.content
    if not content:
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": "Empty response body",
            "path": ""
        }

    ct = resp.headers.get("Content-Type", "")
    if not ct.startswith("application/") and not ct.startswith("image/") and not ct.startswith(
            "application/octet-stream"):
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": f"Unexpected content-type: {ct}",
            "path": ""
        }

    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(resp.content)
    except OSError as exc:
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": f"File write error: {exc}",
            "path": ""
        }

    return {
        "success": True,
        "status_code": resp.status_code,
        "msg": "",
        "path": file_path
    }