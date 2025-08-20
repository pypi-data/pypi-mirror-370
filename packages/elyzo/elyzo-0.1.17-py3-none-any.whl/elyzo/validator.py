# File: validators/pre_validator.py
# Description: Performs high-level pre-validation checks in the Python CLI
# before sending data to the backend API.

import toml
from pathlib import Path

# Define high-level constraints
MAX_TOML_SIZE_BYTES = 64 * 1024  # 64 KB
MAX_SCRIPT_SIZE_BYTES = 5 * 1024 * 1024 # 5 MB
REQUIRED_TOP_LEVEL_BLOCKS = {"agent", "network"} # Outputs are now optional

def pre_validate_toml(toml_string: str, base_path: str = "."):
    """
    Performs basic, high-level checks on the raw TOML string and its content.

    Args:
        toml_string: The raw string content of the elyzo.toml file.
        base_path: The root directory of the user's project, used to check for the entrypoint file.

    Returns:
        A list of error strings. The list is empty if all pre-checks pass.
    """
    errors = []
    ALLOWED_SECRET_FIELDS = {"description", "allowed"}

    # 1. Check the total size of the configuration file.
    if len(toml_string.encode('utf-8')) > MAX_TOML_SIZE_BYTES:
        errors.append(f"Configuration file size exceeds the maximum limit of {MAX_TOML_SIZE_BYTES / 1024} KB.")
        # If the file is too big, stop here to avoid parsing a huge file.
        return errors

    # 2. Check if the TOML is syntactically valid.
    try:
        parsed_toml = toml.loads(toml_string)
    except toml.TomlDecodeError as e:
        errors.append(f"Invalid TOML format: {e}")
        # If parsing fails, we can't perform any more checks.
        return errors

    # 3. Check for the presence of essential top-level blocks.
    missing_blocks = REQUIRED_TOP_LEVEL_BLOCKS - set(parsed_toml.keys())
    if missing_blocks:
        for block in missing_blocks:
            errors.append(f"Required top-level block '[{block}]' is missing.")

    # 4. Check the agent entrypoint file.
    agent_block = parsed_toml.get("agent", {})
    entrypoint = agent_block.get("entrypoint")

    if not entrypoint:
        errors.append("[agent.entrypoint] is a required field.")
    else:
        entrypoint_path = Path(base_path) / entrypoint
        # 4a. Check if the file exists.
        if not entrypoint_path.is_file():
            errors.append(f"Entrypoint file not found at the specified path: {entrypoint}")
        else:
            # 4b. Check if the file is too large.
            script_size = entrypoint_path.stat().st_size
            if script_size > MAX_SCRIPT_SIZE_BYTES:
                errors.append(
                    f"Agent script '{entrypoint}' is too large "
                    f"({script_size / 1024 / 1024:.2f} MB). "
                    f"The maximum size is {MAX_SCRIPT_SIZE_BYTES / 1024 / 1024} MB."
                )

    # 5. Check the number of inputs and outputs.
    inputs_block = parsed_toml.get("inputs", {})
    if len(inputs_block) > 5:
        errors.append("An agent cannot have more than 5 inputs.")

    outputs_block = parsed_toml.get("outputs", {})
    if len(outputs_block) > 5:
        errors.append("An agent cannot have more than 5 outputs.")

    # 6. Check the secrets block, if it exists.
    secrets_block = parsed_toml.get("secrets")
    if secrets_block is not None:
        if not isinstance(secrets_block, dict):
            errors.append("The [secrets] block must be a table.")
        else:
            for secret_name, secret_config in secrets_block.items():
                if not isinstance(secret_config, dict):
                    errors.append(f"Secret '[secrets.{secret_name}]' must be a table.")
                    continue

                # Check for unexpected fields
                unexpected_fields = set(secret_config.keys()) - ALLOWED_SECRET_FIELDS
                if unexpected_fields:
                    for field in unexpected_fields:
                        errors.append(f"Unexpected field '[secrets.{secret_name}.{field}]'. Only 'description' and 'allowed' are permitted.")

                # Check 'description' field
                description = secret_config.get("description")
                if description is None:
                    errors.append(f"Missing required field 'description' in '[secrets.{secret_name}]'.")
                elif not isinstance(description, str):
                    errors.append(f"Field '[secrets.{secret_name}.description]' must be a string.")

                # Check 'allowed' field
                allowed = secret_config.get("allowed")
                if allowed is None:
                    errors.append(f"Missing required field 'allowed' in '[secrets.{secret_name}]'.")
                elif not isinstance(allowed, list):
                    errors.append(f"Field '[secrets.{secret_name}.allowed]' must be a list of domains.")
                elif not all(isinstance(item, str) for item in allowed):
                    errors.append(f"All items in '[secrets.{secret_name}.allowed]' must be strings.")
                elif not allowed:
                    errors.append(f"The 'allowed' list for secret '[secrets.{secret_name}]' cannot be empty.")


    # 7. Check for conflicts between network and secrets settings.
    network_block = parsed_toml.get("network", {})
    if network_block.get("allow") == "all" and "secrets" in parsed_toml:
        errors.append("Secrets cannot be used when '[network.allow]' is set to 'all'.")

    return errors