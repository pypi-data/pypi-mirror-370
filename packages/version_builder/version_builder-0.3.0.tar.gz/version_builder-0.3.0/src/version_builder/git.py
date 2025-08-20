"""Module for interacting with Git repositories.

Provides a helper class to work with Git tags and logging.
"""

from logging import Logger

from git import Repo
from semver import Version

from .constants import ENABLED_CHOICES, INITIAL_VERSION
from .exceptions import BadChoiceError
from .logger import logger


class GitHelper:
    """A helper class to interact with a local Git repository."""

    repo: Repo
    log: Logger

    def __init__(self) -> None:
        """Initialize the Git repository and logger."""
        self.repo = Repo.init()
        self.remote = self.repo.remote()
        self.log = logger

    def get_last_tag(self) -> str | None:
        """Log information about existing Git tags or absence of them."""
        tag: str | None

        if not self.repo.tags:
            self.log.info("No tags found")
            tag = None
        else:
            tag: str = self.repo.tags[-1].name
            self.log.info("Last tag: %s", tag)

        return tag

    def bump(self, *, choice: ENABLED_CHOICES) -> None:
        """Bump the version based on the provided increment choice.

        Retrieves the last tag and generates a new one using the selected strategy.
        """
        tag: str | None = self.get_last_tag()

        if not tag:
            self.create_tag(tag=INITIAL_VERSION)
        else:
            bumped_tag = self._generate_tag_name(last_tag=tag, choice=choice)
            self.create_tag(tag=bumped_tag)

    def create_tag(self, *, tag: str) -> None:
        """Create and push a new Git tag with the specified name.

        Logs the creation of the tag locally and to the remote repository.
        """
        self.repo.create_tag(tag)
        self.remote.push(tag)
        self.log.info("Created tag %s", tag)

    @staticmethod
    def _generate_tag_name(*, last_tag: str, choice: ENABLED_CHOICES) -> str:
        """Generate a new semantic version string based on the last tag and bump choice.

        Uses semver rules to bump major, minor, or patch version accordingly.
        """
        ver = Version.parse(last_tag)
        match choice:
            case "major":
                ver = ver.bump_major()
            case "minor":
                ver = ver.bump_minor()
            case "patch":
                ver = ver.bump_patch()
            case _:
                raise BadChoiceError

        return str(ver)
