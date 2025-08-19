# elyzo/output.py
from __future__ import annotations
import errno
import os
import shutil
from pathlib import Path
from typing import Final

class OutputError(Exception):
    """Raised when setting an output file fails."""

_OUTPUT_DIR: Final[str] = os.environ.get("ELYZO_OUTPUT_DIR", "/output")

# Treat these as transient; remove them from the effective extension
_TRANSIENT_SUFFIXES: Final[set[str]] = {".tmp", ".temp", ".partial", ".part", ".bak", "~"}

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

def _effective_extension(p: Path) -> str:
    """Return multi-part extension with transient suffixes removed (e.g., '.tmp')."""
    cleaned = [s for s in p.suffixes if s not in _TRANSIENT_SUFFIXES]
    if not cleaned:
        raise ValueError(f"Cannot infer file type: '{p.name}' only has transient suffixes.")
    return "".join(cleaned)

def setOutputFile(src_path: str, output_name: str, *, overwrite: bool = True) -> str:
    """
    Stage a file into the Elyzo output directory as /output/<output_name><ext>,
    where <ext> is inferred from the source file *after removing transient suffixes*
    like '.tmp', '.partial', etc.

    If the source already lives in /output, it is atomically renamed to the target.
    Otherwise, the file is copied into /output.

    Examples:
      - /output/report.tmp.json -> /output/<output_name>.json  (rename)
      - /work/archive.tar.gz    -> /output/<output_name>.tar.gz (copy)

    Raises:
        FileNotFoundError, IsADirectoryError, FileExistsError, ValueError, OutputError
    """
    if not isinstance(src_path, str):
        raise ValueError("src_path must be a string path.")

    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    if src.is_dir():
        raise IsADirectoryError(f"src_path is a directory: {src}")

    _validate_output_name(output_name)

    ext = _effective_extension(src)  # <-- strips '.tmp' etc.
    out_dir = Path(_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = (out_dir / f"{output_name}{ext}").resolve()

    # No-op if already correct target
    try:
        if src.resolve() == dst:
            return str(dst)
    except Exception:
        pass

    if not overwrite and dst.exists():
        raise FileExistsError(f"Destination already exists: {dst}")

    # If source is already under /output, prefer atomic rename.
    try:
        if src.resolve().is_relative_to(out_dir.resolve()):  # Py 3.9+
            try:
                os.replace(str(src), str(dst))
                return str(dst)
            except OSError as e:
                if e.errno not in (errno.EXDEV,):
                    raise
    except AttributeError:
        # Fallback for Python <3.9
        try:
            src_abs = src.resolve()
            out_abs = out_dir.resolve()
            if str(src_abs).startswith(str(out_abs) + os.sep):
                try:
                    os.replace(str(src), str(dst))
                    return str(dst)
                except OSError as e:
                    if e.errno not in (errno.EXDEV,):
                        raise
        except Exception:
            pass

    # Copy (works across mounts)
    try:
        shutil.copyfile(str(src), str(dst))
    except Exception as e:
        raise OutputError(f"Failed to copy {src} -> {dst}: {e}") from e

    return str(dst)
