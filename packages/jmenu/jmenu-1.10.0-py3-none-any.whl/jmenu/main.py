"""
This file contains the logic for executing jmenu from the command line.
"""

import argparse
import sys
import time
from datetime import datetime, timedelta
from importlib.metadata import PackageNotFoundError, version
from os import get_terminal_size

from .classes import MARKERS, RESTAURANTS, MenuItem, MenuItemFactory


class _ArgsNamespace:
    """Dataclass for managing command line arguments

    Attributes:
        explain (bool):
            print allergen marker info
        allergens (list[str]):
            highlight the provided allergen markers
        tomorrow (bool):
            fetch the menus for tomorrow
    """

    explain: bool
    allergens: list[str]
    tomorrow: bool
    lang_code: str


def run():
    """Fetch and print restaurant menus

    Returns:
        success (bool):
            returns True if any errors were encountered,
            returns False otherwise
    """
    try:
        args = _get_args()
        if args.explain:
            _print_explanations(args.lang_code)
            return 0
        start = time.time()
        encountered_error = _print_menu(args)
        print("Process took {:.2f} seconds.".format(time.time() - start))
        return encountered_error
    except KeyboardInterrupt:
        return True


def _get_args():
    parser = argparse.ArgumentParser(
        description="Display University of Oulu restaurant menus for the day"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="display version information",
        version=get_version(),
    )
    parser.add_argument(
        "-e",
        "--explain",
        dest="explain",
        action="store_true",
        help="display allergen marking information",
    )
    parser.add_argument(
        "-t",
        "--tomorrow",
        dest="tomorrow",
        action="store_true",
        help="display menus for tomorrow",
    )
    parser.add_argument(
        "-l",
        "--language",
        dest="lang_code",
        choices=["fi", "en"],
        default="en",
        help="display language for menu items",
    )
    allergens = parser.add_argument_group("allergens")
    allergens.add_argument(
        "-a",
        "--allergens",
        dest="allergens",
        action="extend",
        type=str,
        metavar=("markers", "G, VEG"),
        nargs="+",
        help='list of allergens, for ex. "g veg"',
    )
    return parser.parse_args(namespace=_ArgsNamespace())


def _print_menu(args: _ArgsNamespace) -> bool:
    fac = MenuItemFactory()
    encountered_error = False
    fetch_date = datetime.now()
    if args.tomorrow:
        fetch_date += timedelta(days=1)

    allergens = []
    if args.allergens:
        allergens = [x.lower() for x in args.allergens]

    _print_header(fetch_date)
    for res in RESTAURANTS:
        try:
            items = fac.get_menu_items(res, fetch_date, args.lang_code)
            if len(items) == 0:
                print(res.name.ljust(8), "--")
            else:
                print(res.name)
                if not allergens:
                    print(
                        *[f"\t {item.name} {item.diets_to_string()}" for item in items],
                        sep="\n",
                    )
                else:
                    _print_highlight(items, allergens)

        except Exception as e:
            print(e)
            encountered_error = True
            print("Couldn't fetch menu for", res.name)
    return encountered_error


def _print_explanations(lang_code: str = "en"):
    for mark in MARKERS:
        print(mark.letters, "\t", mark.get_explanation(lang_code))


def _print_highlight(items: list[MenuItem], queried_allergens: list[str]):
    for item in items:
        item_markers = [diet.strip().lower() for diet in item.diets]
        if all(marker in item_markers for marker in queried_allergens):
            print("\033[92m", "\t", item.name, item.diets_to_string(), "\033[0m")
        else:
            print("\t", item.name, item.diets_to_string())


def _print_header(fetch_date: datetime):
    try:
        width = get_terminal_size()[0]
        if width is None or width > 79:
            width = 79
    except OSError:
        width = 79
    print("-" * width)
    print("Menu for", fetch_date.strftime("%d.%m"))
    print("-" * width)


def get_version() -> str:
    """Returns the application build version

    version data is pulled by importlib.metadata.version,
    defaults to 'development build' if it is not somehow present

    Returns:
        version (str):
            semantic versioning string
    """
    try:
        return version("jmenu")
    except PackageNotFoundError:
        return "development build"


if __name__ == "__main__":
    sys.exit(run())
