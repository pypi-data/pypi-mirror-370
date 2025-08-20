import logging
from io import StringIO
from typing import Generator

import pytest

from catchery.error_handler import ErrorHandler, log_critical, set_default_handler
from catchery.validation import ensure_object


@pytest.fixture
def handler() -> Generator[ErrorHandler, None, None]:
    """Fixture to provide a clean ErrorHandler instance for each test."""
    # Setup: Create a new handler for each test to ensure isolation
    h = ErrorHandler(use_json_logging=True)
    yield h
    # Teardown: Reset the global handler to ensure a clean state for the next test
    set_default_handler(None)


def test_non_json_serializable_context_is_serialized(handler: ErrorHandler):
    # Set the global handler, to our personal handler.
    set_default_handler(handler)

    # A non-JSON serializable object (a set)
    non_serializable_object = {"item1", "item2"}

    # The context dictionary containing the non-serializable object
    context_with_non_serializable = {
        "some_key": "some_value",
        "bad_data": non_serializable_object,
    }

    # Force ensure_object to trigger a log_warning by providing a value
    # that does not match the expected type.
    ensure_object(
        obj=123,  # Not a string
        name="test_param",
        expected_type=str,
        context=context_with_non_serializable,
    )


def test_log_critical_no_exception_details_on_console(handler: ErrorHandler):
    # Set the global handler, to our personal handler.
    set_default_handler(handler)

    # Capture stderr output
    captured_stderr = StringIO()
    handler.logger.addHandler(logging.StreamHandler(captured_stderr))

    # Log a critical error with an exception, but do not re-raise
    log_critical(
        "Database connection lost!",
        context={"db_host": "localhost"},
        exception=ConnectionError("No DB connection"),
        raise_exception=False,
    )

    # Get the captured output
    output = captured_stderr.getvalue()

    # Assert that the exception details are NOT in the output
    assert "ConnectionError: No DB connection" not in output
    assert "Database connection lost!" in output
