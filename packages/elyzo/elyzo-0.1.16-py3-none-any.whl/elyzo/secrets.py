# elyzo/secrets.py
import os

class SecretNotFoundError(Exception):
    """Raised when a requested secret is not found in the Elyzo environment."""
    pass

# The absolute path to the directory where secrets are mounted in the sandbox.
_SECRETS_BASE_PATH = "/secrets"

def getSecret(secret_name: str) -> str:
    """
    Retrieves a secret's value from the Elyzo execution environment.

    This function reads the content of the specified secret file, which is securely
    mounted by the Elyzo platform. It returns the secret as a UTF-8 decoded string,
    stripping any leading or trailing whitespace.

    Args:
        secret_name: The name of the secret to retrieve. This should match the
                     name defined in your agent's configuration.

    Returns:
        The secret's value as a string.

    Raises:
        SecretNotFoundError: If no secret with the given name can be found.
        TypeError: If 'secret_name' is not a string.
    """
    if not isinstance(secret_name, str):
        raise TypeError("secret_name must be a string.")

    # Construct the full, absolute path to the secret file.
    secret_path = os.path.join(_SECRETS_BASE_PATH, secret_name)

    try:
        with open(secret_path, "r", encoding="utf-8") as f:
            # .strip() is important to remove trailing newlines common in secrets
            return f.read().strip()
    except FileNotFoundError:
        # Catch the low-level error and raise a more informative, specific exception.
        raise SecretNotFoundError(
            f"Secret '{secret_name}' not found. Please ensure it is defined in your "
            "agent's configuration and provided at invocation time."
        ) from None