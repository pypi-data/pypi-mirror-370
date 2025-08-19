"""
Test initialization actions using pytest.
"""

import os
import subprocess
from pathlib import Path

from rich.console import Console

from pyscaf.actions import Action, CLIOption

console = Console()


class TestAction(Action):
    """Action to initialize a project with pytest testing framework."""

    depends = {"core", "git"}
    run_preferably_after = "git"
    cli_options = [
        CLIOption(
            name="--testing",
            type="bool",
            help="Enable testing with pytest",
            prompt="Do you want to set up testing with pytest?",
            default=False,
        ),
    ]

    def __init__(self, project_path):
        super().__init__(project_path)

    def activate(self, context: dict) -> bool:
        """Activate this action only if testing is enabled."""
        return context.get("testing") is None or context.get("testing", True)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """
        Define the filesystem skeleton for pytest initialization.

        Returns:
            Dictionary mapping paths to content
        """
        # Read pytest documentation
        pytest_doc_path = Path(__file__).parent / "README.md"
        pytest_doc = pytest_doc_path.read_text() if pytest_doc_path.exists() else ""

        # Read test example template
        test_example_path = Path(__file__).parent / "template_test_example.py"
        test_example_template = test_example_path.read_text() if test_example_path.exists() else ""

        # Basic test example
        project_name = context.get("project_name", "myproject")
        curated_project_name = project_name.replace("-", "_")

        # Format the test example with project variables
        test_example = test_example_template.format(
            project_name=project_name, curated_project_name=curated_project_name
        )

        # Ajout conditionnel du .gitignore si git est activé
        skeleton = {
            Path("tests"): None,  # Create tests directory
            Path("tests/__init__.py"): "",  # Empty init file for tests package
            Path(f"tests/test_{curated_project_name}.py"): test_example,
            Path("tests/README.md"): pytest_doc,
        }
        if context.get("versionning"):
            gitignore_path = Path(__file__).parent / "template.gitignore"
            gitignore_content = gitignore_path.read_text() if gitignore_path.exists() else ""
            skeleton[Path(".gitignore")] = gitignore_content
        return skeleton

    def install(self, context: dict) -> None:
        """
        Install test dependencies and run initial test.
        """
        console.print("[bold blue]Installing test dependencies...[/bold blue]")

        try:
            # Ensure we're in the right directory
            os.chdir(self.project_path)

            # Run a quick test to validate setup
            console.print("[bold cyan]Running initial test validation...[/bold cyan]")
            result = subprocess.call(
                ["poetry", "run", "pytest", "--version"],
                stdin=None,
                stdout=None,
                stderr=None,
            )

            if result == 0:
                console.print("[bold green]Pytest setup validated successfully![/bold green]")

                # Run the actual tests
                console.print("[bold cyan]Running initial tests...[/bold cyan]")
                test_result = subprocess.call(
                    ["poetry", "run", "pytest", "tests/", "-v"],
                    stdin=None,
                    stdout=None,
                    stderr=None,
                )

                if test_result == 0:
                    console.print("[bold green]All tests passed![/bold green]")
                else:
                    console.print(f"[bold yellow]Some tests failed (exit code {test_result})[/bold yellow]")
            else:
                console.print(f"[bold yellow]Pytest validation failed (exit code {result})[/bold yellow]")

        except FileNotFoundError:
            console.print("[bold yellow]Poetry not found. Please install it first:[/bold yellow]")
            console.print("https://python-poetry.org/docs/#installation")
