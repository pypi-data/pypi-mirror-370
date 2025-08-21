# Cloudreve Python Client

An **async** Python client for the [Cloudreve API](https://github.com/cloudreve/).  
Supports authentication, file operations, token management, and utilities—built on [httpx](https://www.python-httpx.org/) and [aiofiles](https://github.com/Tinche/aiofiles).

---

## Important Note
> **Active Development**  
> This client library is under active development and is not yet feature-complete. It was built to satisfy specific use-cases and may change without warning.
>
> **Not Production-Ready**  
> Use at your own risk. Do **not** deploy this in production environments unless you fully understand its internals and have thoroughly tested it for your needs.
>
> Contributions, feedback, and issue reports are welcome—but please be cautious if you plan to rely on this library for critical workloads.
---
## Features

- **Health check** (`ping()`)

- **Authentication**
  - `password_sign_in(email, password, captcha=None, ticket=None)`
  - `refresh_token(refresh_token)`
  - `is_token_valid()`
  - `validate_token()`

- **File operations**
  - `list_files(uri, page=0, page_size=50, order_by="created_at", order_direction="asc", next_page_token=None)`
  - `get_file_info(file_uri, file_id, extended=False, folder_summary=False)`
  - `create_download_url(uris, download=False, redirect=False, entity=None, use_primary_site_url=False, skip_error=False, archive=False, no_cache=False)`
  - `get_download_url(uris, download=False, redirect=False, entity=None, use_primary_site_url=False, skip_error=False, archive=False, no_cache=False)`
  - `update_file_content(file_uri, content, previous=None)`
  - `create_upload_session(uri, filename, size, chunk_size, expire_in, ...)`
  - `delete_upload_session(id, uri)`
  - `delete_file(uris, unlink=False, skip_soft_delete=False)`
  - `force_unlock(tokens)`
  - `get_last_folder_or_file(uri)`

- **Download & save**
  - `save_url_as_file(url, save_dir, filename, extension, overwrite=True)`

- **Utilities**
  - `read_file_as_bytes(path)`
  - `get_headers(include_auth=True, include_content_type=True)`


---

## Installation

```bash
# Install from PyPI
pip install InoCloudreve

# install locally:
git clone https://github.com/nobandegani/InoCloudreve.git
cd InoCloudreve
pip install -e .
```
---

## License
Mozilla Public License Version 2.0