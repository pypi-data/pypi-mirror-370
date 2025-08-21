import os
import asyncio
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
    """
    Download a file from `url` and save it to `save_dir/filename+extension`.

    Args:
        self: CloudreveClient instance
        url: the download URL (string)
        save_dir: directory path to save the file (string)
        filename: base name for the saved file (string)
        extension: file extension including the dot, e.g. ".zip" or ".png" (string)
        overwrite: if False and file exists, abort with error (bool, default True)

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str,
            "code": int | None,
            "path": str  # full path to the saved file
        }
    """

    os.makedirs(save_dir, exist_ok=True)
    final_path = os.path.join(save_dir, f"{filename}{extension}")
    tmp_path = final_path + ".part"

    if not overwrite and os.path.exists(final_path):
        return {
            "success": False,
            "status_code": None,
            "msg": f"File already exists at {final_path}",
            "path": final_path
        }

    MAX_RETRIES = 3
    BACKOFF_SEC = 0.8
    CHUNK_SIZE = 8 * 1024 * 1024  # 8 MiB

    try:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    except OSError:
        pass

    last_status = None

    for attempt in range(1, MAX_RETRIES + 1):
        bytes_written = 0
        try:
            async with self.download_conn.stream("GET", url) as resp:
                last_status = resp.status_code
                resp.raise_for_status()

                content_length = resp.headers.get("Content-Length")
                expected_size = int(content_length) if content_length and content_length.isdigit() else None

                async with aiofiles.open(tmp_path, "wb") as f:
                    async for chunk in resp.aiter_bytes(CHUNK_SIZE):
                        if not chunk:
                            continue
                        await f.write(chunk)
                        bytes_written += len(chunk)

            if expected_size is not None and bytes_written != expected_size:
                raise IOError(f"Incomplete download: expected {expected_size} bytes, got {bytes_written}")

            os.replace(tmp_path, final_path)

            return {
                "success": True,
                "status_code": last_status,
                "msg": "",
                "path": final_path
            }

        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError) as exc:
            if attempt == MAX_RETRIES:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except OSError:
                    pass
                return {
                    "success": False,
                    "status_code": last_status,
                    "msg": f"Timeout/connection error: {exc}",
                    "path": ""
                }
            await asyncio.sleep(BACKOFF_SEC * attempt)

        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            retryable = status in (408, 429, 500, 502, 503, 504)
            if not retryable or attempt == MAX_RETRIES:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except OSError:
                    pass
                return {
                    "success": False,
                    "status_code": status,
                    "msg": f"HTTP error: {status}",
                    "path": ""
                }
            await asyncio.sleep(BACKOFF_SEC * attempt)

        except Exception as exc:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            return {
                "success": False,
                "status_code": last_status,
                "msg": f"Download error: {exc}",
                "path": ""
            }

    return {
        "success": False,
        "status_code": last_status,
        "msg": "Unknown download failure",
        "path": ""
    }



async def read_file_as_bytes(self, path: str) -> dict:
    """
    Read a file from disk and return its bytes and size.

    Args:
        self: CloudreveClient instance
        path: path to the file as a string

    Returns:
        {
            "success": bool,
            "msg": str,
            "data": bytes,
            "size": int
        }
    """
    try:
        async with aiofiles.open(path, "rb") as f:
            data = await f.read()
        return {
            "success": True,
            "msg": "",
            "data": data,
            "size": len(data),
        }
    except Exception as exc:
        return {
            "success": False,
            "msg": f"Error reading file: {exc}",
            "data": b"",
            "size": 0,
        }
