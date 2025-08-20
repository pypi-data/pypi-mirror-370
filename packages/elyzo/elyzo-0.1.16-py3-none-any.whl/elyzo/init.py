# File: elyzo/init.py
# Description: Handles the interactive creation of the elyzo.toml configuration file.

import re
import toml
from pathlib import Path
import elyzo.codegen

def _is_valid_domain(domain: str) -> bool:
    """Checks if a string is a valid domain format using a simple regex."""
    if len(domain) > 253:
        return False
    # A standard regex for domain validation
    pattern = re.compile(
        r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$'
    )
    return re.match(pattern, domain) is not None

def _ask_question(prompt, default=None):
    """Helper to ask a question on one line and get input on the next."""
    full_prompt = f"{prompt}"
    if default:
        full_prompt += f" ({default})"
    # Add a newline and an arrow for the input prompt
    full_prompt += "\n→ "
    return input(full_prompt).strip()

def _ask_yes_no(prompt):
    """Helper to ask a yes/no question on one line and get input on the next."""
    full_prompt = f"{prompt} (y/n)\n→ "
    answer = input(full_prompt).lower().strip()
    return answer == 'y'

def _ask_yes_no_with_yes_default(prompt):
    """Helper to ask a yes/no question where the default is 'yes'."""
    full_prompt = f"{prompt} (Y/n)\n→ "
    answer = input(full_prompt).lower().strip()
    # If the user types 'n', return False. Otherwise (including empty), return True.
    return answer != 'n'

