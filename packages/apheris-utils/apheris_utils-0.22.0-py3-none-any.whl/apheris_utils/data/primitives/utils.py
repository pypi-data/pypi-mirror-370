from pathlib import Path


def validate_is_in_directory(sub_path: Path, base_path: Path) -> None:
    """
    Validate that sub_path is within base_path. Use this helper function to prevent
    path traversal attacks.

    Args:
        sub_path: A path that is expected to be within base_path.
        base_path: A path that is expected to contain `sub_path`.

    Raises:
        ValueError: If sub_path is not a subdirectory of base_path.

    """
    try:
        sub_path.resolve().relative_to(base_path.resolve())
    except ValueError:
        raise ValueError(f"Path traversal attempt detected: {sub_path}")
