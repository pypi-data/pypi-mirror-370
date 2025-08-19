"""
Command-line interface for pyscaf.
"""

import sys
from typing import Any, Type

import click
from rich.console import Console

from pyscaf import __version__
from pyscaf.actions import Action, discover_actions
from pyscaf.actions.cli_option_to_key import cli_option_to_key
from pyscaf.actions.manager import ActionManager
from pyscaf.preference_chain import best_execution_order
from pyscaf.preference_chain.model import Node

console = Console()


def print_version(ctx, param, value):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    console.print(f"pyscaf version {__version__}")
    ctx.exit()


def collect_cli_options():
    action_classes = discover_actions()
    deps = []
    action_class_by_id: dict[str, Type[Action]] = {}
    for action_cls in action_classes:
        action_id = action_cls.__name__.replace("Action", "").lower()
        depends = getattr(action_cls, "depends", set())
        after = getattr(action_cls, "run_preferably_after", None)

        # If there are dependencies but no 'after' is specified, use the first dependency
        if depends and after is None:
            after = next(iter(depends))

        # Create Node object
        node = Node(id=action_id, depends=depends, after=after)
        deps.append(node)
        action_class_by_id[action_id] = action_cls
    order = best_execution_order(deps)
    cli_options = []
    for action_id in order:
        action_cls = action_class_by_id[action_id]
        cli_options.extend(getattr(action_cls, "cli_options", []))
    return cli_options


def set_option_default(opt) -> Any:
    """
    Get the default value for a CLI option.

    Args:
        opt: The CLI option to get default value for

    Returns:
        The default value for the option
    """
    if opt.type == "choice":
        # For choices, get the default key, not the default value
        default_index = opt.default
        if default_index is not None and opt.choices:
            default_value = opt.choices[default_index].key
        else:
            default_value = None
        print(f"default_key: {default_value}")
    else:
        default_value = opt.default() if callable(opt.default) else opt.default
    return default_value


def fill_default_context(context: dict) -> dict:
    """
    Fill the context with default values from all actions.

    This function discovers all actions and fills the context with their default values
    for options that are not already set in the context.

    Args:
        context: The current context dictionary

    Returns:
        Updated context with default values filled in
    """
    action_classes = discover_actions()

    for action_cls in action_classes:
        if hasattr(action_cls, "cli_options"):
            for opt in action_cls.cli_options:
                # Convert option name to context key
                name = cli_option_to_key(opt)

                # Only set default if not already present in context
                if name not in context or context[name] is None:
                    context[name] = set_option_default(opt)

    return context


def add_dynamic_options(command):
    cli_options = collect_cli_options()
    for opt in reversed(cli_options):
        param_decls = [opt.name]
        click_opts = {}
        # Type
        if opt.type == "int":
            click_opts["type"] = int
        elif opt.type == "choice" and opt.choices:
            # Use choice keys for CLI
            choice_keys = opt.get_choice_keys()
            click_opts["type"] = click.Choice(choice_keys, case_sensitive=False)
            if opt.multiple:
                click_opts["multiple"] = True
        elif opt.type == "str":
            click_opts["type"] = str
        elif opt.type == "bool":
            click_opts["type"] = click.BOOL
            click_opts["default"] = None
            # Use Click's built-in --option/--no-option syntax for boolean flags
            base_name = opt.name.lstrip("-")
            param_decls[0] = f"--{base_name}/--no-{base_name}"

        # Help
        if opt.help:
            click_opts["help"] = opt.help
        # Default
        # Required
        if opt.required:
            click_opts["required"] = True
        command = click.option(*param_decls, **click_opts)(command)
    return command


@click.group()
@click.version_option(
    __version__,
    "--version",
    "-V",
    callback=print_version,
    help="Show the version and exit.",
)
def cli():
    """🧪 pyscaf - Project generator for laboratory, teaching and data analysis."""
    pass


@cli.command()
@add_dynamic_options
@click.argument("project_name")
@click.option(
    "--interactive",
    is_flag=True,
    help="Enable interactive mode (asks questions to the user).",
)
@click.option("--no-install", is_flag=True, help="Skip installation step.")
def init(project_name, interactive, no_install, **kwargs):
    """
    Initialize a new customized project structure.
    """
    context = dict(kwargs)
    context["project_name"] = project_name
    context["interactive"] = interactive
    context["no_install"] = no_install

    if not interactive:
        context = fill_default_context(context)

    manager = ActionManager(project_name, context)
    context = manager.run_postfill_hooks(context)

    if interactive:
        context = manager.ask_interactive_questions(context)
    manager.create_project()


def main():
    """Entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
