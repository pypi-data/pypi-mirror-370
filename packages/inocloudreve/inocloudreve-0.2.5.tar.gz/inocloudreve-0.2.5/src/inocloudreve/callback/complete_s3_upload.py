import httpx
from pathlib import Path

async def complete_s3_upload(
    self,
    session_id: str,
    key_id: str
) -> dict:
    """
     Notify Cloudreve that all parts have been uploaded via S3 multipart.

    Calls POST /callback/s3/{session_id}/{key}.

    Args:
        self: CloudreveClient instance
        session_id: the upload session ID returned by create_upload_session
        key_id: the object key (path under `cloudreve://my/…`, e.g. "Spark/test/file.zip")

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "code": int | None,
            "msg": str
        }
    """

    path = f"/callback/s3/{session_id}/{Path(key_id).name.split("_", 1)[0]}"

    try:
        resp = await self.api_conn.get(path)
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
        "msg": payload.get("msg", "callback success")
    }
