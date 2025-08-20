"""Custom exception raised when an invalid version bump choice is provided.

Used to signal errors in CLI or GitHelper when an unsupported option is selected.
"""


class BadChoiceError(Exception):
    """Exception raised for invalid choices passed to the bump command."""

    def __init__(self) -> None:
        """Initialize the exception with a default message.

        Message: "Invalid choice for bump version"
        """
        super().__init__("Invalid choice for bump version")
