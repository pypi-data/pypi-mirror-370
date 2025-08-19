# elyzo/output.py
from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import Final

class OutputError(Exception):
    """Raised when setting an output file fails."""

# Default to sandbox path; allow override for local/dev
_OUTPUT_DIR: Final[str] = os.environ.get("ELYZO_OUTPUT_DIR", "/output")

def _validate_output_name(name: str) -> None:
    if not isinstance(name, str) or not name:
        raise ValueError("output_name must be a non-empty string.")
    if os.sep in name or (os.altsep and os.altsep in name):
        raise ValueError("output_name must not contain path separators.")
    if name != os.path.basename(name):
        raise ValueError("output_name must be a simple base name.")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    if not set(name) <= allowed:
        raise ValueError("output_name may only contain letters, numbers, '-' and '_'.")

def setOutputFile(src_path: str, output_name: str, *, overwrite: bool = True) -> str:
    """
    Stage a file into the Elyzo output directory.

    Uses the source file's extension(s) to create: /output/<output_name><ext>

    Examples:
      - src: /work/dir/other/report.json  -> /output/<output_name>.json
      - src: /work/x/archive.tar.gz       -> /output/<output_name>.tar.gz

    Args:
        src_path: Path to an existing source file.
        output_name: Logical output base name (no extension).
        overwrite: If False and destination exists, raise FileExistsError.

    Returns:
        Absolute destination path in the output directory.

    Raises:
        FileNotFoundError: If src_path doesn't exist.
        IsADirectoryError: If src_path is a directory.
        FileExistsError: If overwrite=False and destination exists.
        ValueError: If output_name invalid or source has no extension.
        OutputError: On copy failure.
    """
    if not isinstance(src_path, str):
        raise ValueError("src_path must be a string path.")

    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    if src.is_dir():
        raise IsADirectoryError(f"src_path is a directory: {src}")

    _validate_output_name(output_name)

    # Capture full multi-part extension (e.g., ".tar.gz")
    suffixes = src.suffixes
    ext = "".join(suffixes)
    if not ext:
        raise ValueError(f"Cannot infer file type: '{src}' has no extension.")

    out_dir = Path(_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = (out_dir / f"{output_name}{ext}").resolve()

    # If already the intended file, no-op
    try:
        if src.resolve() == dst:
            return str(dst)
    except Exception:
        pass

    if not overwrite and dst.exists():
        raise FileExistsError(f"Destination already exists: {dst}")

    try:
        # copy (works across mounts); preserves content
        shutil.copyfile(str(src), str(dst))
    except Exception as e:
        raise OutputError(f"Failed to copy {src} -> {dst}: {e}") from e

    return str(dst)
