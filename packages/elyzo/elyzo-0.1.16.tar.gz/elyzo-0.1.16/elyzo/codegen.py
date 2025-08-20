# File: elyzo/codegen.py
# Description: Handles the generation of boilerplate agent code.

from __future__ import annotations

def generate_boilerplate_code(config: dict) -> str:
    """Generates the content for the boilerplate Python agent file."""

    # Helpers
    def norm_ext(ext: str | None) -> tuple[str, str]:
        """
        Return (with_dot, without_dot) lowercase.
        "" -> ("", "")
        "CSV" -> (".csv", "csv")
        ".Json" -> (".json", "json")
        """
        e = (ext or "").strip()
        if not e:
            return "", ""
        e = e.lower()
        e_wo = e[1:] if e.startswith(".") else e
        return f".{e_wo}", e_wo

    # 1) Build the dynamic 'elyzo test' command from the config
    command_parts = ['elyzo test']
    if config.get("inputs"):
        for name, details in config["inputs"].items():
            with_dot, _ = norm_ext(details.get("type", ""))
            command_parts.append(f'--input {name}=path/to/your/file{with_dot}')
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
        with_dot, wo_dot = norm_ext(ext)
        file_id = f"{input_name}{with_dot}" if with_dot else input_name

        if with_dot == ".json":
            need_json = True
            return (
                f'# {input_name} ({with_dot})\n'
                f'with elyzo.getInputAsFile("{file_id}", mode="r") as f:  # mode="r" for text; mode="rb" for binary\n'
                f'    {input_name}_json = json.load(f)\n'
                f'    # print(f"{input_name}: keys -> {{list({input_name}_json)[:5]}}")'
            )
        elif with_dot == ".csv":
            need_csv = True
            return (
                f'# {input_name} ({with_dot})\n'
                f'with elyzo.getInputAsFile("{file_id}", mode="r") as f:  # mode="r" for text; mode="rb" for binary\n'
                f'    # Choose DictReader if you expect a header row:\n'
                f'    reader = csv.reader(f)\n'
                f'    {input_name}_rows = list(reader)\n'
                f'    # print(f"{input_name}: rows -> {{len({input_name}_rows)}}")'
            )
        elif with_dot == ".txt":
            return (
                f'# {input_name} ({with_dot})\n'
                f'with elyzo.getInputAsFile("{file_id}", mode="r") as f:  # mode="r" for text; mode="rb" for binary\n'
                f'    {input_name}_text = f.read()\n'
                f'    # print(f"{input_name}: chars -> {{len({input_name}_text)}}")'
            )
        elif with_dot == ".pdf":
            return (
                f'# {input_name} ({with_dot})\n'
                f'with elyzo.getInputAsFile("{file_id}") as f:  # mode="r" for text; mode="rb" for binary\n'
                f'    {input_name}_pdf_bytes = f.read()\n'
                f'    # Tip: use PyPDF2 or pdfminer.six to parse pages if available.\n'
                f'    # print(f"{input_name}: bytes -> {{len({input_name}_pdf_bytes)}}")'
            )
        elif with_dot in (".jpg", ".jpeg", ".png"):
            return (
                f'# {input_name} ({with_dot})\n'
                f'with elyzo.getInputAsFile("{file_id}") as f:  # mode="r" for text; mode="rb" for binary\n'
                f'    {input_name}_img_bytes = f.read()\n'
                f'    # Tip: use Pillow (PIL) if installed to open images from bytes.\n'
                f'    # print(f"{input_name}: bytes -> {{len({input_name}_img_bytes)}}")'
            )
        else:
            # Fallback: raw bytes
            ext_note = with_dot or "unknown"
            return (
                f'# {input_name} ({ext_note})\n'
                f'with elyzo.getInputAsFile("{file_id}") as f:  # mode="r" for text; mode="rb" for binary\n'
                f'    {input_name}_bytes = f.read()\n'
                f'    # print(f"{input_name}: bytes -> {{len({input_name}_bytes)}}")'
            )

    if config.get("inputs"):
        for name, details in config["inputs"].items():
            inputs_snippets.append(snip_for_input(name, details.get("type", "")))

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
            with_dot, _ = norm_ext(details.get("type", ""))
            sample_path = f"/work/path/to/your/file{with_dot}" if with_dot else "/work/path/to/your/file"
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

# WARNING: Using a secret locks all future internet access to only that secret's allowed domain(s).
{secrets_code}

{outputs_code}
'''.strip()

    return boilerplate
