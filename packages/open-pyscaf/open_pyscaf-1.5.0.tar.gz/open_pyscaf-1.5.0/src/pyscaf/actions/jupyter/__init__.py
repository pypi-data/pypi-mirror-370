"""
Jupyter initialization actions.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional

import tomli
import tomli_w
from rich.console import Console

from pyscaf.actions import Action, CLIOption

console = Console()


class JupyterAction(Action):
    """Action to initialize Jupyter notebook support in a project."""

    depends = {"core", "git"}
    run_preferably_after = "git"
    cli_options = [
        CLIOption(
            name="--jupyter",
            type="bool",
            help="Handle Jupyter notebook support",
            prompt="Does this project will use Jupyter notebook ?",
            default=False,
        ),
    ]  # Add Jupyter-specific options if needed

    def __init__(self, project_path):
        super().__init__(project_path)

    def activate(self, context: dict) -> bool:
        return context.get("jupyter") is None or context.get("jupyter", True)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """
        Define the filesystem skeleton for Jupyter notebook support.

        Returns:
            Dictionary mapping paths to content
        """
        project_name = context.get("project_name", "myproject")

        # Read Jupyter documentation
        jupyter_doc_path = Path(__file__).parent / "README.md"
        jupyter_doc = jupyter_doc_path.read_text() if jupyter_doc_path.exists() else ""

        # Create a README for notebooks
        notebook_readme = f"""# {project_name} - Notebooks

This directory contains Jupyter notebooks for the {project_name} project.

{jupyter_doc}
"""

        # Ajout conditionnel du .gitignore si git est activé
        skeleton = {
            Path("notebooks"): None,  # Create main notebook directory
            Path("notebooks/README.md"): notebook_readme,
        }
        if context.get("versionning"):
            gitignore_path = Path(__file__).parent / "template.gitignore"
            gitignore_content = gitignore_path.read_text() if gitignore_path.exists() else ""
            skeleton[Path(".gitignore")] = gitignore_content
        return skeleton

    def install(self, context: dict) -> None:
        """
        Set up the Jupyter kernel for the project.

        This will create a Jupyter kernel specific to this project.
        """
        console.print("[bold blue]Setting up Jupyter kernel for the project...[/bold blue]")

        try:
            # Ensure we're in the right directory
            os.chdir(self.project_path)

            # Create a Jupyter kernel for this project
            console.print("[bold cyan]Creating Jupyter kernel for this project...[/bold cyan]")

            project_name = context.get("project_name", "myproject")

            # Run the ipykernel installation via poetry
            result = subprocess.call(
                [
                    "poetry",
                    "run",
                    "python",
                    "-m",
                    "ipykernel",
                    "install",
                    "--user",
                    "--name",
                    project_name,
                    "--display-name",
                    f"{project_name} (Poetry)",
                ],
                stdin=None,
                stdout=None,
                stderr=None,
            )

            if result == 0:
                console.print("[bold green]Jupyter kernel created successfully![/bold green]")
                console.print(
                    f"[bold green]You can now use the '{project_name} (Poetry)' kernel in Jupyter.[/bold green]"
                )
            else:
                console.print(f"[bold yellow]Jupyter kernel creation exited with code {result}[/bold yellow]")

        except FileNotFoundError:
            console.print("[bold yellow]Poetry or Jupyter not found. Make sure they are installed.[/bold yellow]")
            console.print("https://python-poetry.org/docs/#installation")
