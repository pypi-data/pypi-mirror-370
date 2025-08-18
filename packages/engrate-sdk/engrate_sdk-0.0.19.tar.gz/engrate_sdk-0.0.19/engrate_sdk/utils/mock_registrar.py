"""Mock plugin registrar for engrate_sdk.

This module provides a FastAPI app with endpoints to register plugins for testing
purposes.
"""

from typing import Dict, List
from uuid import UUID, uuid4

from fastapi import FastAPI
from starlette import status

from engrate_sdk.http import server
from engrate_sdk.http.server import ServerConf
from engrate_sdk.types.plugins import BasePluginSpec
from engrate_sdk.utils import log

logger = log.get_logger(__name__)

app: FastAPI = FastAPI()
registrar: Dict[UUID, BasePluginSpec] = {}


@app.post(
    "/plugins",
    status_code=status.HTTP_201_CREATED,
    response_model=BasePluginSpec,
    description="Register a new plugin",
)
async def register_plugin(plugin: BasePluginSpec) -> BasePluginSpec:
    """Mock endpoint to register a new plugin.

    Parameters
    ----------
    plugin : BasePluginSpec
        The plugin specification to register.

    Returns:
    -------
    BasePluginSpec
        The registered plugin with a new UUID assigned.
    """
    logger.info(f"Registering plugin: {plugin.name} by {plugin.author}")
    uuid = uuid4()
    plugin.uid = uuid
    registrar[uuid] = plugin
    return plugin


@app.get(
    "/plugins",
    response_model=list[BasePluginSpec],
    description="Register a new plugin",
)
async def list_plugins() -> List[BasePluginSpec]:
    """Mock endpoint to list all registered plugins.

    Returns:
    -------
    list[BasePluginSpec]
        A list of all registered plugins.
    """
    logger.info("Listing all registered plugins")
    return list(registrar.values())


def run() -> None:
    """Run the mock plugin registrar FastAPI server for testing purposes."""
    config = ServerConf(port=8899, host="0.0.0.0", debug=True, autoreload=True)  # noqa: S104
    server.run(config, "engrate_sdk.utils.mock_registrar:app")
