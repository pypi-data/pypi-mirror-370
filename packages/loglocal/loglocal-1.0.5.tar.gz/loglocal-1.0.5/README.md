# loglocal

`loglocal` is a Python library for advanced local logging, built on top of [loguru](https://github.com/Delgan/loguru) and [pydantic](https://github.com/pydantic/pydantic). It provides configurable logging with support for both synchronous and asynchronous function decorators, file rotation, retention, and more.

## Features

- Easy-to-use logger with sensible defaults
- Configurable via environment variables and pydantic models
- Supports both console and file logging
- Decorators for logging function execution (sync and async)
- File rotation, retention, compression, and serialization

## Installation
You can install `loglocal` via pip:
```bash
pip install loglocal
```
Or if you prefer to use `uv` (Universal Virtual Environment):
```bash
uv add loglocal
```
## Usage

```python
from loglocal import logger

logger.info("Hello from loglocal!")


@logger.wrap
def my_function(x, y):
  return x + y


@logger.wrap
async def my_async_function(x, y):
  return x * y
```

## API Reference

### `logger`

A class-level property that returns a configured `LogLocal` instance using default settings.

### `LogLocal`

Extends `loguru.Logger` with additional configuration and decorators.

#### Methods

- `from_config(config: LogLocalConfig, **kwargs) -> LogLocal`  
  Create a logger instance from a `LogLocalConfig` object.

- `wrap(func=None)`  
  Decorator to log execution of sync or async functions.

#### Example

```python
from loglocal import Logger, logger
from loglocal.models import LogLocalConfig

custom_logger = Logger(
    config=LogLocalConfig(
        ...  # Custom configuration parameters
    )
)
logger.info("Logging with default config")
```

### Configuration

#### Environment Variables
- `LOGLOCAL_PATH`: Path to the log file (default: `logs/app.log`)

You can customize logging behavior by passing a custom `LogLocalConfig`:

- `log_path`: Path to log file (default: `logs/app.log`) # overrides `LOGLOCAL_PATH` environment variable
- `log_format`: Log message format
- `log_level`: Logging level (default: `DEBUG`)
- `log_opt`: Additional options for the logger (e.g., `exception`, `depth`, `colors`, etc.) of type `LogLocalOptions`
- `log_config`: Pydantic model for additional configuration options (e.g., file rotation, retention, compression, etc.) of type `LogConfig`

## License

MIT