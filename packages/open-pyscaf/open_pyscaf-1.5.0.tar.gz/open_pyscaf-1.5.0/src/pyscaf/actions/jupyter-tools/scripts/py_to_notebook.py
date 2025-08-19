"""Module for converting Python files to Jupyter notebooks.

This module provides functionality to convert Python files to Jupyter notebooks,
handling cell markers, tags, and markdown links.
"""

import argparse
import os

import jupytext
import nbformat


def convert_to_notebook(input_path: str, output_path: str) -> None:
    """Convert a .py file to a .ipynb notebook.

    Args:
        input_path: Path to the input Python file
        output_path: Path to the output notebook file

    Note:
        Tags can be added to any cell using the syntax:
        # %% [markdown] tags=["tag1", "tag2"]  # for markdown cells
        # %% tags=["tag1", "tag2"]            # for code cells
    """
    # Read the notebook with jupytext
    nb = jupytext.read(input_path)

    # Convert all cells and handle their metadata
    for cell in nb.cells:
        # Ensure metadata exists
        if not hasattr(cell, "metadata"):
            cell.metadata = {}

        # Initialize tags if they don't exist
        if "tags" not in cell.metadata:
            cell.metadata["tags"] = []

        # Handle cell markers and their tags
        source_lines = cell.source.split("\n")
        for i, line in enumerate(source_lines):
            # Check for cell markers with tags
            if line.startswith("# %%"):
                # Extract tags if present
                if "tags=[" in line:
                    tags_start = line.find("tags=[")
                    tags_end = line.find("]", tags_start)
                    if tags_end != -1:
                        tags_str = line[tags_start + 6 : tags_end]
                        # Parse the tags (handling both "tag" and tag formats)
                        tags = [t.strip().strip("\"'") for t in tags_str.split(",")]
                        cell.metadata["tags"].extend(tags)

        # Handle markdown links
        if cell.cell_type == "markdown":
            cell.source = cell.source.replace(".py)", ".ipynb)")

    # Write the notebook
    with open(output_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)


def main():
    """CLI entry point for converting Python files to notebooks."""
    parser = argparse.ArgumentParser(
        description="Convert Python files to Jupyter notebooks"
    )
    parser.add_argument("input", help="Path to the input Python file")
    parser.add_argument("output", help="Path to the output notebook file")

    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    convert_to_notebook(args.input, args.output)
    print(f"Successfully converted {args.input} to {args.output}")


def main_all():
    """CLI entry point to convert all .py files in notebooks/ to .ipynb notebooks in ./build."""
    import glob

    notebooks_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "notebooks"
    )
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "build")
    os.makedirs(output_dir, exist_ok=True)
    py_files = glob.glob(os.path.join(notebooks_dir, "*.py"))
    if not py_files:
        print("No .py files found in notebooks directory.")
        return
    for py_file in py_files:
        base_name = os.path.basename(py_file)[:-3]
        ipynb_file = os.path.join(output_dir, base_name + ".ipynb")
        convert_to_notebook(py_file, ipynb_file)
        print(f"Converted {py_file} -> {ipynb_file}")


if __name__ == "__main__":
    main()
