"""Module for executing Jupyter notebooks.

This module provides functionality to execute Jupyter notebooks in-place,
handling cell execution and error management.
"""

import subprocess
import argparse
import os


def execute_notebook(notebook_path: str) -> None:
    """Execute a notebook and save the results.

    Args:
        notebook_path: Path to the notebook file to execute

    Raises:
        subprocess.CalledProcessError: If notebook execution fails
    """
    try:
        subprocess.run(
            [
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--inplace",
                notebook_path,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error executing notebook: {e}")
        raise


def main():
    """CLI entry point for executing notebooks."""
    parser = argparse.ArgumentParser(description="Execute a Jupyter notebook in-place")
    parser.add_argument("notebook", help="Path to the notebook file to execute")

    args = parser.parse_args()

    if not os.path.exists(args.notebook):
        print(f"Error: Notebook file {args.notebook} does not exist")
        return

    try:
        execute_notebook(args.notebook)
        print(f"Successfully executed notebook: {args.notebook}")
    except subprocess.CalledProcessError:
        print(f"Failed to execute notebook: {args.notebook}")


if __name__ == "__main__":
    main()
