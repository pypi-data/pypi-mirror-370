# loguru_wrapper

A lightweight wrapper around [loguru](https://github.com/Delgan/loguru) that provides lazy evaluation and automatic caller context detection.

## Features

-   **Lazy Evaluation**: Log arguments are only evaluated if the log level is enabled
-   **Automatic Caller Detection**: Shows actual function name and line number in logs
-   **Format Conversion**: Automatically converts `%s` format strings to `{}` format
-   **Full Loguru Support**: All log levels (debug, info, success, warning, error, critical)
-   **Structured Logging**: Built-in structured logging support

## Installation

```bash
pip install -e /path/to/loguru_wrapper
```

## Quick Start

```python
from loguru_wrapper import logger

def my_function():
    log = logger()
    log.debug("User: {}", get_username)  # Lazy evaluation
    log.info("Processing %s items", item_count)  # Format conversion
    log.structured("user_login", user_id=123, success=True)
```

Output:

```
2025-07-17 09:18:27.409 | DEBUG | my_module:my_function:42 | User: john_doe
2025-07-17 09:18:27.429 | INFO  | my_module:my_function:43 | Processing 5 items
2025-07-17 09:18:27.449 | INFO  | my_module:my_function:44 | EVENT=user_login user_id=123 success=True
```

## Configuration

```python
from loguru_wrapper import logger, LoggerConfig

config = LoggerConfig(
    default_level="DEBUG",
    enable_lazy=True
)
log = logger(config=config)
```

## Requirements

-   Python ≥ 3.10
-   loguru ≥ 0.7.3
-   stackwalker ≥ 0.4.2
