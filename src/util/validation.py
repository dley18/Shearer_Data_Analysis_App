"""Data validation end error handling utilities"""

import os
from typing import List


def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a file exists.

    Parameters:
      file_path (str): Path to the file

    Returns:
      bool: True if file exists, False otherwise
    """

    return os.path.exists(file_path) and os.path.isfile(file_path)


def validate_file_extension(file_path: str, allowed_extensions: List[str]) -> tuple:
    """
    Validate file extension.

    Parameters:
      file_path (str): Path to the file
      allowed_extensions (List[str]): List of allowed extensions (with dots)

    Returns:
      tuple: (is_valid, error_message)
    """

    if not file_path:
        return False, "File path connot be empty"

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext not in [e.lower() for e in allowed_extensions]:
        return (
            False,
            f"Invalid file extension: {ext}. ALlowed: {', '.join(allowed_extensions)}",
        )

    return True, ""
