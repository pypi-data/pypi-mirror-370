"""Shared functionality for notebook conversion.

This module provides common functionality used by both HTML and PDF converters.
"""

from typing import Any

from nbconvert import HTMLExporter
from traitlets.config import Config


def create_exporter(
    hide_input: bool = False,
    hide_output: bool = False,
    template_name: str | None = None,
    template_path: str | None = None,
    template_file: str | None = None,
) -> tuple[HTMLExporter, dict[str, Any]]:
    """Create and configure the HTML exporter with preprocessors.

    Args:
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

    Returns:
        Tuple of (exporter, resources)
    """
    # Create configuration
    c = Config()

    # Configure TagRemovePreprocessor
    c.TagRemovePreprocessor.remove_cell_tags = {"remove_cell"}
    c.TagRemovePreprocessor.remove_input_tags = {"hide_input"}
    c.TagRemovePreprocessor.remove_all_outputs_tags = {"hide_output"}
    c.TagRemovePreprocessor.enabled = True

    # Configure HTMLExporter
    c.HTMLExporter.preprocessors = ["nbconvert.preprocessors.TagRemovePreprocessor"]

    # Configure template
    if template_name:
        c.HTMLExporter.template_name = template_name
    elif template_path:
        c.HTMLExporter.template_paths = [template_path]
    elif template_file:
        c.HTMLExporter.template_file = template_file

    # Create exporter with config
    exporter = HTMLExporter(config=c)

    # Set global visibility options
    exporter.exclude_input = hide_input
    exporter.exclude_output = hide_output

    # Create resources dictionary
    resources = {
        "metadata": {},
        "global_content_filter": {
            "include_input": not hide_input,
            "include_output": not hide_output,
        },
    }

    return exporter, resources
