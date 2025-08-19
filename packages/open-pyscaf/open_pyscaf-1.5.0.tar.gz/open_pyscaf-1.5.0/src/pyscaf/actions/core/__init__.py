"""
Poetry initialization actions.
"""

import os
import subprocess
from pathlib import Path

import tomli
import tomli_w
from rich.console import Console

from pyscaf.actions import Action, CLIOption

console = Console()


def get_local_git_author():
    """Get the author name from the local git config."""
    try:
        git_name = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
        git_email = subprocess.check_output(["git", "config", "user.email"]).decode().strip()
        default_author = f"{git_name} <{git_email}>"
    except subprocess.CalledProcessError:
        default_author = ""
    return default_author


class CoreAction(Action):
    """Action to initialize a project with Poetry."""

    depends = set()  # Poetry is the root action
    run_preferably_after = None
    cli_options = [
        CLIOption(
            name="--author",
            type="str",
            help="Author name",
            prompt="Who is the main author of this project ?",
            default=get_local_git_author,
        ),
    ]

    def __init__(self, project_path):
        super().__init__(project_path)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """
        Define the filesystem skeleton for Core initialization.

        Returns:
            Dictionary mapping paths to content
        """
        project_name = context.get("project_name", "myproject")
        currated_projet_name = project_name.replace("-", "_")

        # Read Poetry documentation
        poetry_doc_path = Path(__file__).parent / "README.md"
        poetry_doc = poetry_doc_path.read_text() if poetry_doc_path.exists() else ""

        # Add default ruff settings for VSCode
        vscode_settings_path = Path(__file__).parent / "default_settings.json"
        vscode_settings = vscode_settings_path.read_text() if vscode_settings_path.exists() else ""
        # Return skeleton dictionary
        skeleton = {
            Path("README.md"): (f"# {project_name}\n\nA Python project created with pyscaf\n\n{poetry_doc}\n"),
            Path(f"src/{currated_projet_name}/__init__.py"): (
                f'"""\n{project_name} package.\n"""\n\n__version__ = "0.0.0"\n'
            ),
            Path(".vscode/settings.json"): vscode_settings if vscode_settings else None,
        }
        return skeleton

    def init(self, context: dict) -> None:
        """
        Initialize Core after skeleton creation.

        This will run 'poetry init' in non-interactive mode.
        """
        console.print("[bold blue]Initializing core project...[/bold blue]")

        try:
            # Change to project directory
            os.chdir(self.project_path)

            # Use subprocess.call to pass control to the terminal
            result = subprocess.call(
                [
                    "poetry",
                    "init",
                    "--no-interaction",
                    "--author",
                    context.get("author", ""),
                ],
                # No redirection,
                # allows full terminal interaction
                stdin=None,
                stdout=None,
                stderr=None,
            )

            project_name = context.get("project_name", "myproject")
            currated_projet_name = project_name.replace("-", "_")

            # Ajout dynamique de la clé packages dans [tool.poetry] du pyproject.toml
            pyproject_path = Path("pyproject.toml")
            if pyproject_path.exists():
                with pyproject_path.open("rb") as f:
                    pyproject_data = tomli.load(f)
                try:
                    # Ensure tool.poetry.group.dev exists
                    if "tool" not in pyproject_data:
                        pyproject_data["tool"] = {}
                    if "poetry" not in pyproject_data["tool"]:
                        pyproject_data["tool"]["poetry"] = {}
                    pyproject_data["tool"]["poetry"]["packages"] = [{"include": currated_projet_name, "from": "src"}]
                    with pyproject_path.open("wb") as f:
                        f.write(tomli_w.dumps(pyproject_data).encode("utf-8"))
                    console.print(
                        f"[bold green]Added [tool.poetry].packages for {currated_projet_name} in pyproject.toml[/bold green]"
                    )
                except Exception as e:
                    console.print(f"[bold yellow]Section [tool.poetry] not found or error: {e}[/bold yellow]")
            else:
                console.print("[bold yellow]pyproject.toml not found after poetry init.[/bold yellow]")

            if result == 0:
                console.print("[bold green]Poetry initialization successful![/bold green]")
            else:
                console.print(f"[bold yellow]Poetry init exited with code {result}[/bold yellow]")

        except FileNotFoundError:
            console.print("[bold yellow]Poetry not found. Please install it first:[/bold yellow]")
            console.print("https://python-poetry.org/docs/#installation")

    def install(self, context: dict) -> None:
        """
        Install dependencies with Poetry.

        This will run 'poetry install' to install all dependencies.
        """
        super().init(context)

        console.print("[bold blue]Installing dependencies with Poetry...[/bold blue]")
        try:
            # Ensure we're in the right directory
            os.chdir(self.project_path)

            # Run poetry install
            console.print("[bold cyan]Running poetry install...[/bold cyan]")
            result = subprocess.call(["poetry", "install"], stdin=None, stdout=None, stderr=None)

            if result == 0:
                console.print("[bold green]Poetry dependencies installed successfully![/bold green]")
            else:
                console.print(f"[bold yellow]Poetry install exited with code {result}[/bold yellow]")

        except FileNotFoundError:
            console.print("[bold yellow]Poetry not found. Please install it first:[/bold yellow]")
            console.print("https://python-poetry.org/docs/#installation")
            return

        # Separate block for VSCode Ruff extension installation
        try:
            console.print("[bold cyan]Installing VSCode Ruff extension...[/bold cyan]")
            subprocess.call(["code", "--install-extension", "charliermarsh.ruff", "--force"])
        except FileNotFoundError:
            console.print("[bold yellow]VSCode not found. Please install it first:[/bold yellow]")
            console.print("https://code.visualstudio.com/download")
