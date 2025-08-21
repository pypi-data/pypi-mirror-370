
async def get_last_folder_or_file(
        self,
        uri: str,
        file_type: str = "folder",
        order_by: str = "name",
        order_direction: str = "desc"
) -> dict:
    """
    Get last folder GET /file.

    Args:
        self: CloudreveClient instance
        uri: the directory URI (string)
        file_type: "folder" or "file" (string, default "folder")
        order_by: field to order by ("name" or "size" or "created_at" or "updated_at", default "name")
        order_direction: sort direction ("asc" or "desc", default "desc")

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str,
            "code": int | None,
            "data": dict  # contains files list, parent, pagination, etc.
            "last": dict,
            "last_name": str
        }
    """

    final_uri = uri + "?type=" + file_type
    result = await self.list_files(
        uri=final_uri,
        page=0,
        page_size=50,
        order_by=order_by,
        order_direction=order_direction)
    if not result["success"]:
        return {
            "success": result["success"],
            "status_code": result["status_code"],
            "msg": result["msg"],
            "code": result["code"],
            "data": result,
            "last": None,
            "last_name": None
        }
    if not result["files"]:
        return {
            "success": result["success"],
            "status_code": result["status_code"],
            "msg": "Files or folders empty",
            "code": result["code"],
            "data": result,
            "last": None,
            "last_name": None
        }

    return {
        "success": result["success"],
        "status_code": result["status_code"],
        "msg": result["msg"],
        "code": result["code"],
        "data": result,
        "last": result["files"][0],
        "last_name": result["files"][0]["name"]
    }
