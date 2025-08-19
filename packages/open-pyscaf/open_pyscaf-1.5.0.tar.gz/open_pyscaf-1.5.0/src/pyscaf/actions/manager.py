"""
Project action manager module.
"""

import logging
from pathlib import Path
from typing import Any

import questionary
from rich.console import Console

from pyscaf.actions import Action, discover_actions
from pyscaf.actions.cli_option_to_key import cli_option_to_key
from pyscaf.preference_chain import (
    CircularDependencyError,
    build_chains,
    compute_all_resolution_pathes,
    compute_path_score,
    extend_nodes,
)
from pyscaf.preference_chain.model import Node

console = Console()
logger = logging.getLogger(__name__)


class ActionManager:
    """Manager for all project actions."""

    def __init__(self, project_name: str | Path, context: dict[str, Any]):
        """
        Initialize the action manager.

        Args:
            project_name: Name of the project to create
            context: Project context
        """
        self.project_path = Path.cwd() / project_name
        console.print(f"[bold green]Project path: [/bold green]{self.project_path}")
        self.context = context
        self.actions: list[Action] = []

        # Determine which actions to include based on configuration
        self._determine_actions()

    def _determine_actions(self) -> None:
        """Determine which actions to include based on configuration using the new preference chain logic."""
        # Discover all available Action classes
        action_classes = discover_actions()

        # Build Node objects for the new preference chain logic
        nodes = []
        action_class_by_id = {}

        for action_cls in action_classes:
            action_id = action_cls.__name__.replace("Action", "").lower()
            depends = getattr(action_cls, "depends", set())
            after = getattr(action_cls, "run_preferably_after", None)

            # Create Node object
            node = Node(id=action_id, depends=depends, after=after)
            nodes.append(node)
            action_class_by_id[action_id] = action_cls

        logger.debug(f"Created {len(nodes)} action nodes")

        # Use the new preference chain logic to determine optimal execution order
        extended_dependencies = extend_nodes(nodes)
        clusters = build_chains(extended_dependencies)

        logger.debug(f"Built {len(clusters)} chains from actions")

        # Compute all possible resolution paths
        all_resolution_paths = list(compute_all_resolution_pathes(clusters))

        if not all_resolution_paths:
            # No valid resolution path found - this indicates a serious dependency issue
            action_ids = [node.id for node in nodes]
            error_msg = (
                f"No valid resolution path found for actions: {action_ids}. "
                "This indicates circular dependencies or unsatisfiable constraints between actions."
            )
            logger.error(error_msg)
            raise CircularDependencyError(error_msg)

        logger.debug(f"Found {len(all_resolution_paths)} resolution paths for actions")

        # Sort paths by score (best score first)
        all_resolution_paths.sort(key=lambda path: -compute_path_score(list(path)))

        # Extract the final execution order from the best path
        best_path = all_resolution_paths[0]
        order = [action_id for chain in best_path for action_id in chain.ids]

        logger.debug(f"Final action execution order: {order}")

        # Instantiate actions in the optimal order
        self.actions = [
            action_class_by_id[action_id](self.project_path) for action_id in order if action_id in action_class_by_id
        ]

    def run_postfill_hooks(self, context: dict) -> dict:
        """Run all postfill hooks for actions in optimal order."""
        for action in self.actions:
            if action.activate(context):
                for opt in action.cli_options:
                    context_key = cli_option_to_key(opt)
                    if context.get(context_key) is None:
                        continue
                    if opt.postfill_hook:
                        context = opt.postfill_hook(context)
        return context

    def ask_interactive_questions(self, context: dict) -> dict:
        """
        Ask all relevant questions for actions in optimal order, updating the context.
        Only asks if action.activate(context) is True.
        Skips questions for which a value is already present in the context (e.g. provided via CLI).
        """
        for action in self.actions:
            if action.activate(context):
                for opt in action.cli_options:
                    context_key = cli_option_to_key(opt)
                    if context.get(context_key) is not None:
                        continue
                    prompt = opt.prompt or context_key
                    if opt.type == "choice":
                        default = opt.get_default_value()
                    else:
                        default = opt.default() if callable(opt.default) else opt.default
                    if opt.type == "bool":
                        answer = questionary.confirm(prompt, default=bool(default)).ask()
                    elif opt.type == "int":
                        answer = questionary.text(prompt, default=str(default) if default is not None else "").ask()
                        answer = int(answer) if answer is not None and answer != "" else None
                    elif opt.type == "choice" and opt.choices:
                        choices = opt.get_choice_displays()
                        default_display = opt.get_default_display()

                        if opt.multiple:
                            # Use checkbox for multiple choice
                            answer = questionary.checkbox(prompt, choices=choices, default=default_display).ask()
                        else:
                            # Use select for single choice
                            answer = questionary.select(prompt, choices=choices, default=default_display).ask()

                        # Convert displays back to keys (we always store keys)
                        if answer:
                            if opt.multiple:
                                # Handle multiple choices
                                converted_answer = []
                                for display in answer:
                                    for choice in opt.choices:
                                        if choice.display == display:
                                            converted_answer.append(choice.key)
                                            break
                                answer = converted_answer
                            else:
                                # Handle single choice
                                for choice in opt.choices:
                                    if choice.display == answer:
                                        answer = choice.key
                                        break

                    else:  # str or fallback
                        answer = questionary.text(prompt, default=default if default is not None else "").ask()
                    context[context_key] = answer
                    if opt.postfill_hook:
                        context = opt.postfill_hook(context)
        return context

    def create_project(self) -> None:
        """Create the project structure and initialize it."""
        # Create project directory if it doesn't exist
        self.project_path.mkdir(parents=True, exist_ok=True)

        console.print(f"[bold green]Creating project at: [/bold green]{self.project_path}")

        # First pass: Create all skeletons
        for action in self.actions:
            if not action.activate(self.context):
                print(f"Skipping {action.__class__.__name__}")
                continue
            action_name = action.__class__.__name__
            console.print(f"[bold blue]Creating skeleton for: [/bold blue]{action_name}")
            action.create_skeleton(self.context)

        # Second pass: Initialize all actions
        for action in self.actions:
            if not action.activate(self.context):
                continue
            action_name = action.__class__.__name__
            console.print(f"[bold blue]Initializing: [/bold blue]{action_name}")
            action.init(self.context)

        # Third pass: Install dependencies if not skipped
        if not self.context.get("no_install", False):
            for action in self.actions:
                if not action.activate(self.context):
                    continue
                action_name = action.__class__.__name__
                console.print(f"[bold blue]Installing dependencies for: [/bold blue]{action_name}")
                action.install(self.context)
        else:
            console.print("[bold yellow]Skipping installation.[/bold yellow]")

        console.print("[bold green]Project creation complete![/bold green]")
