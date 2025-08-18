# Engrate SDK

A utility SDK providing common services for logging, configuration, and HTTP clients to connect the Engrate Platform.

## Features

- Simple and consistent logging interface
- Flexible configuration management
- HTTP client utilities for seamless API integration
- TypeScript support

## Installation

Add the dependency to your project configuration (i.e. UV):

```code
"engrate-sdk ~= 0.0.16"
```
Then update your local environment
```bash
uv pip install .
```

## Usage

```python
from engrate_sdk import Logger, Config, HttpClient

# Logging
logger = Logger()
logger.info('Engrate SDK initialized')

# Configuration
config = Config()
config.load_from_env()

# HTTP Client
client = HttpClient(base_url=config.get('API_URL'))
response = client.get('/status')
```

## Registry

The library contains a ```regystry.py``` module which provides access to our internal plugin registry. Every plugin has to call to the ```register_plugin()``` method
at some point in the plugin bootstrap process (if using ```FastAPI``this is usually recommended to use a lifespan function). 

```python
@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    """Startup and shutdown logic using lifespan events."""
    try:
        print("Validating environment variables...")
        env.validate()
        if env.should_register():
            logger.info("Registering plugin...")
            plugin = PluginRegistry(registrar_url=env.get_registrar_url())
            await plugin.register_plugin()
        yield
    finally:
        logger.info("Shutting down application...")
```
This method will look for a ```plugin_manifest.yaml```file at root level of the project (it's also possible to provide an url when initializing the ```PluginRegistry```object) This file must exist and contain the following format ***(WIP: this might change in the near future)***:

 ```yaml
name: "power-tariffs"
author: "Energy development solutions"
description: "Test plugin to use Engrate SDK"
product_category: "market_intelligence"
extensions:
  markets:
    - "*"
    - "nl"
    - "de"
    - "se"
plugin_metadata:
  display_name: "Demo Plugin"
  service_name: "demo-plugin"
  url_prefix: "demo-plugin"
  fav_icon: ""
  image: ""
  port: "3111"
  api_version: "v1"
  flavors:
    - "external-api"
  traits:
    - "storage"

 ```

### Mock registrar
For testing purposes, the library includes a ```mock registrar```that mimics the behaviour for the actual registrar in the core services. This is a simple ```FastApi``` server that will
implement the required endpoints for puglins lifecycle.

## Documentation

[TODO]

## License

[TBD]