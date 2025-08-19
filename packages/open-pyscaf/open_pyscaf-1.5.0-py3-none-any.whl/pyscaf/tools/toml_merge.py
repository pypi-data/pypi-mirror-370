from pathlib import Path

import tomlkit


def merge_toml_files(input_path: Path, output_path: Path):
    """
    Merges all content from input_path TOML file into output_path TOML file.
    Recursively merges sections and avoids duplicates by intelligently combining content.
    Preserves and merges comments at the correct location (inline, under section, etc.).
    """
    # Read files as TOML documents (preserving comments)
    input_doc = (
        tomlkit.parse(input_path.read_text(encoding="utf-8"))
        if input_path.exists()
        else tomlkit.document()
    )
    output_doc = (
        tomlkit.parse(output_path.read_text(encoding="utf-8"))
        if output_path.exists()
        else tomlkit.document()
    )

    def deep_merge(source, dest):
        """
        Recursively merge source into dest, preserving comments and structure.
        """
        for key in source:
            if key in dest:
                if isinstance(source[key], dict) and isinstance(dest[key], dict):
                    # Both are tables, merge recursively
                    deep_merge(source[key], dest[key])
                elif isinstance(source[key], list) and isinstance(dest[key], list):
                    # Both are arrays, extend with unique items
                    for item in source[key]:
                        if item not in dest[key]:
                            dest[key].append(item)
                else:
                    # Overwrite value, preserve inline comment if present
                    dest[key] = source[key]
            else:
                # New key: insert with its comments
                dest[key] = source[key]
                # tomlkit preserves comments automatically for new keys

    deep_merge(input_doc, output_doc)

    # Write output, preserving comments
    output_path.write_text(tomlkit.dumps(output_doc), encoding="utf-8")
