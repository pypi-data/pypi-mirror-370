from uuid import UUID


def convert_uuid_fields(obj: dict | list) -> dict | list | str:
    """Recursively convert UUID objects to strings in nested data structures.

    This utility function traverses dictionaries and lists to convert any UUID
    objects to their string representation. This is useful for JSON serialization
    where UUID objects need to be converted to strings.

    Args:
        obj: The object to process. Can be a dictionary, list, UUID, or any other type.

    Returns:
        The processed object with all UUID instances converted to strings.
        Other types are returned unchanged.

    Examples:
        >>> convert_uuid_fields({"id": UUID("12345678-1234-5678-1234-567812345678")})
        {"id": "12345678-1234-5678-1234-567812345678"}

        >>> convert_uuid_fields([UUID("12345678-1234-5678-1234-567812345678"), "test"])
        ["12345678-1234-5678-1234-567812345678", "test"]
    """
    if isinstance(obj, dict):
        return {k: convert_uuid_fields(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_uuid_fields(i) for i in obj]
    elif isinstance(obj, UUID):
        return str(obj)
    return obj
