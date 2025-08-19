# File: deploy.py
# Description: Handles the logic for the 'deploy' command.

import os
from pathlib import Path
import sys
import requests
import toml
from elyzo.validator import pre_validate_toml

# --- Configuration ---
CONFIG_FILENAME = "elyzo.toml"
# Use an environment variable for the API URL for flexibility
API_BASE_URL = os.environ.get("ELYZO_API_URL", "http://192.168.64.9:3000") 
# API_BASE_URL = os.environ.get("ELYZO_API_URL", "https://api.elyzo.ai") 

def deploy_agent(api_key: str):
    """
    Orchestrates the agent deployment process from validation to API call.

    Args:
        api_key: The authenticated developer's API key.
    """
    print("Starting deployment process...")
    
    # 1. Check if elyzo.toml exists
    config_path = Path.cwd() / CONFIG_FILENAME
    if not config_path.is_file():
        print(f"❌ Error: Your elyzo.toml file ('{CONFIG_FILENAME}') was not found in this directory.")
        print("   Please run this command from your agent's project root.")
        sys.exit(1)
        
    print(f"✅ Found elyzo.toml file: {config_path}")

    # 2. Read and pre-validate the TOML configuration
    try:
        toml_content = config_path.read_text()
        validation_errors = pre_validate_toml(toml_content, base_path=str(Path.cwd()))
    except Exception as e:
        print(f"❌ Error reading or validating your elyzo.toml file: {e}")
        sys.exit(1)

    if validation_errors:
        print(f"❌ Validation failed for '{CONFIG_FILENAME}':")
        for error in validation_errors:
            print(f"   - {error}")
        sys.exit(1)
        
    print("✅ Local validation passed.")

    # 3. Read the agent script file
    try:
        parsed_toml = toml.loads(toml_content)
        entrypoint = parsed_toml.get("agent", {}).get("entrypoint")
        if not entrypoint:
            # This should be caught by the validator, but it's good to be safe
            print("❌ Error: [agent.entrypoint] is missing in your elyzo.toml.")
            sys.exit(1)
        
        agent_script_path = Path.cwd() / entrypoint
        agent_code_content = agent_script_path.read_text()
        print(f"✅ Reading agent script: {agent_script_path}")

    except Exception as e:
        print(f"❌ Error reading agent script file '{entrypoint}': {e}")
        sys.exit(1)

    # 4. Prepare and make the API call
    api_url = f"{API_BASE_URL}/register-agent"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "elyzo_toml": toml_content,
        "agent_code": agent_code_content
    }

    print(f"🚀 Deploying agent '{parsed_toml['agent']['name']}' to Elyzo...")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)

        # 5. Handle successful response
        response_data = response.json()
        deployment_id = response_data.get("deployment", {}).get("id")
        print("\n🎉 Agent deployed successfully! Stuck? Go to:\nhttps://elyzo.ai/projects")
        print(f"   Deployment ID: {deployment_id}")
        if response_data.get("warnings"):
            print("\n⚠️  Deployment Warnings:")
            for warning in response_data["warnings"]:
                print(f"   - {warning}")

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Deployment failed (HTTP {e.response.status_code}):")
        try:
            # Try to print the detailed error from the API
            error_details = e.response.json()
            print(f"   Error: {error_details.get('error')}")
            if error_details.get('details'):
                for detail in error_details['details']:
                    print(f"   - {detail}")
        except ValueError:
            # If the response is not JSON, print the raw text
            print(f"   {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: Could not connect to the Elyzo API at {api_url}.")
        print(f"   Please check your network connection. Details: {e}")
        sys.exit(1)

