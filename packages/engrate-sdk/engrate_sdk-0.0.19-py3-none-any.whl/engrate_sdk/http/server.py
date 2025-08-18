"""HTTP server configuration and runner for engrate-sdk.

This module defines the ServerConf configuration model and provides
a function to run a Uvicorn server with the specified settings.
"""

from typing import Annotated

import uvicorn
from pydantic import BaseModel, Field

from engrate_sdk.utils import log

logger = log.get_logger(__name__)


class ServerConf(BaseModel):
    """Configuration model for the HTTP server.

    Attributes:
    ----------
    port : int
        The port number to bind the server to (1-65535).
    host : str
        The hostname or IP address to bind the server to.
    debug : bool, optional
        Enables debug logging if True (default is False).
    autoreload : bool, optional
        Enables automatic reload on code changes if True (default is False).
    """

    port: Annotated[int, Field(gt=0, le=65535)]
    host: str
    debug: bool = False
    autoreload: bool = False


#### Actions ####


class HttpServer:
    """HTTP server runner for the Engrate SDK.

    This class provides a method to run the server with the specified configuration.
    """

    @staticmethod
    def run(conf: ServerConf, app_ref: str):
        """Runs the server."""
        logger.info(f"Starting server on {conf.host}:{conf.port}")
        uvicorn.run(  # type: ignore
            app_ref,
            host=conf.host,
            port=conf.port,
            log_level="debug" if conf.debug else "info",
            reload=conf.autoreload,
            log_config=None,
        )
