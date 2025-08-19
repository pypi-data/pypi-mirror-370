"""
Git initialization actions.
"""

import os
import re
import subprocess
from pathlib import Path

import questionary
from rich.console import Console

from pyscaf.actions import Action, ChoiceOption, CLIOption

console = Console()

GIT_HOST_CHOICES = [
    ChoiceOption(key="github", display="Github", value="github"),
    ChoiceOption(key="gitlab", display="Gitlab", value="gitlab"),
]


def postfill_remote_url(context: dict) -> dict:
    context["versionning"] = True
    if re.search(r"[^\w]github\.com[^\w]", context["remote_url"]):
        context["git_host"] = "github"
        console.print("[bold cyan]Detected GitHub repository from URL[/bold cyan]")
    elif re.search(r"[^\w]gitlab\.com[^\w]", context["remote_url"]):
        context["git_host"] = "gitlab"
        console.print("[bold cyan]Detected GitLab repository from URL[/bold cyan]")
    return context


def postfill_git_host(context: dict) -> dict:
    context["versionning"] = True
    return context


class GitAction(Action):
    """Action to initialize a Git repository in a project."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--versionning",
            type="bool",
            help="Enable versionning with git",
            prompt="Does this project will be versionned with git ?",
            default=True,
        ),
        CLIOption(
            name="--remote-url",
            type="str",
            help="Provide a remote url for the git repository",
            prompt="Git remote url ?",
            postfill_hook=postfill_remote_url,
        ),
        CLIOption(
            name="--git-host",
            type="choice",
            help="What is the git host for this project ?",
            prompt="Git host ?",
            choices=GIT_HOST_CHOICES,
            default=0,
            postfill_hook=postfill_git_host,
        ),
    ]  # Add Git-specific options if needed

    def __init__(self, project_path):
        super().__init__(project_path)

    def activate(self, context: dict) -> bool:
        return context.get("versionning") is None or context.get("versionning", True)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """
        Define the filesystem skeleton for Git initialization.

        Returns:
            Dictionary mapping paths to content
        """
        # Read Git documentation
        git_doc_path = Path(__file__).parent / "README.md"
        git_doc = git_doc_path.read_text() if git_doc_path.exists() else ""

        # Python & Poetry .gitignore content
        gitignore_path = Path(__file__).parent / "template.gitignore"
        gitignore_content = gitignore_path.read_text() if gitignore_path.exists() else ""

        # Return skeleton dictionary
        return {
            Path(".gitignore"): gitignore_content,
            Path("README.md"): git_doc,  # Add Git documentation to README.md
        }

    def init(self, context: dict) -> None:
        """
        Initialize Git repository after skeleton creation.

        This will initialize a Git repository and optionally add a remote.
        """
        console.print("[bold blue]Initializing Git repository...[/bold blue]")

        try:
            # Change to project directory
            os.chdir(self.project_path)

            # Initialize Git repository
            console.print("[bold cyan]Running git init...[/bold cyan]")

            # Use subprocess.call to run git commands
            result = subprocess.call(
                ["git", "init"],
                stdin=None,
                stdout=None,
                stderr=None,
            )

            if result == 0:
                console.print("[bold green]Git repository initialized successfully![/bold green]")

                # Configure remote repository if URL is provided
                self._configure_remote(context)
            else:
                console.print(f"[bold yellow]Git init exited with code {result}[/bold yellow]")

        except FileNotFoundError:
            console.print("[bold yellow]Git not found. Please install it first.[/bold yellow]")

    def _configure_remote(self, context: dict) -> None:
        """Configure remote repository."""
        # Use remote URL from config if provided
        remote_url = context.get("remote_url")

        if not remote_url and context.get("interactive"):
            # Ask for remote URL in interactive mode
            remote_url = questionary.text(
                "Enter remote URL for Git repository (leave empty to configure later):",
                default="",
            ).ask()

        if remote_url:
            # Add remote
            result = subprocess.call(
                ["git", "remote", "add", "origin", remote_url],
                stdin=None,
                stdout=None,
                stderr=None,
            )

            if result == 0:
                console.print(f"[bold green]Remote repository configured: {remote_url}[/bold green]")
        else:
            console.print("[bold blue]No remote URL provided. You can add it later with:[/bold blue]")
            console.print("  git remote add origin <your-repository-url>")

    def install(self, context: dict) -> None:
        """
        No additional installation steps needed for Git.
        """
        console.print("[bold blue]Setting up Git for the project...[/bold blue]")
        # Add files to repository
        subprocess.call(
            ["git", "add", "."],
            stdin=None,
            stdout=None,
            stderr=None,
        )

        # Initial commit
        subprocess.call(
            ["git", "commit", "-m", "feat: Initial commit"],
            stdin=None,
            stdout=None,
            stderr=None,
        )
