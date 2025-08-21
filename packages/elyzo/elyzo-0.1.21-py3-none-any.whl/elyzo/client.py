# File: elyzo/client.py
# Description: Provides a Python client SDK for interacting with and running Elyzo agents.

import os
import base64
from pathlib import Path
from typing import Dict, Optional, Any, Union

import requests

# Use an environment variable for the API URL for flexibility, with a production default.
API_BASE_URL = os.environ.get("ELYZO_API_URL", "https://api.elyzo.ai")
MAX_INPUT_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

class ElyzoError(Exception):
    """Custom exception for errors originating from the Elyzo client."""
    pass

class RunResult:
    """A structured object to hold the results of an agent run."""
    def __init__(self, stdout: str, stderr: str, outputs: Dict[str, bytes]):
        self.stdout = stdout
        self.stderr = stderr
        self.outputs = outputs

    def __repr__(self) -> str:
        return f"RunResult(stdout_len={len(self.stdout)}, stderr_len={len(self.stderr)}, outputs={list(self.outputs.keys())})"

    def save_outputs(self, output_dir: Union[str, Path] = "."):
        """
        Saves all output files to a specified directory.

        Args:
            output_dir: The directory where output files will be saved. Defaults to the current directory.
        """
        path = Path(output_dir)
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"💾 Saving outputs to '{path.resolve()}'...")
            for name, content in self.outputs.items():
                (path / name).write_bytes(content)
                print(f"  ✅ Saved: {name}")
        except IOError as e:
            raise ElyzoError(f"Failed to write to output directory '{path}': {e}") from e


class Agent:
    """A class representing a remote Elyzo agent, providing an interface to run it."""

    def __init__(self, agent_id: str, api_key: Optional[str] = None):
        """
        Initializes the Agent instance.

        Args:
            agent_id: The unique identifier for the agent, in 'username/agentName' format.
            api_key: Your Elyzo API key. If not provided, it will be read from the ELYZO_API_KEY environment variable.

        Raises:
            ElyzoError: If the API key is not found or if the agent configuration cannot be fetched.
        """
        self.agent_id = agent_id
        self.api_key = api_key or os.environ.get("ELYZO_API_KEY")
        if not self.api_key:
            raise ElyzoError("API key not provided. Pass it to the Agent constructor or set the ELYZO_API_KEY environment variable.")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.config = self._fetch_config()

    def _fetch_config(self) -> Dict[str, Any]:
        """Fetches the agent's configuration from the API."""
        config_url = f"{API_BASE_URL}/agents/{self.agent_id}"
        try:
            response = requests.get(config_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"Failed to fetch config for '{self.agent_id}' (HTTP {e.response.status_code})"
            try:
                details = e.response.json().get('error', e.response.text)
                error_msg += f": {details}"
            except ValueError:
                pass
            raise ElyzoError(error_msg) from e
        except requests.exceptions.RequestException as e:
            raise ElyzoError(f"Network error fetching config for '{self.agent_id}': {e}") from e

    def run(self, inputs: Dict[str, Union[str, Path]] = None, secrets: Dict[str, str] = None) -> RunResult:
        """
        Runs the agent with the provided inputs and secrets.

        Args:
            inputs: A dictionary mapping input names to their values.
                    For file inputs, the value should be a string path or a Path object.
                    For text inputs, the value should be the string content.
            secrets: A dictionary mapping secret names to their string values.

        Returns:
            A RunResult object containing stdout, stderr, and any output files.

        Raises:
            ElyzoError: If input validation fails or the API call is unsuccessful.
        """
        inputs = inputs or {}
        secrets = secrets or {}

        inputs_payload = self._process_inputs(inputs)
        secrets_payload = self._process_secrets(secrets)

        run_url = f"{API_BASE_URL}/run/{self.agent_id}"
        payload = {"inputs": inputs_payload, "secrets": secrets_payload}

        try:
            response = requests.post(run_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            result_json = response.json()
            
            outputs_content = {
                key: base64.b64decode(output_file["content"])
                for key, output_file in result_json.get("outputs", {}).items()
            }
            
            return RunResult(
                stdout=result_json.get("stdout", ""),
                stderr=result_json.get("stderr", ""),
                outputs=outputs_content
            )
        except requests.exceptions.HTTPError as e:
            error_msg = f"Agent run failed for '{self.agent_id}' (HTTP {e.response.status_code})"
            try:
                details = e.response.json().get('error', e.response.text)
                error_msg += f": {details}"
            except ValueError:
                pass
            raise ElyzoError(error_msg) from e
        except requests.exceptions.RequestException as e:
            raise ElyzoError(f"Network error during agent run: {e}") from e

    def _process_inputs(self, inputs: Dict[str, Union[str, Path]]) -> Dict[str, Dict[str, str]]:
        """Validates, reads, and encodes input data for the API payload."""
        payload = {}
        defined_inputs = self.config.get("inputs", {})

        for key, value in inputs.items():
            if key not in defined_inputs:
                raise ElyzoError(f"Unexpected input '{key}' was provided. This agent does not define it.")

            spec = defined_inputs[key]
            filename = ""
            content = b""

            if spec.get("type") == "text":
                content = str(value).encode('utf-8')
                filename = f"{key}.txt"
            else:
                path = Path(value)
                if not path.is_file():
                    raise ElyzoError(f"Input '{key}' expects a file, but path '{value}' is not a valid file.")
                if path.stat().st_size > MAX_INPUT_FILE_SIZE_BYTES:
                    raise ElyzoError(f"Input file '{path}' for '{key}' exceeds the size limit.")
                
                content = path.read_bytes()
                filename = path.name

            payload[key] = {
                "Name": filename,
                "Content": base64.b64encode(content).decode('utf-8')
            }

        missing = [name for name, spec in defined_inputs.items() if spec.get("required") and name not in inputs]
        if missing:
            raise ElyzoError(f"Missing required inputs: {', '.join(missing)}")
            
        return payload

    def _process_secrets(self, secrets: Dict[str, str]) -> Dict[str, str]:
        """Validates and encodes secrets for the API payload."""
        payload = {}
        defined_secrets = self.config.get("secrets", {})

        for key, value in secrets.items():
            if key not in defined_secrets:
                raise ElyzoError(f"Unexpected secret '{key}' was provided. This agent does not define it.")
            
            content = str(value).encode('utf-8')
            payload[key] = base64.b64encode(content).decode('utf-8')
        
        missing = [name for name in defined_secrets if name not in secrets]
        if missing:
            raise ElyzoError(f"Missing required secrets: {', '.join(missing)}")
            
        return payload