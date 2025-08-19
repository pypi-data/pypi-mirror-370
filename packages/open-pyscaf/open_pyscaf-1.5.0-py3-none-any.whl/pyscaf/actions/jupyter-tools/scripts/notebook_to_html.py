"""Module for converting Jupyter notebooks to HTML.

This module provides functionality to convert Jupyter notebooks to HTML format,
handling markdown links, notebook metadata, and cell tags.

Supported cell tags:
- remove_cell: Completely removes the cell from the output
- hide_input: Hides the input (code) but shows the output
- hide_output: Hides the output but shows the input

Template configuration:
- template_name: Name of the built-in template (see list below)
- template_path: Path to a custom template directory
- template_file: Path to a specific template file

Available built-in templates:
- classic: The classic Jupyter notebook template
- lab: JupyterLab-like template
- basic: A minimal template
- reveal: For presentations (requires reveal.js)
- full: Full template with all features
- custom: Custom template (requires template_path or template_file)

Creating custom templates:
1. Copy an existing template from nbconvert/templates/html/
2. Modify the template to your needs
3. Use --template-path or --template-file to use your custom template

Template documentation:
- Official nbconvert templates: https://nbconvert.readthedocs.io/en/latest/customizing.html#templates
- Jinja2 template engine: https://jinja.palletsprojects.com/
- Custom template example: https://github.com/jupyter/nbconvert-examples/tree/main/custom_templates
"""

import argparse
import os

import nbformat

from .shared.exporter import create_exporter


def process_cell_tags(cell: nbformat.NotebookNode) -> None:
    """Process cell tags to determine visibility and execution.

    Args:
        cell: Notebook cell to process
    """
    if not hasattr(cell, "metadata"):
        cell.metadata = {}

    if "tags" not in cell.metadata:
        cell.metadata["tags"] = []


def convert_notebook_to_html(
    notebook_path: str,
    output_path: str,
    hide_input: bool = False,
    hide_output: bool = False,
    template_name: str | None = None,
    template_path: str | None = None,
    template_file: str | None = None,
) -> None:
    """Convert a .ipynb notebook to an HTML file.

    Args:
        notebook_path: Path to the input notebook file
        output_path: Path to the output HTML file
        hide_input: Whether to hide all input cells by default
        hide_output: Whether to hide all output cells by default
        template_name: Name of the built-in template to use. Available options:
            - classic: The classic Jupyter notebook template
            - lab: JupyterLab-like template
            - basic: A minimal template
            - reveal: For presentations (requires reveal.js)
            - full: Full template with all features
            - custom: Custom template (requires template_path or template_file)
        template_path: Path to a custom template directory
        template_file: Path to a specific template file
    """
    print(f"Converting notebook {notebook_path} to HTML...")
    print("DEBUG: template_name", template_name)
    # Read the notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Process all cells
    for cell in nb.cells:
        # Process cell tags
        process_cell_tags(cell)

        # Handle markdown links
        if cell.cell_type == "markdown":
            cell.source = cell.source.replace(".ipynb)", ".html)")

    # Create and configure exporter
    exporter, resources = create_exporter(
        hide_input=hide_input,
        hide_output=hide_output,
        template_name=template_name,
        template_path=template_path,
        template_file=template_file,
    )

    # Convert notebook
    output, _ = exporter.from_notebook_node(nb, resources=resources)

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)


def main():
    """CLI entry point for converting notebooks to HTML."""
    parser = argparse.ArgumentParser(description="Convert Jupyter notebooks to HTML")
    parser.add_argument("input", help="Path to the input notebook file")
    parser.add_argument("output", help="Path to the output HTML file")
    parser.add_argument(
        "--hide-input", action="store_true", help="Hide all input cells by default"
    )
    parser.add_argument(
        "--hide-output", action="store_true", help="Hide all output cells by default"
    )
    parser.add_argument(
        "--template",
        help="Name of the built-in template to use. Available options: classic, lab, basic, reveal, full, custom",
    )
    parser.add_argument("--template-path", help="Path to a custom template directory")
    parser.add_argument("--template-file", help="Path to a specific template file")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Notebook file {args.input} does not exist")
        return

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    try:
        convert_notebook_to_html(
            args.input,
            args.output,
            args.hide_input,
            args.hide_output,
            args.template,
            args.template_path,
            args.template_file,
        )
        print(f"Successfully converted {args.input} to {args.output}")
    except Exception as e:
        print(f"Error converting notebook to HTML: {e}")


if __name__ == "__main__":
    main()
    main()
