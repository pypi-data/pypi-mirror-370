# File: auth.py (or credentials.py)
# Description: Handles saving, loading, and retrieving the Elyzo API key.

import os
from pathlib import Path
import getpass

# --- Configuration Constants ---
CONFIG_DIR = Path.home() / ".elyzo"
CREDENTIALS_FILE = CONFIG_DIR / "api_key"  # Renamed for maximum clarity
API_KEY_ENV_VAR = "ELYZO_API_KEY"
API_KEY_PREFIX = "elyzo_sk_"
DOCS_LINK = "https://elyzo.ai/quickstart"  # placeholder

def is_valid_api_key(key: str) -> bool:
    """Checks if the provided key has the correct format."""
    if not key or not isinstance(key, str):
        return False
    return key.startswith(API_KEY_PREFIX) and len(key[len(API_KEY_PREFIX):]) >= 10

def save_api_key(key: str):
    """Saves the API key to the credentials file."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CREDENTIALS_FILE, "w") as f:
            f.write(f"{API_KEY_ENV_VAR}={key.strip()}\n")
    except IOError as e:
        print(f"❌ Error: Could not write to credentials file at {CREDENTIALS_FILE}.")
        print(f"   Please check permissions. Details: {e}")
        exit(1)

def load_api_key_from_file():
    """Loads the API key from the credentials file, if it exists."""
    if not CREDENTIALS_FILE.exists():
        return None
    with open(CREDENTIALS_FILE, "r") as f:
        for line in f:
            if line.startswith(f"{API_KEY_ENV_VAR}="):
                return line.strip().split("=", 1)[1]
    return None

def prompt_for_api_key():
    """Prompts the user to securely enter their API key."""
    prompt_message = f"Enter your API key (find it at {DOCS_LINK}): "
    try:
        key = getpass.getpass(prompt_message).strip()
    except Exception:
        # Fallback for environments where getpass is not available
        key = input(prompt_message).strip()

    if not is_valid_api_key(key):
        print("❌ Invalid API key format.")
        exit(1)

    return key

def get_api_key(cli_arg: str = None):
    """
    Retrieves the API key based on a clear hierarchy:
    1. A key provided directly as a command-line argument.
    2. A key found in the environment variable ELYZO_API_KEY.
    3. A key loaded from the ~/.elyzo/api_key file.
    4. If none are found, prompts the user to enter one.
    """
    # 1. Check for a key provided as a CLI argument
    if cli_arg:
        key = cli_arg.strip()
        if not is_valid_api_key(key):
            print("❌ Invalid API key format provided as argument.")
            exit(1)
        # Save the key for future use
        save_api_key(key)
        print("✅ API key saved for future use.")
        return key

    # 2. Check for an environment variable
    env_key = os.environ.get(API_KEY_ENV_VAR)
    if env_key and is_valid_api_key(env_key):
        return env_key

    # 3. Check for a key in the credentials file
    file_key = load_api_key_from_file()
    if file_key and is_valid_api_key(file_key):
        return file_key

    # 4. If no key is found, prompt the user
    print("Could not find an Elyzo API key.")
    prompted_key = prompt_for_api_key()
    save_api_key(prompted_key)
    print("✅ API key saved for future use.")
    return prompted_key

def reset_api_key():
    """Forces a prompt to enter and save a new API key."""
    print("🔁 Resetting Elyzo API key.")
    key = prompt_for_api_key()
    save_api_key(key)
    print("✅ API key reset successfully.")

