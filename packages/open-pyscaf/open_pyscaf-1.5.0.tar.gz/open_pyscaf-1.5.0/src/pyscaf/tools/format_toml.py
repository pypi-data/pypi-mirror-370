from pathlib import Path


def format_toml(path: Path):
    """
    Ensures there is exactly one empty line between each section in the TOML file.
    The formatted content is written back to the same file.
    """
    # Read the file content
    lines = path.read_text(encoding="utf-8").splitlines()
    formatted_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Detect section header
        if stripped.startswith("[") and stripped.endswith("]"):
            # Remove trailing empty lines before section
            while formatted_lines and formatted_lines[-1] == "":
                formatted_lines.pop()
            # Add exactly one empty line before section (except for the first section)
            if formatted_lines:
                formatted_lines.append("")
            formatted_lines.append(line)
        else:
            formatted_lines.append(line)

    # Write the formatted content back to the file
    path.write_text("\n".join(formatted_lines) + "\n", encoding="utf-8")
