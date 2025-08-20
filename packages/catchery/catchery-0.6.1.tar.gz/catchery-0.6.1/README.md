# Catchery: A Robust Python Error Handling Library

[![PyPI - Version](https://img.shields.io/pypi/v/catchery.svg)](https://pypi.org/project/catchery/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/catchery.svg)](https://pypi.org/project/catchery/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Catchery is a comprehensive Python library designed to streamline error handling in your applications. It provides a centralized, structured, and flexible approach to managing errors, logging, and exceptions, making your code more robust and maintainable.

## Features

- **Structured Error Representation:** Define and manage application errors with severity levels, contextual data, and associated exceptions using the `AppError` dataclass.
- **Simplified Setup:** Quickly configure your error handling system with the `setup_catchery_logging()` convenience function, enabling easy setup of logging levels, file outputs (plain text and structured JSON), and more.
- **Flexible Logging:** Integrate seamlessly with Python's standard `logging` module. Output logs to console, plain text files, or structured JSON Lines files for easy parsing and analysis.
- **Thread-Safe Context Management:** Attach thread-local contextual data to all errors within a specific scope using `ErrorHandler.Context`, ensuring rich and relevant error information.
- **Robust Exception Chaining:** Utilize the `re_raise_chained` decorator to catch exceptions, log them, and re-raise new exceptions while preserving the original exception chain, providing clear error propagation paths.
- **Safe Operation Execution:** Execute potentially risky operations with built-in fallback mechanisms using `safe_operation`, preventing application crashes and ensuring graceful degradation.
- **Integrated Validation:** Leverage validation utilities that seamlessly log warnings and errors through the centralized error handling system.
- **In-Memory Error History:** Maintain a configurable history of recent `AppError` instances for debugging and analysis.

## Installation

You can install `catchery` using pip:

```bash
pip install catchery
```

## Quick Start

Get your error handling system up and running quickly with these examples.

### Basic Console Logging

Log messages directly to the console.

```python
import logging
from catchery.error_handler import setup_catchery_logging, log_error, log_info

# Set up logging to console (default behavior)
handler = setup_catchery_logging(level=logging.INFO)

log_info("Application started successfully.")

try:
    result = 10 / 0
except ZeroDivisionError as e:
    log_error("An unexpected error occurred during calculation.", context={"operation": "division"}, exception=e)

log_info("Application finished.")
```

### Logging to a Plain Text File

Direct your logs to a plain text file for persistent storage.

```python
import logging
import os
from catchery.error_handler import setup_catchery_logging, log_error, log_info

LOG_FILE = "app_errors.log"
if os.path.exists(LOG_FILE): os.remove(LOG_FILE) # Clean up from previous runs

# Set up logging to a plain text file
handler = setup_catchery_logging(
    level=logging.INFO,
    text_log_path=LOG_FILE
)

log_info("Application started, logging to file.")
try:
    value = int("not-a-number")
except ValueError as e:
    log_error("Failed to parse configuration value.", context={"config_key": "timeout"}, exception=e)

log_info("Application finished, check app_errors.log.")

# In a real application, you might read the log file here to verify
# with open(LOG_FILE, "r") as f:
#     print(f.read())
# os.remove(LOG_FILE) # Clean up
```

### Logging Structured JSON Errors

Store detailed error information in a JSON Lines file for easy programmatic parsing and analysis.

```python
import logging
import os
from catchery.error_handler import setup_catchery_logging, log_error, log_info

JSON_LOG_FILE = "app_errors.jsonl"
if os.path.exists(JSON_LOG_FILE): os.remove(JSON_LOG_FILE) # Clean up from previous runs

# Set up logging to a structured JSON Lines file
handler = setup_catchery_logging(
    level=logging.DEBUG,
    json_log_path=JSON_LOG_FILE
)

log_info("Application started, logging structured errors.")
try:
    data = {"user_id": "abc-123", "input_data": [1, 2, {"complex": "object"}]}
    raise ValueError("Invalid data received")
except ValueError as e:
    log_error(
        "Data processing failed.",
        context={"data_payload": data, "processor_id": "P-789"},
        exception=e
    )
log_info("Application finished, check app_errors.jsonl.")

# In a real application, you might read the log file here to verify
# import json
# with open(JSON_LOG_FILE, "r") as f:
#     for line in f:
#         print(json.loads(line))
# os.remove(JSON_LOG_FILE) # Clean up
```

### Combined Logging Setup

Combine console, plain text file, and structured JSON logging for comprehensive error management.

```python
import logging
import os
from catchery.error_handler import setup_catchery_logging, log_error, log_info

CONSOLE_LOG_FILE = "app_console.log" # For demonstration, console output can also go to a file
TEXT_LOG_FILE = "app_text.log"
JSON_LOG_FILE = "app_json.jsonl"

# Clean up from previous runs
if os.path.exists(CONSOLE_LOG_FILE): os.remove(CONSOLE_LOG_FILE)
if os.path.exists(TEXT_LOG_FILE): os.remove(TEXT_LOG_FILE)
if os.path.exists(JSON_LOG_FILE): os.remove(JSON_LOG_FILE)

# Set up combined logging
handler = setup_catchery_logging(
    level=logging.DEBUG,
    text_log_path=TEXT_LOG_FILE,
    json_log_path=JSON_LOG_FILE,
    use_json_logging=True # Main logger will output JSON to console/text_log_path
)

log_info("Combined setup: Application started.", context={"env": "development"})
try:
    # Simulate an error with complex context
    data = {"transaction_id": "tx-456", "amount": 100.50}
    raise RuntimeError("Payment gateway timeout")
except RuntimeError as e:
    log_error(
        "Payment processing failed.",
        context={"transaction_details": data, "gateway": "stripe"},
        exception=e
    )
log_info("Combined setup: Application finished.")

# Don't forget to call shutdown if your script is short-lived
# atexit automatically registers shutdown for the default handler
# handler.shutdown() # Not strictly necessary here due to atexit, but good practice for clarity

# In a real application, you would check the contents of the log files
# os.remove(TEXT_LOG_FILE)
# os.remove(JSON_LOG_FILE)
```

## Advanced Usage

### Context Management

Use `ErrorHandler.Context` to add temporary, thread-local context to your error logs:

```python
from catchery.error_handler import get_default_handler, log_error

handler = get_default_handler() # Assumes setup_catchery_logging has been called

with handler.Context(request_id="req-001", user_session="sess-xyz"):
    log_error("Failed to process user request.")
    # All errors logged within this 'with' block will automatically include request_id and user_session
```

### Safe Operations

Prevent crashes and provide fallback values for risky operations:

```python
from catchery.error_handler import safe_operation

@safe_operation(default_value=None, error_message="Failed to fetch data from API")
def fetch_data_from_api(url: str):
    # Simulate an API call that might fail
    if "error" in url:
        raise ConnectionError("API connection failed")
    return {"status": "success", "data": "some_data"}

# Successful call
data = fetch_data_from_api("http://api.example.com/data")
print(f"Fetched data: {data}")

# Failed call, returns default_value (None)
error_data = fetch_data_from_api("http://api.example.com/error")
print(f"Failed to fetch data: {error_data}")
```

### Exception Chaining

Chain exceptions to provide a clear audit trail of error propagation:

```python
from catchery.error_handler import re_raise_chained, ChainedReRaiseError

class DatabaseError(Exception):
    pass

class ServiceError(Exception):
    pass

@re_raise_chained(message="Failed to connect to database.", new_exception_type=DatabaseError)
def connect_to_db():
    raise ConnectionRefusedError("DB server not responding")

@re_raise_chained(message="Service operation failed.", new_exception_type=ServiceError)
def perform_service_operation():
    try:
        connect_to_db()
    except DatabaseError as e:
        # Re-raise the DatabaseError as a ServiceError, chaining it
        raise ServiceError("Underlying database issue.") from e

try:
    perform_service_operation()
except ServiceError as e:
    print(f"Caught ServiceError: {e}")
    if e.__cause__:
        print(f"Caused by: {e.__cause__} ({type(e.__cause__).__name__})")
```

## Development

### Running Tests

To run the unit and integration tests, ensure you have `pytest` installed and run:

```bash
PYTHONPATH=./src pytest
```

### Linting with Ruff

This project uses [Ruff](https://beta.ruff.rs/docs/) for linting and code formatting. Ruff is configured via the `pyproject.toml` file in the project root.

To run the linter, execute the following command from the project root:

```bash
ruff check src/catchery/
```

### Type Checking with MyPy

This project uses [MyPy](https://mypy.readthedocs.io/en/stable/) for static type checking. MyPy is configured via the `pyproject.toml` file.

To run type checks, execute the following command from the project root:

```bash
mypy src/catchery/
```

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) (Coming soon) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
