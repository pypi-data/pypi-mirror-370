"""Types and base classes for plugins in the Engrate SDK.

This module defines the BasePlugin class and related types for plugin development.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, field_serializer

from engrate_sdk.types.exceptions import ParseError, UnsetError
from engrate_sdk.utils import log

log = log.get_logger(__name__)


class BasePluginSpec(BaseModel):
    """Base class for all plugins in the Engrate SDK.

    This class provides a common interface for plugins, ensuring they can be initialized
    and have a name.
    """

    uid: UUID | None = None
    name: str
    author: str
    description: str | None = None
    enabled: bool = False
    plugin_metadata: dict[str, Any] = {}

    def __init__(self, **data: Any):
        """Initialize the plugin with the provided data."""
        super().__init__(**data)
        if not self.uid:
            self.uid = UUID(int=0)
        self.__validate()

    def __validate(self):
        """Validate the plugin's configuration.

        This method can be overridden by subclasses.
        """
        if not self.name:
            raise UnsetError("Plugin name must be set.")
        if not self.author:
            raise UnsetError("Plugin author must be set.")
        if type(self.enabled) is not bool:
            raise ParseError("Plugin enabled must be a boolean value.")

    @field_serializer("uid")
    def serialize_uid(self, uid: UUID):
        """Serialize the UUID to a string for output.

        Parameters
        ----------
        uid : UUID
            The UUID to serialize.

        Returns:
        -------
        str
            The string representation of the UUID.
        """
        return str(uid)
