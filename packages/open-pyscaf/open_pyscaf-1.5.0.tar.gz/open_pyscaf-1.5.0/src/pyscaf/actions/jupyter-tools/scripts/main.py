"""Main module for the Jupyter Factory.

This module provides a complete CLI interface for converting Python files to notebooks,
executing them, and converting them to HTML. It can process individual files or entire directories.
"""

import os

import tomli

from .execute_notebook import execute_notebook
from .notebook_to_html import convert_notebook_to_html
from .py_to_notebook import convert_to_notebook


def load_project_config(config_path: str = "./pyproject.toml") -> dict:
    """Load the project configuration from a TOML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file {config_path} not found.")
    with open(config_path, "rb") as f:
        return tomli.load(f)


def py_to_nb_all():
    config = load_project_config()
    src_dir = config["tool"]["pyscaf"]["jupyter-tools"]["python_notebook_dir"]
    dst_dir = config["tool"]["pyscaf"]["jupyter-tools"]["jupyter_notebook_dir"]
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                input_path = os.path.join(root, file)
                rel_path = os.path.relpath(input_path, src_dir)
                output_path = os.path.join(
                    dst_dir, os.path.splitext(rel_path)[0] + ".ipynb"
                )
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                convert_to_notebook(input_path, output_path)
                print(f"Converted {input_path} -> {output_path}")


def exec_nb_all():
    config = load_project_config()
    src_dir = config["tool"]["pyscaf"]["jupyter-tools"]["jupyter_notebook_dir"]
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".ipynb"):
                input_path = os.path.join(root, file)
                execute_notebook(input_path)
                print(f"Executed {input_path}")


def nb_to_html_all():
    config = load_project_config()
    section = config["tool"]["pyscaf"]["jupyter-tools"]
    src_dir = section["jupyter_notebook_dir"]
    html_dir = section["html_dir"]
    hide_input = section.get("hide_input", False)
    hide_output = section.get("hide_output", False)
    template_name = section.get("template_name", "classic")
    template_path = section.get("template_path", "")
    template_file = section.get("template_file", "")
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".ipynb"):
                input_path = os.path.join(root, file)
                rel_path = os.path.relpath(input_path, src_dir)
                output_path = os.path.join(
                    html_dir, os.path.splitext(rel_path)[0] + ".html"
                )
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                convert_notebook_to_html(
                    input_path,
                    output_path,
                    hide_input=hide_input,
                    hide_output=hide_output,
                    template_name=template_name or None,
                    template_path=template_path or None,
                    template_file=template_file or None,
                )
                print(f"Converted {input_path} -> {output_path}")
                print(f"Converted {input_path} -> {output_path}")
