# File: elyzo/run_agent.py
# Description: Handles the logic for the 'run' command for a deployed agent.

import os
from pathlib import Path
import sys
import requests
import base64
from elyzo.validator import pre_validate_toml # We can reuse parts of this if needed

# Use an environment variable for the API URL for flexibility
API_BASE_URL = os.environ.get("ELYZO_API_URL", "http://192.168.64.9:3000")
# API_BASE_URL = os.environ.get("ELYZO_API_URL", "https://api.elyzo.ai") 

MAX_INPUT_FILE_SIZE_BYTES = 50 * 1024 * 1024 # 50 MB limit for individual input files

def execute_agent_run(agent_id: str, api_key: str, input_args: list, secret_args: list, output_path: str = None):
    """
    Orchestrates a run of a deployed agent by fetching its config, validating inputs,
    and sending the inputs to the backend API for execution.

    Args:
        agent_id: The ID or name of the agent to run.
        api_key: The authenticated developer's API key.
        input_args: A list of input arguments from the CLI.
        secret_args: A list of secret arguments from the CLI.
        output_path: An optional path to a directory where output files will be saved.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 1. Fetch the deployed agent's configuration from the API
    # The agent_id is in the format 'username/agentName', which we need to use directly in the URL
    config_url = f"{API_BASE_URL}/agents/{agent_id}"
    print(f"▶️  Fetching configuration for agent '{agent_id}' from {config_url}...")
    try:
        response = requests.get(config_url, headers=headers, timeout=30)
        response.raise_for_status()
        agent_config = response.json()
        print("✅ Configuration received.")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Failed to fetch agent configuration (HTTP {e.response.status_code}):")
        try:
            error_details = e.response.json()
            print(f"   Error: {error_details.get('error', 'Unknown error')}")
        except ValueError:
            print(f"   {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching config: {e}")
        sys.exit(1)

    # 2. Process and validate the input arguments
    inputs_payload = {}
    provided_input_keys = set()
    defined_inputs = agent_config.get("inputs", {})
    
    for arg in input_args:
        if "=" not in arg:
            print(f"❌ Error: Invalid input format '{arg}'. Please use 'key=value'.")
            sys.exit(1)
        
        key, value = arg.split("=", 1)
        provided_input_keys.add(key)
        
        if key not in defined_inputs:
            print(f"❌ Error: Unexpected input '{key}' was provided. This agent does not define it.")
            sys.exit(1)

        expected_type = defined_inputs[key].get("type")
        
        filename = ""
        input_content = b""

        if expected_type == "text":
            input_content = value.encode('utf-8')
            filename = f"{key}.txt" # Create a default filename for text inputs
            print(f"✅ Using text input for: {key}")
        else:
            file_path = Path(value)
            if not file_path.is_file():
                print(f"❌ Error: Input for '{key}' is defined as a file, but '{value}' is not a valid file path.")
                sys.exit(1)
            
            file_size = file_path.stat().st_size
            if file_size > MAX_INPUT_FILE_SIZE_BYTES:
                print(f"❌ Error: Input file '{value}' is too large.")
                sys.exit(1)

            if expected_type and not value.endswith(expected_type):
                print(f"❌ Error: Input file for '{key}' has the wrong extension. Expected '{expected_type}'.")
                sys.exit(1)
            
            try:
                input_content = file_path.read_bytes()
                filename = file_path.name # Use the actual filename from the path
                print(f"✅ Reading input file: {value}")
            except Exception as e:
                print(f"❌ Error reading input file '{value}': {e}")
                sys.exit(1)

        # *** FIX 1: Match the payload structure from the working test_run.py ***
        inputs_payload[key] = {
            "Name": filename,
            "Content": base64.b64encode(input_content).decode('utf-8')
        }
    
    # 3. Check for missing required inputs
    missing_required_inputs = []
    for input_name, input_spec in defined_inputs.items():
        if input_spec.get("required") and input_name not in provided_input_keys:
            missing_required_inputs.append(input_name)
    
    if missing_required_inputs:
        print("❌ Error: Missing required inputs.")
        for missing in missing_required_inputs:
            print(f"   - Missing: {missing}")
        sys.exit(1)

    # 4. Process and validate secrets
    secrets_payload = {}
    provided_secret_keys = set()
    defined_secrets = agent_config.get("secrets", {})

    for arg in secret_args:
        if "=" not in arg:
            print(f"❌ Error: Invalid secret format '{arg}'. Please use 'key=value'.")
            sys.exit(1)

        key, value = arg.split("=", 1)
        provided_secret_keys.add(key)

        if key not in defined_secrets:
            print(f"❌ Error: Unexpected secret '{key}' was provided. This agent does not define it.")
            sys.exit(1)

        # *** FIX 2: Match the secret encoding from the working test_run.py ***
        secret_content = value.encode('utf-8')
        secrets_payload[key] = base64.b64encode(secret_content).decode('utf-8')
        print(f"✅ Processing secret: {key}")
    
    # 5. Check if all defined secrets were provided
    missing_secrets = set(defined_secrets.keys()) - provided_secret_keys
    if missing_secrets:
        print("❌ Error: Missing required secrets.")
        for missing in missing_secrets:
            print(f"   - Missing secret: {missing}")
        sys.exit(1)

    # 6. Prepare and make the API call to the run endpoint
    # The agent_id from the CLI is already in the 'username/agentName' format.
    run_url = f"{API_BASE_URL}/run/{agent_id}"
    payload = {
        "inputs": inputs_payload,
        "secrets": secrets_payload
    }

    print(f"🚀 Executing agent '{agent_id}'...")
    try:
        response = requests.post(run_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        # 7. Handle successful response
        result = response.json()
    
        print("\n🎉 Run completed successfully!")
        
        if result.get("stdout"):
            print("\n--- Agent STDOUT ---")
            print(result["stdout"].strip())
            print("--------------------")
        
        if result.get("stderr"):
            print("\n--- Agent STDERR ---")
            print(result["stderr"].strip())
            print("--------------------")

        if result.get("outputs"):
            if output_path:
                output_dir = Path(output_path)
            else:
                output_dir = Path.cwd()

            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                print(f"\n--- 💾 Saving Agent Outputs to '{output_dir.resolve()}' ---")
                
                for key, output_file in result["outputs"].items():
                    try:
                        filename = output_file["name"]
                        file_content = base64.b64decode(output_file["content"])
                        save_path = output_dir / filename
                        save_path.write_bytes(file_content)
                        print(f"  ✅ Saved: {filename}")
                    except Exception as e:
                        print(f"  ❌ FAILURE: Could not write file '{filename}': {e}")
                print("-------------------------------------------------")
            except Exception as e:
                print(f"❌ Error: Could not create or write to output directory '{output_dir}': {e}")

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Agent run failed (HTTP {e.response.status_code}):")
        try:
            error_details = e.response.json()
            print(f"   Error: {error_details.get('error', 'An unknown error occurred.')}")
        except ValueError:
            print(f"   {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: Could not connect to the Elyzo API at {run_url}.")
        print(f"   Details: {e}")
        sys.exit(1)
