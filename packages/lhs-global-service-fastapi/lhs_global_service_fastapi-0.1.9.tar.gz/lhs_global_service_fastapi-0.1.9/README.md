# lhs-global-service-fastapi

Global Oracle logging and debug management for FastAPI apps.

## Features
- Oracle DB logging integration
- Debug log flag management with TTL
- Date formatting for Oracle
- Configurable via environment variables
- Designed for FastAPI and other Python web apps

## Installation
```bash
pip install lhs-global-service-fastapi
```

## Usage
Import and configure in your FastAPI app:
```python
from global_service_fastapi_pkg import debug_log_flag_manager, global_service_pkg, oracle_date_formatter

# Example: Enable debug logs
debug_log_flag_manager.enable_debug_logs("username")

# Example: Format Oracle datetime
oracle_date_formatter.format_oracle_datetime("08-08-2025 12:34:56")

# Configure global service
global_service_pkg.config.configure(GLOBAL_LOG_URL="...", ORACLE_USER="...", ORACLE_PASS="...", ...)
```

## Requirements
- Python >= 3.7
- cx_Oracle
- requests
- python-dotenv

## License
MIT