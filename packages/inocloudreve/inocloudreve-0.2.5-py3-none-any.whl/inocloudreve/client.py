import httpx

from .site import ping as _ping

from .session import password_sign_in as _password_sign_in
from .session import refresh_token as _refresh_token
from .session import generate_token as _generate_token
from .session import decode_token as _decode_token

from .file import get_file_info as _get_file_info
from .file import create_download_url as _create_download_url
from .file import get_download_url as _get_download_url
from .file import update_file_content as _update_file_content
from .file import list_files as _list_files

from .file import delete_file as _delete_file
from .file import force_unlock as _force_unlock
from .file import get_last_folder_or_file as _get_last_folder_or_file

from .upload import create_upload_session as _create_upload_session
from .upload import delete_upload_session as _delete_upload_session

from .callback import complete_s3_upload as _complete_s3_upload

from .workflow import extract_archive as _extract_archive

from .utils import is_token_valid as _is_token_valid
from .utils import validate_token as _validate_token
from .utils import save_url_as_file as _save_url_as_file
from .utils import read_file_as_bytes as _read_file_as_bytes
from .utils import get_headers as _get_headers

from .utils import download_file as _download_file

from .utils import upload_parts_via_presigned_urls as _upload_parts_via_presigned_urls
from .utils import complete_upload_via_complete_url as _complete_upload_via_complete_url
from .utils import upload_file as _upload_file

class CloudreveClient:
    def __init__(self):
        self.base_url = None
        self.api_conn = None
        self.download_conn = None
        self.upload_conn = None

        self.api_timeout = httpx.Timeout(connect=10.0, read=60, write=60, pool=10.0)
        self.api_limits = httpx.Limits(max_connections=8, max_keepalive_connections=8, keepalive_expiry=120.0)
        self.api_headers = {
                "Connection": "keep-alive",
                "User-Agent": "inocloudreve (+https://github.com/nobandegani/InoCloudreve)"
            }

        self.upload_timeout = httpx.Timeout(connect=10, read=900, write=900, pool=120.0)
        self.upload_limits = httpx.Limits(max_connections=32, max_keepalive_connections=32, keepalive_expiry=300.0)

        self.download_timeout = httpx.Timeout(connect=10, read=900, write=900, pool=120.0)
        self.download_limits = httpx.Limits(max_connections=32, max_keepalive_connections=32, keepalive_expiry=300.0)

        self.email = None
        self.password = None
        self.user_info= None
        self.token = None

    def init(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.api_conn = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.api_timeout,
            limits=self.api_limits,
            headers=self.api_headers,
            http2=True,
            trust_env=False,
            follow_redirects=False
        )
        self.download_conn = httpx.AsyncClient(
            timeout=self.download_timeout,
            limits=self.download_limits,
            http2=True,
            trust_env=False,
            follow_redirects=False
        )
        self.upload_conn = httpx.AsyncClient(
            timeout=self.upload_timeout,
            limits=self.upload_limits,
            http2=True,
            trust_env=False,
            follow_redirects=False
        )

    ping = _ping

    password_sign_in = _password_sign_in
    refresh_token = _refresh_token
    generate_token = _generate_token
    decode_token = _decode_token

    list_files = _list_files
    get_file_info = _get_file_info
    create_download_url = _create_download_url
    get_download_url = _get_download_url
    update_file_content = _update_file_content
    delete_file = _delete_file
    force_unlock = _force_unlock
    get_last_folder_or_file = _get_last_folder_or_file

    create_upload_session = _create_upload_session
    delete_upload_session = _delete_upload_session

    complete_s3_upload = _complete_s3_upload

    extract_archive = _extract_archive

    is_token_valid = _is_token_valid
    validate_token = _validate_token
    save_url_as_file = _save_url_as_file
    read_file_as_bytes = _read_file_as_bytes
    get_headers = _get_headers

    download_file = _download_file

    upload_parts_via_presigned_urls = _upload_parts_via_presigned_urls
    complete_upload_via_complete_url = _complete_upload_via_complete_url
    upload_file = _upload_file

    async def close(self):
        if self.api_conn:
            await self.api_conn.aclose()
        if self.upload_conn:
            await self.upload_conn.aclose()