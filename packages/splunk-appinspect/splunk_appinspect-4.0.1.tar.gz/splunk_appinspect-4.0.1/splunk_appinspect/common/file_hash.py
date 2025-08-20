"""
Module to provide high level common functionalities
"""

import hashlib
from io import BufferedReader
from pathlib import Path


def md5(file_path: Path) -> str:
    """Generate md5 hash hex string."""
    with open(file_path, "rb") as file:
        return hashlib.md5(file.read()).hexdigest()
