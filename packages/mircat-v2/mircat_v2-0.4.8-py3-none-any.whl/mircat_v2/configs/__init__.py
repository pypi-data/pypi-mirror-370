from argparse import _SubParsersAction
from pprint import pprint
from .config import *


def add_config_subparser(subparsers: _SubParsersAction) -> None:
    "Add config specific subcommands to mircat-v2 cli interface"
    config_parser = subparsers.add_parser(
        "config",
        description="Show specific configurations stored in the config.json",
        help="Show mircat-v2 config",
    )
    config_parser.add_argument(
        "key",
        type=str,
        default="all",
        choices=["all", "dbase", "models", "stats_models"],
    )
    config_parser.add_argument(
        "--subkey",
        "-s",
        type=str,
        default=None,
        help="Show a specific subkey of the config - e.x. input `mircat-v2 config dbase -s tables` -> config[dbase][tables]",
    )


def print_config(key: str, subkey: str | None) -> None:
    """Print the specified key"""
    config = read_config()
    if key == "all":
        pprint(config, indent=4)
        return
    text = config.get(key, {})
    if not text:
        print(f"No config found for {key}")
        return
    if subkey:
        text = text.get(subkey)
        if not text:
            print(f"No config found for {key}[{subkey}]")
            return
    pprint(text, indent=4)
