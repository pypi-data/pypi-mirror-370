"""Plugin registry module for the Engrate SDK.

This module provides the PluginRegistry class for managing plugin registration
with a remote registrar service.
At the moment, this method is proactive (the client is responsible for
registering plugins), but this will change in the future to a more
reactive approach where the server will automatically discover and register
plugins.
"""

from http import HTTPStatus
from pathlib import Path

from engrate_sdk.http.client import AsyncClient
from engrate_sdk.types.exceptions import ParseError, UncontrolledError, ValidationError
from engrate_sdk.types.plugins import BasePluginSpec
from engrate_sdk.utils import log

logger = log.get_logger(__name__)


class PluginRegistry:
    """A registry for managing plugins in the Engrate SDK."""

    def __init__(self, registrar_url: str, manifest_path: str | None = None):
        """Initialize the plugin registry."""
        self.registrar_url = registrar_url
        self.manifest_path = manifest_path

    def __load_yaml(self) -> BasePluginSpec:
        """Load the plugin specification from a YAML file.

        TODO this should be in a module
        """
        import yaml

        try:
            manifest_path = (
                Path(self.manifest_path)
                if self.manifest_path
                else Path("plugin_manifest.yaml")
            )
            with manifest_path.open() as file:
                data = yaml.safe_load(file)
                return BasePluginSpec(**data)
        except FileNotFoundError as err:
            raise ValidationError("Plugin specification file not found.") from err
        except yaml.YAMLError as err:
            raise ParseError(f"Error parsing plugin specification: {err}") from err

    async def register_plugin(self):
        """Register a plugin in the registry."""
        plugin = self.__load_yaml()

        async with AsyncClient() as client:
            response = await client.post(
                url=self.registrar_url,
                json=plugin.model_dump(),
                headers={"Content-Type": "application/json"},
            )
            if response.status_code != HTTPStatus.CREATED:
                json = response.json()
                msg = json.get("message", "Unknown error")
                logger.error(f"Failed to register plugin: {msg}")
                raise UncontrolledError(f"Failed to register plugin: {response.text}")
                raise UncontrolledError(f"Failed to register plugin: {response.text}")
