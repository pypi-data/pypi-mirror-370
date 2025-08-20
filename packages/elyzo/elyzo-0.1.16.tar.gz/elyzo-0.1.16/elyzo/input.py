# elyzo/input.py
from __future__ import annotations
import os
from typing import Final, IO

class InputNotFoundError(FileNotFoundError):
    """Raised when a requested input file is not found in the Elyzo environment."""

# Default to sandbox path; allow override for local/dev runs
_INPUTS_BASE_PATH: Final[str] = os.environ.get("ELYZO_INPUTS_DIR", "/input")

def _resolve_input_path(name: str) -> str:
    """Prevent path traversal; ensure final path stays under base dir."""
    base = os.path.abspath(_INPUTS_BASE_PATH)
    candidate = os.path.abspath(os.path.join(base, name))
    if not candidate.startswith(base + os.sep) and candidate != base:
        raise InputNotFoundError(f"Illegal input name {name!r}.")
    return candidate

def getInputAsFile(name: str, mode: str = "rb") -> IO[bytes] | IO[str]:
    """
    Open an input by name as a file object (default binary mode).
    Caller is responsible for closing the returned file.

    Args:
        name: Logical input name (e.g., 'bookingRequest.json').
        mode: File open mode (read-only). Defaults to 'rb'.

    Returns:
        A readable file object.

    Raises:
        TypeError: If 'name' is not a string.
        ValueError: If a write/append mode is requested.
        InputNotFoundError: If the input file doesn't exist.
    """
    if not isinstance(name, str):
        raise TypeError("name must be a string.")
    if any(flag in mode for flag in ("w", "a", "+")):
        raise ValueError("mode must be read-only (e.g., 'r' or 'rb').")

    path = _resolve_input_path(name)
    try:
        return open(path, mode)
    except FileNotFoundError:
        raise InputNotFoundError(
            f"Input '{name}' not found at {_INPUTS_BASE_PATH!r}."
        ) from None
