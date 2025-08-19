# PyDefinition

Environment-driven configuration helpers with low boilerplate.

## Installation

```bash
pip install pydefinition
```

## Features

- Environment variable management with descriptors
- Type casting for environment variables
- Default values and required variables
- Automatic naming based on class structure
- Caching for performance

## Usage

```python
from pydefinition import EnvVar, parse_bool, parse_int, Required

class AppConfig:
    # Basic usage with default value
    PORT = EnvVar(default=8080, cast=parse_int)
    
    # Required environment variable (raises KeyError if not set)
    API_KEY = EnvVar(default=Required)
    
    # Boolean parsing
    DEBUG = EnvVar(default=False, cast=parse_bool)
    
    # Custom name for environment variable
    DATABASE_URL = EnvVar(default="sqlite:///app.db", name="DB_URL")

# Usage
config = AppConfig()
port = config.PORT  # Will read from APP_CONFIG_PORT or use default 8080
api_key = config.API_KEY  # Will read from APP_CONFIG_API_KEY or raise KeyError
```

## Advanced Usage

See the [examples directory](https://github.com/Rushberg/PyDefinition/tree/main/pydefinition/examples) for more advanced usage patterns.

## License

This project is licensed under the MIT License - see the LICENSE file for details.