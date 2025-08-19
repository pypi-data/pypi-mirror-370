from pyscaf.actions import CLIOption


def cli_option_to_key(cli_option: CLIOption) -> str:
    return cli_option.name.lstrip("-").replace("-", "_")