def initialize_project():
    """
    Guides the user through creating an elyzo.toml file.
    """
    print("Welcome to Elyzo! Let's set up your agent configuration.\n")
    
    ALLOWED_FILE_TYPES = [".json", ".csv", ".txt", ".pdf", ".jpg", ".jpeg", ".png"]

    config = {
        "agent": {},
        "resources": {},
        "network": {},
        "outputs": {}
    }

    # --- Agent Section ---
    while True:
        agent_name = _ask_question("What is the name of your agent?", "e.g. my-agent")
        if re.match(r"^[a-z0-9-]+$", agent_name):
            config["agent"]["name"] = agent_name
            break
        print("❗️ Invalid name. Please use only lowercase letters, numbers, and dashes.")

    description = _ask_question("Briefly describe what this agent does (optional, press Enter to skip):")
    config["agent"]["description"] = description or "A placeholder description for this agent."

    entrypoint_filename = "elyzo-agent.py"
    config["agent"]["entrypoint"] = entrypoint_filename

    # --- Inputs Section ---
    if _ask_yes_no("Does your agent accept any files as input?"):
        config["inputs"] = {}
        while True:
            while True:
                input_name = _ask_question("Input name?", "use camelCase, e.g. flightDetails")
                if input_name.strip():
                    break
                print("❗️ Input name cannot be empty. Please try again.")
            
            while True:
                file_type = _ask_question("File type?", f"e.g. {', '.join(ALLOWED_FILE_TYPES)}").strip()
                if file_type in ALLOWED_FILE_TYPES:
                    break
                if not file_type:
                    print("❗️ File type cannot be empty. Please try again.")
                else:
                    print(f"❗️ Invalid file type. Must be one of: {', '.join(ALLOWED_FILE_TYPES)}")

            is_required = _ask_yes_no(f"Is '{input_name}' required?")
            
            config["inputs"][input_name] = {
                "type": file_type,
                "description": "A placeholder description for this input.",
                "required": is_required,
            }

            if not _ask_yes_no("Any more inputs?"):
                break

    # --- Outputs Section ---
    if _ask_yes_no("Does your agent produce any output files?"):
        config["outputs"] = {}
        while True:
            while True:
                output_name = _ask_question("Output name?", "use camelCase, e.g. 'bookingConfirmation'")
                if output_name.strip():
                    break
                print("❗️ Output name cannot be empty. Please try again.")

            while True:
                file_type = _ask_question("File type?", f"e.g. {', '.join(ALLOWED_FILE_TYPES)}").strip()
                if file_type in ALLOWED_FILE_TYPES:
                    break
                if not file_type:
                    print("❗️ File type cannot be empty. Please try again.")
                else:
                    print(f"❗️ Invalid file type. Must be one of: {', '.join(ALLOWED_FILE_TYPES)}")

            config["outputs"][output_name] = {
                "type": file_type,
                "description": "A placeholder description for this output.",
            }
            
            if not _ask_yes_no("Any more outputs?"):
                break

    # --- Resources Section ---
    while True:
        timeout_str = _ask_question("Set request/response timeout in seconds:", "default: 30")
        if not timeout_str.strip():
            config["resources"]["timeout_seconds"] = 30
            break
        try:
            timeout = int(timeout_str)
            if 0 < timeout <= 600:
                config["resources"]["timeout_seconds"] = timeout
                break
            else:
                print("❗️ Timeout must be between 1 and 600 seconds.")
        except ValueError:
            print("❗️ Please enter a valid number.")

    # --- Network and Secrets Section ---
    has_secrets = False
    if _ask_yes_no("If your agent can only access specific domains, 'y'. Otherwise, 'n' if your agent can access the entire internet."):
        while True:
            domains_str = _ask_question("List allowed domains (comma-separated):", "e.g. example.com, api.openai.com")
            potential_domains = [d.strip() for d in domains_str.split(',') if d.strip()]
            
            if not potential_domains:
                print("❗️ You must provide at least one domain for restricted access. Please try again.")
                continue

            invalid_domains = [domain for domain in potential_domains if not _is_valid_domain(domain)]
            
            if not invalid_domains:
                config["network"]["allow"] = potential_domains
                break
            else:
                print(f"❗️ The following are not valid domain names: {', '.join(invalid_domains)}. Please check your list and try again.")
        
        if _ask_yes_no("Do you want to define any secrets? (e.g. API keys, passwords)"):
            has_secrets = True
            config["secrets"] = {}
            while True:
                while True:
                    secret_name = _ask_question("Secret name?", "use camelCase, e.g. apiKey")
                    if secret_name.strip():
                        break
                    print("❗️ Secret name cannot be empty. Please try again.")

                while True:
                    network_allowed_domains = config.get("network", {}).get("allow", [])
                    
                    available_domains_str = "\nAvailable domains from your network settings:\n" + "\n".join(f"- {d}" for d in network_allowed_domains)
                    prompt_question = f"Which domains should '{secret_name}' be allowed to access (comma-separated)?{available_domains_str}"
                    
                    domains_str = _ask_question(prompt_question)
                    potential_domains = [d.strip() for d in domains_str.split(',') if d.strip()]

                    if not potential_domains:
                        print("❗️ You must provide at least one domain. Please try again.")
                        continue
                    
                    invalid_format_domains = [d for d in potential_domains if not _is_valid_domain(d)]
                    not_allowed_domains = [d for d in potential_domains if d not in network_allowed_domains]

                    error_messages = []
                    if invalid_format_domains:
                        error_messages.append(f"Invalid domain format: {', '.join(invalid_format_domains)}")
                    if not_allowed_domains:
                        error_messages.append(f"Not in network allow list: {', '.join(not_allowed_domains)}")
                    
                    if error_messages:
                        print(f"❗️ Errors found: {'; '.join(error_messages)}. Please try again.")
                        continue
                    
                    allowed_domains_list = potential_domains
                    break

                config["secrets"][secret_name] = {
                    "description": "A placeholder description for this secret.",
                    "allowed": allowed_domains_list
                }
                if not _ask_yes_no("Any more secrets?"):
                    break
    else:
        config["network"]["allow"] = "all"

    # --- Generate TOML file ---
    toml_path = Path("elyzo.toml")
    with toml_path.open("w") as f:
        f.write("# Elyzo Agent Configuration\n\n")
        
        # Agent
        f.write("[agent]\n")
        f.write(f'name = "{config["agent"]["name"]}"\n')
        f.write(f'description = "{config["agent"]["description"]}"\n')
        f.write(f'entrypoint = "{config["agent"]["entrypoint"]}"\n\n')

        # Resources
        f.write("[resources]\n")
        f.write(f'timeout_seconds = {config["resources"]["timeout_seconds"]}\n\n')

        # Inputs
        if "inputs" in config and config["inputs"]:
            f.write("[inputs]\n")
            for name, details in config["inputs"].items():
                req_str = str(details["required"]).lower()
                f.write(
                    f'{name} = {{ type = "{details["type"]}", description = "{details["description"]}", required = {req_str} }}\n'
                )
            f.write("\n")
        else:
            f.write("# [inputs]\n")
            f.write('# flightDetails = { type = ".json", description = "The flight details.", required = true }\n\n')

        # Outputs
        if "outputs" in config and config["outputs"]:
            f.write("[outputs]\n")
            for name, details in config["outputs"].items():
                f.write(
                    f'{name} = {{ type = "{details["type"]}", description = "{details["description"]}" }}\n'
                )
            f.write("\n")
        else:
            f.write("# [outputs]\n")
            f.write('# bookingConfirmation = { type = ".json", description = "The booking confirmation." }\n\n')

        # Network
        f.write("[network]\n")
        allow_val = config["network"]["allow"]
        if isinstance(allow_val, list):
            f.write(toml.dumps({"allow": allow_val}))
            f.write('# allow = "all"\n\n')
        else:
            f.write('allow = "all"\n')
            f.write('# allow = ["api.openai.com", "example.com"]\n\n')
        
        # Secrets
        if has_secrets:
            f.write("[secrets]\n")
            for name, details in config["secrets"].items():
                # Use toml.dumps to safely format the list and description string
                allowed_str = toml.dumps({"k": details["allowed"]}).split("=", 1)[1].strip()
                description_str = toml.dumps({"k": details["description"]}).split("=", 1)[1].strip()
                f.write(
                    f'{name} = {{ description = {description_str}, allowed = {allowed_str} }}\n'
                )
            f.write("\n")
        else:
             f.write("# [secrets]\n")
             f.write('# openAIKey = { description = "API key for OpenAI", allowed = ["api.openai.com"] }\n\n')

    # --- Generate Boilerplate Python File ---
    entrypoint_path = Path(entrypoint_filename)
    
    should_write_file = True
    if entrypoint_path.exists():
        print(f"\n❗️ The file '{entrypoint_filename}' already exists.")
        should_write_file = _ask_yes_no_with_yes_default("Do you want to overwrite it with the boilerplate?")

    if should_write_file:
        try:
            boilerplate_content = elyzo.codegen.generate_boilerplate_code(config)
            with entrypoint_path.open("w") as f:
                f.write(boilerplate_content + "\n")
        except Exception as e:
            print(f"❌ Error generating boilerplate file: {e}")

    # --- Final Instructions ---
    print("\n🎉 Setup complete!")
    print(f"(1/2) Created agent file: `{entrypoint_filename}`")
    print("(2/2) Created configuration: `elyzo.toml`")
    print(f"\nGo to the generated '{entrypoint_filename}'...")