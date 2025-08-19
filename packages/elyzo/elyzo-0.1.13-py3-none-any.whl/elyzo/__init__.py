# elyzo/__init__.py
from .secrets import getSecret as getSecret, SecretNotFoundError as SecretNotFoundError

__all__ = ["getSecret", "getSecrets", "SecretNotFoundError"]

# Optional convenience: plural helper
from typing import Dict, Iterable

def getSecrets(names: Iterable[str]) -> Dict[str, str]:
    """
    Batch-read multiple secrets. Returns a dict of {name: value}.
    Raises SecretNotFoundError if any requested secret is missing.
    """
    from .secrets import getSecret, SecretNotFoundError  # local import to avoid import cycles
    out: Dict[str, str] = {}
    missing = []
    for n in names:
        try:
            out[n] = getSecret(n)
        except SecretNotFoundError:
            missing.append(n)
    if missing:
        # Keep the same error type so callers can catch a single exception
        raise SecretNotFoundError(f"Missing secrets: {', '.join(missing)}")
    return out
