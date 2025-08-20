# elyzo/__init__.py
from __future__ import annotations
from typing import Dict, Iterable

# Secrets API
from .secrets import getSecret as getSecret, SecretNotFoundError as SecretNotFoundError

# Inputs API
from .input import getInputAsFile as getInputAsFile, InputNotFoundError as InputNotFoundError

# Outputs API (new signature: (src_path, output_name))
from .output import setOutputFile as setOutputFile, OutputError as OutputError

__all__ = [
    "getSecret",
    "getSecrets",
    "SecretNotFoundError",
    "getInputAsFile",
    "InputNotFoundError",
    "setOutputFile",
    "OutputError",
]

def getSecrets(names: Iterable[str]) -> Dict[str, str]:
    """Batch-read multiple secrets; raises if any are missing."""
    from .secrets import getSecret, SecretNotFoundError
    out: Dict[str, str] = {}
    missing = []
    for n in names:
        try:
            out[n] = getSecret(n)
        except SecretNotFoundError:
            missing.append(n)
    if missing:
        raise SecretNotFoundError(f"Missing secrets: {', '.join(missing)}")
    return out
