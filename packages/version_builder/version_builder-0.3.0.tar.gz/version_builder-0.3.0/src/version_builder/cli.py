"""Module for the command-line interface of version_builder.

Provides a CLI entry point to interact with Git tags and display help.
"""

import argparse

from .constants import ENABLED_CHOICES
from .git import GitHelper
from .logger import logger as log
from .version import VERSION


class CLI:
    """Handles command-line arguments and user interaction."""

    def __init__(self) -> None:
        """Initialize the Git helper and argument parser."""
        self.git = GitHelper()

        self.parser = argparse.ArgumentParser(
            prog="version_builder",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self.parser.add_argument(
            "-v",
            "--version",
            action="store_true",
            help="Show builder version",
        )
        self.parser.add_argument(
            "-s",
            "--show",
            action="store_true",
            help="Show last tag",
        )
        self.parser.add_argument(
            "-b",
            "--bump",
            choices=ENABLED_CHOICES,
            help="Bump version (default: patch)",
        )

    def __call__(self) -> None:
        """Parse arguments and execute the appropriate command."""
        args = self.parser.parse_args()

        if args.show:
            self.show()
        elif args.bump:
            self.bump(choice=args.bump)
        elif args.version:
            self.version()
        else:
            self.help()

    def help(self) -> None:
        """Print help message from the argument parser."""
        self.parser.print_help()

    @staticmethod
    def version() -> None:
        """Display the current version of the version_builder package."""
        log.info("Current version: %s", VERSION)

    def show(self) -> None:
        """Display the last Git tag using the GitHelper."""
        self.git.get_last_tag()

    def bump(self, choice: ENABLED_CHOICES) -> None:
        """Bump the version in the Git repository based on the provided choice.

        Delegates to GitHelper to create a new tag with the bumped version.
        """
        self.git.bump(choice=choice)


def main() -> None:
    """Entry point for the CLI application."""
    cli_helper = CLI()
    cli_helper()
