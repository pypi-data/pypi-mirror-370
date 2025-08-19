from pathlib import Path

from pyscaf.actions import Action, ChoiceOption, CLIOption

LICENSE_CHOICES = [
    ChoiceOption(
        key="mit",
        display="MIT (permissive, suitable for most open source projects)",
        value="template_MIT.txt",
    ),
    ChoiceOption(
        key="apache",
        display="Apache-2.0 (permissive, protects against patent claims, recommended for companies)",
        value="template_Apache-2.0.txt",
    ),
    ChoiceOption(
        key="gpl",
        display="GPL-3.0 (copyleft, requires sharing source code of derivatives)",
        value="template_GPL-3.0.txt",
    ),
    ChoiceOption(
        key="bsd",
        display="BSD-3-Clause (permissive, good for academic or enterprise projects)",
        value="template_BSD-3-Clause.txt",
    ),
    ChoiceOption(
        key="mpl",
        display="Mozilla (MPL-2.0, weak copyleft, for libraries or modules)",
        value="template_MPL-2.0.txt",
    ),
    ChoiceOption(
        key="unlicense",
        display="Unlicense (public domain, no restrictions)",
        value="template_Unlicense.txt",
    ),
]


class LicenseAction(Action):
    """Action to add a LICENSE file to the project."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--license",
            type="choice",
            help="Choose a license for your project",
            prompt="Which license do you want to use?",
            choices=LICENSE_CHOICES,
            default=0,  # Index of the default choice
        ),
    ]

    def __init__(self, project_path):
        super().__init__(project_path)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        license_key = context.get("license", "mit")  # Get the key (e.g., "mit")

        # Convert key to value using LICENSE_CHOICES directly
        license_choice = None
        for choice in LICENSE_CHOICES:
            if choice.key == license_key:
                license_choice = choice.value
                break

        skeleton = {}
        if license_choice:
            # Read the selected license template
            license_template_path = Path(__file__).parent / license_choice
            if license_template_path.exists():
                license_content = license_template_path.read_text()
                skeleton[Path("LICENSE")] = license_content
        return skeleton
