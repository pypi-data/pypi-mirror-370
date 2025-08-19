# File: elyzo/codegen.py
# Description: Handles the generation of boilerplate agent code.

from __future__ import annotations

def generate_boilerplate_code(config: dict) -> str:
    """Generates the content for the boilerplate Python agent file."""

    # 1) Build the dynamic 'elyzo test' command from the config
    command_parts = ['elyzo test']
    if config.get("inputs"):
        for name, details in config["inputs"].items():
            ftype = details.get("type", "")
            command_parts.append(f'--input {name}=path/to/your/file{ftype}')
    if config.get("secrets"):
        for name in config["secrets"].keys():
            command_parts.append(f'--secret {name}=YOUR_KEY_HERE')

    test_command = " ".join(command_parts)

    # 2) Generate per-input snippets with correct modes/parsers
    need_json = False
    need_csv = False
    inputs_snippets = []

    def snip_for_input(input_name: str, ext: str) -> str:
        nonlocal need_json, need_csv
        e = (ext or "").lower()
        # Normalize a few common forms
        if e in ("json", "csv", "txt", "pdf", "jpg", "jpeg", "png"):
            e = "." + e

        if e == ".json":
            need_json = True
            return (
                f'# {input_name} ({e})\n'
                f'with elyzo.getInputAsFile("{input_name}", mode="r") as f:\n'
                f'    {input_name}_json = json.load(f)\n'
                f'    # print(f"{input_name}: keys -> {{list({input_name}_json)[:5]}}")'
            )
        elif e == ".csv":
            need_csv = True
            return (
                f'# {input_name} ({e})\n'
                f'with elyzo.getInputAsFile("{input_name}", mode="r") as f:\n'
                f'    # Choose DictReader if you expect a header row:\n'
                f'    reader = csv.reader(f)\n'
                f'    {input_name}_rows = list(reader)\n'
                f'    # print(f"{input_name}: rows -> {{len({input_name}_rows)}}")'
            )
        elif e == ".txt":
            return (
                f'# {input_name} ({e})\n'
                f'with elyzo.getInputAsFile("{input_name}", mode="r") as f:\n'
                f'    {input_name}_text = f.read()\n'
                f'    # print(f"{input_name}: chars -> {{len({input_name}_text)}}")'
            )
        elif e == ".pdf":
            return (
                f'# {input_name} ({e})\n'
                f'with elyzo.getInputAsFile("{input_name}") as f:  # bytes\n'
                f'    {input_name}_pdf_bytes = f.read()\n'
                f'    # Tip: use PyPDF2 or pdfminer.six to parse pages if available.\n'
                f'    # print(f"{input_name}: bytes -> {{len({input_name}_pdf_bytes)}}")'
            )
        elif e in (".jpg", ".jpeg", ".png"):
            return (
                f'# {input_name} ({e})\n'
                f'with elyzo.getInputAsFile("{input_name}") as f:  # bytes\n'
                f'    {input_name}_img_bytes = f.read()\n'
                f'    # Tip: use Pillow (PIL) if installed to open images from bytes.\n'
                f'    # print(f"{input_name}: bytes -> {{len({input_name}_img_bytes)}}")'
            )
        else:
            # Fallback: raw bytes
            return (
                f'# {input_name} ({e or "unknown"})\n'
                f'with elyzo.getInputAsFile("{input_name}") as f:  # bytes\n'
                f'    {input_name}_bytes = f.read()\n'
                f'    # print(f"{input_name}: bytes -> {{len({input_name}_bytes)}}")'
            )

    if config.get("inputs"):
        for name, details in config["inputs"].items():
            ext = details.get("type", "")
            inputs_snippets.append(snip_for_input(name, ext))

    inputs_code = "\n\n".join(inputs_snippets) if inputs_snippets else "# No inputs defined in your elyzo.toml."

    # 3) Secrets snippets
    secrets_snippets = []
    if config.get("secrets"):
        for secret_name in config["secrets"].keys():
            secrets_snippets.append(f'elyzo.getSecret("{secret_name}")')

    secrets_code = "\n".join(secrets_snippets) if secrets_snippets else "# No secrets defined in your elyzo.toml. Requires restricted access to the internet."

    # 4) Outputs snippets (use setOutputFile and honor configured extensions)
    outputs_snippets = []
    if config.get("outputs"):
        for out_name, details in config["outputs"].items():
            ext = details.get("type", "")
            # Normalize ext for the placeholder path only
            sample_ext = ext if str(ext).startswith(".") else f".{ext}" if ext else ""
            sample_path = f"/work/path/to/your/file{sample_ext}" if sample_ext else "/work/path/to/your/file"
            outputs_snippets.append(f'elyzo.setOutputFile("{sample_path}", "{out_name}")')

    outputs_code = "\n".join(outputs_snippets) if outputs_snippets else "# No outputs defined in your elyzo.toml."

    # 5) Assemble imports (only what we actually used)
    import_lines = ["import elyzo"]
    if need_json:
        import_lines.append("import json")
    if need_csv:
        import_lines.append("import csv")
    imports_block = "\n".join(import_lines)

    # 6) Final boilerplate assembly
    boilerplate = f'''
"""

(1/2) Uncomment code -> Add your agent logic -> Test with the command below:
{test_command}

(2/2) When you're done testing, you can deploy with:
elyzo deploy

"""
{imports_block}

{inputs_code}

"""
TODO:
Add your agent's core logic here.
You can do anything you want!
"""

# WARNING: Using a secret locks all future internet access to only that secret's allowed domain.
{secrets_code}

{outputs_code}
'''.strip()

    return boilerplate
