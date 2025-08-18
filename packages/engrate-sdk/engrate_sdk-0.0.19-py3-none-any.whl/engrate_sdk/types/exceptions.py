"""Exception classes for controlled and uncontrolled errors in the engrate_sdk.

This module defines custom exceptions for handling known and unknown
error conditions, including token errors, missing resources, parsing
failures, and provider-specific issues.
"""

from typing import Any

from engrate_sdk.utils import log

logger = log.get_logger(__name__)


class ControlledError(Exception):
    """Base class for known, controlled exceptions."""

    pass


class MissingError(ControlledError):
    """Exception used for missing resources."""

    def __init__(self, kind: str, id: str, version: str | None = None):
        """Initialize a MissingError for a missing resource.

        Args:
            kind (str): The type of resource.
            id (str): The identifier of the resource.
            version (str | None, optional): The version of the resource, if applicable.
        """
        self.kind = kind
        self.id = id
        self.version = version
        if version:
            super().__init__(f"No {kind} with ID {id} and version {version} found")
        else:
            super().__init__(f"No {kind} with ID {id} found")


class NotMatchingError(ControlledError):
    """Exception used for resources that do not match."""

    def __init__(self, details: str):
        """Initialize a NotMatchingError with details about the mismatch.

        Args:
            details (str): Description of the mismatch.
        """
        self.details = details
        super().__init__(f"{details}")


class UnsetError(Exception):
    """Exception raised when a required environment variable is unset.

    Attributes:
    ----------
    message : str
        Explanation of the error.
    value : Any
        The value that caused the error (typically None).
    """

    def __init__(self, message: str, value: Any | None = None):
        """Initialize the UnsetError with a message and value."""
        super().__init__(message)
        self.value = value


class ValidationError(ControlledError):
    """Exception used for validation errors."""

    def __init__(self, details: str, value: Any | None = None):
        """Initialize a ValidationError with details about the validation failure.

        Args:
            details (str): Description of the validation error.
            value (Any | None, optional): The value that failed validation.
        """
        self.details = details
        self.value = value
        super().__init__(f"{details}")


class NotEnabledError(ControlledError):
    """Exception used for features that are not enabled or allowed."""

    def __init__(self, details: str):
        """Initialize a NotEnabledError with details about the not enabled feature.

        Args:
            details (str): Description of why the feature is not enabled.
        """
        self.details = details
        super().__init__(f"Not enabled: {details}")


class ParseError(ControlledError):
    """Exception used for failed parsing."""

    def __init__(self, details: str, value: Any | None = None):
        """Initialize an UncontrolledError with details about the error.

        Args:
            details (str): Description of the uncontrolled exception.
            value (Any | None, optional): The value that caused the parsing error.
        """
        self.details = details
        self.value = value
        super().__init__(f"{details}")


class AlreadyExistsError(ControlledError):
    """Exception used for resources that already exist."""

    def __init__(self, kind: str, id: str):
        """Initialize an AlreadyExistsError for a resource that already exists.

        Args:
            kind (str): The type of resource.
            id (str): The identifier of the resource.
        """
        self.kind = kind
        self.id = id
        super().__init__(f"{kind} with ID {id} already exists")


class UncontrolledError(Exception):
    """Base class for unknown, uncontrolled, unrecoverable exceptions."""

    def __init__(self, details: str):
        """Initialize a UncontrolledError with details about the failure.

        Args:
            details (str): Description of the unknown error.
        """
        self.details = details
        super().__init__(f"{details}")


class DispatchError(UncontrolledError):
    """Exception used for dispatch errors."""

    def __init__(self, details: str):
        """Initialize a DispatchError with details about the dispatch failure.

        Args:
            details (str): Description of the dispatch error.
        """
        self.details = details

        super().__init__(f"Failed to dispatch message to AS4 provider: {details}")


class UnknownError(UncontrolledError):
    """Nobody knows."""

    def __init__(self, details: str):
        """Initialize an UnknownError with details about the unknown error.

        Args:
            details (str): Description of the unknown error.
        """
        super().__init__(details)


class InitError(UncontrolledError):
    """Exception used for initialization errors."""

    def __init__(self, details: str):
        """Initialize an InitError with details about the initialization failure.

        Args:
            details (str): Description of the initialization error.
        """
        super().__init__(f"Init failure: {details}")
