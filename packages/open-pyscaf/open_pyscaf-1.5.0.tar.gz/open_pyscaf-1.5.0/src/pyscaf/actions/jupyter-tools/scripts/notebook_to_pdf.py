#!/usr/bin/env python3
"""Convert Jupyter notebooks to PDF files.

This script converts Jupyter notebooks to PDF files by first converting to HTML,
and then using wkhtmltopdf to generate the PDF.

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
"""

import argparse
import subprocess
from pathlib import Path
from typing import Any

from nbconvert.preprocessors import ExecutePreprocessor
from nbformat import read as nb_read

from .shared.exporter import create_exporter


def process_cell_tags(cell: Any) -> None:
    """Process cell tags to determine visibility and execution.

    Args:
        cell: Notebook cell to process
    """
    if not hasattr(cell, "metadata"):
        cell.metadata = {}

    if "tags" not in cell.metadata:
        cell.metadata["tags"] = []


def convert_notebook_to_pdf(
    notebook_path: str | Path,
    output_path: str | Path,
    hide_input: bool = False,
    hide_output: bool = False,
    template_name: str | None = None,
    template_path: str | None = None,
    template_file: str | None = None,
    timeout: int = 600,
) -> None:
    """Convert a Jupyter notebook to PDF.

    Args:
        notebook_path: Path to the input notebook
        output_path: Path to the output PDF file
        hide_input: Whether to hide all input cells by default
        hide_output: Whether to hide all output cells by default
        template_name: Name of the built-in template to use
        template_path: Path to a custom template directory
        template_file: Path to a specific template file
        timeout: Timeout in seconds for notebook execution

    Raises:
        FileNotFoundError: If the input notebook doesn't exist
        subprocess.CalledProcessError: If wkhtmltopdf conversion fails
    """
    notebook_path = Path(notebook_path)
    output_path = Path(output_path)

    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook not found: {notebook_path}")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read the notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nb_read(f, as_version=4)

    # Process all cells
    for cell in nb.cells:
        process_cell_tags(cell)
        if cell.cell_type == "markdown":
            cell.source = cell.source.replace(".ipynb)", ".pdf)")

    # Execute the notebook
    ep = ExecutePreprocessor(timeout=timeout)
    ep.preprocess(nb, {"metadata": {"path": str(notebook_path.parent)}})

    # Create and configure exporter
    exporter, resources = create_exporter(
        hide_input=hide_input,
        hide_output=hide_output,
        template_name=template_name,
        template_path=template_path,
        template_file=template_file,
    )

    # Convert to HTML
    (body, _) = exporter.from_notebook_node(nb, resources=resources)

    # Save HTML
    html_path = output_path.parent / f"{notebook_path.stem}.pdf.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(body)

    # Convert HTML to PDF using wkhtmltopdf
    subprocess.run(
        [
            "wkhtmltopdf",
            str(html_path),
            str(output_path),
        ],
        check=True,
    )

    # Clean up temporary files
    html_path.unlink()


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Convert Jupyter notebooks to PDF")
    parser.add_argument("input", help="Path to the input notebook file")
    parser.add_argument("output", help="Path to the output PDF file")
    parser.add_argument(
        "--hide-input", action="store_true", help="Hide all input cells by default"
    )
    parser.add_argument(
        "--hide-output", action="store_true", help="Hide all output cells by default"
    )
    parser.add_argument("--template", help="Name of the built-in template to use")
    parser.add_argument("--template-path", help="Path to a custom template directory")
    parser.add_argument("--template-file", help="Path to a specific template file")
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds for notebook execution",
    )

    args = parser.parse_args()

    try:
        convert_notebook_to_pdf(
            args.input,
            args.output,
            args.hide_input,
            args.hide_output,
            args.template,
            args.template_path,
            args.template_file,
            args.timeout,
        )
        print(f"Successfully converted {args.input} to {args.output}")
    except Exception as e:
        print(f"Error converting notebook to PDF: {e}")
        exit(1)


if __name__ == "__main__":
    main()
    main()
