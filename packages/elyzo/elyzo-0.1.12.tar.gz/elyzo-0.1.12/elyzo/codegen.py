# File: elyzo/codegen.py
# Description: Handles the generation of boilerplate agent code.

def generate_boilerplate_code(config: dict) -> str:
    """Generates the content for the boilerplate Python agent file."""
    
    # 1. Generate the dynamic 'elyzo test' command from the config
    command_parts = ['elyzo test']
    if config.get("inputs"):
        for name, details in config["inputs"].items():
            command_parts.append(f'--input {name}=path/to/your/file{details["type"]}')
    if config.get("secrets"):
        for name in config["secrets"].keys():
            command_parts.append(f'--secret {name}=YOUR_KEY_HERE')
    
    test_command = " ".join(command_parts)

    # 2. Create helpful code snippets based on the config
    inputs_code = "# No inputs defined in your elyzo.toml."
    if config.get("inputs"):
        first_input_name = list(config["inputs"].keys())[0]
        inputs_code = (
            f'    # Example: Access the "{first_input_name}" input file\n'
            f'    try:\n'
            f'        input_path = client.inputs.get("{first_input_name}")\n'
            f'        with open(input_path, "r") as f:\n'
            f'            content = f.read()\n'
            f'            print(f"Successfully read {{len(content)}} bytes from {first_input_name}")\n'
            f'    except Exception as e:\n'
            f'        print(f"Error reading input \'{first_input_name}\': {{e}}")'
        )

    secrets_code = "# No secrets defined in your elyzo.toml."
    if config.get("secrets"):
        first_secret_name = list(config["secrets"].keys())[0]
        secrets_code = (
            f'    # Example: Access the "{first_secret_name}" secret\n'
            f'    api_key = client.secrets.get("{first_secret_name}")\n'
            f'    if api_key:\n'
            f'        print("Successfully loaded secret \'{first_secret_name}\'")\n'
            f'    else:\n'
            f'        print("Warning: Secret \'{first_secret_name}\' not found.")'
        )

    # 3. Assemble the full boilerplate file content using an f-string
    boilerplate = f'''
# TODO: Uncomment code -> Add your agent logic -> Test with the command below:
# {test_command}

import elyzo
# import os # os is useful for accessing secrets via environment variables as well

# Initialize the Elyzo client, which provides access to inputs, outputs, and secrets.
client = elyzo.Client()

def main():
    """
    Main function for the agent.
    This is where you'll implement the agent's core logic.
    """
    print("🚀 Agent starting...")

    # --- Accessing Inputs ---
{inputs_code}

    # --- Accessing Secrets ---
{secrets_code}

    # --- Agent Logic ---
    # TODO: Add your agent's core logic here.
    # You can read from inputs, perform computations, call APIs with secrets, etc.
    
    print("✅ Agent finished.")

if __name__ == "__main__":
    main()
'''
    return boilerplate.strip()