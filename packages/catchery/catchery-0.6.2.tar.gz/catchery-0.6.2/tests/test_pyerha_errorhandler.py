import logging
import threading
from typing import Generator, List

import pytest

# Explicitly import from catchery modules.
from catchery import (
    AppError,
    ErrorHandler,
    ErrorSeverity,
    ensure_int_in_range,
    ensure_list_of_type,
    ensure_non_negative_int,
    ensure_string,
    safe_get_attribute,
    set_default_handler,
    validate_object,
    validate_type,
)


@pytest.fixture
def handler() -> Generator[ErrorHandler, None, None]:
    """Fixture to provide a clean ErrorHandler instance for each test."""
    # Setup: Create a new handler for each test to ensure isolation
    h = ErrorHandler(use_json_logging=True, suppress_validation_warnings=False)
    yield h
    # Teardown: Reset the global handler to ensure a clean state for the next test
    set_default_handler(None)


def test_basic_logging(handler: ErrorHandler) -> None:
    """Tests basic error handling and history logging."""
    handler.handle("Test info", ErrorSeverity.LOW)
    handler.handle("Test warning", ErrorSeverity.MEDIUM)
    handler.handle("Test error", ErrorSeverity.HIGH)
    assert len(handler.error_history) == 3
    assert handler.error_history[-1].severity == ErrorSeverity.HIGH


def test_error_history_limit(handler: ErrorHandler) -> None:
    """Tests that the error history correctly respects the maxlen limit."""
    handler = ErrorHandler(error_history_maxlen=2)
    handler.handle("A", ErrorSeverity.LOW)
    handler.handle("B", ErrorSeverity.LOW)
    handler.handle("C", ErrorSeverity.LOW)
    assert len(handler.error_history) == 2
    assert handler.error_history[0].message == "B"
    assert handler.error_history[1].message == "C"


def test_callbacks(handler: ErrorHandler) -> None:
    """Tests that registered callbacks are correctly invoked."""
    called: List[str] = []

    def cb(error: AppError) -> None:
        called.append(error.message)

    handler.register_callback(cb)
    handler.handle("Callback test", ErrorSeverity.LOW)
    assert called == ["Callback test"]


def test_context_manager(handler: ErrorHandler) -> None:
    """Tests that the context manager correctly adds contextual data."""
    with handler.Context(user_id=42):
        handler.handle("With context", ErrorSeverity.LOW)
    last = handler.error_history[-1]
    assert last.context.get("user_id") == 42


def test_capture_errors(handler: ErrorHandler) -> None:
    """Tests the capture_errors context manager."""
    with handler.CaptureErrors(handler) as errors:
        handler.handle("Captured", ErrorSeverity.LOW)
    assert errors and errors[0].message == "Captured"


def test_thread_safety() -> None:
    """Tests that the ErrorHandler is thread-safe."""
    handler = ErrorHandler(error_history_maxlen=200)

    def log_many() -> None:
        for i in range(50):
            handler.handle(f"Thread log {i}", ErrorSeverity.LOW)

    threads = [threading.Thread(target=log_many) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(handler.error_history) == 200


def test_exception_chaining(handler: ErrorHandler) -> None:
    """Tests that exceptions are correctly chained."""
    try:
        try:
            raise ValueError("inner")
        except ValueError as e:
            handler.handle(
                "outer",
                ErrorSeverity.HIGH,
                exception=RuntimeError("outer"),
                raise_exception=True,  # Corrected from raise_exc
                chain_exception=e,
            )
    except RuntimeError as exc:
        assert exc.__cause__ is not None
        assert isinstance(exc.__cause__, ValueError)


# Test validate_object
def test_validate_object_none():
    with pytest.raises(Exception, match="Required object 'test_obj' is None"):
        validate_object(None, "test_obj")


def test_validate_object_valid_no_attrs():
    obj = object()
    assert validate_object(obj, "test_obj") is obj


def test_validate_object_valid_with_attrs():
    class MyClass:
        def __init__(self):
            self.attr1 = 1
            self.attr2 = "hello"

        def method1(self):
            pass

    obj = MyClass()
    assert validate_object(obj, "test_obj", attributes=["attr1", "method1"]) is obj


def test_validate_object_missing_attrs():
    class MyClass:
        def __init__(self):
            self.attr1 = 1

    obj = MyClass()
    with pytest.raises(
        Exception, match=r"test_obj missing required attributes: \['attr2'\]"
    ):
        validate_object(obj, "test_obj", attributes=["attr1", "attr2"])


def test_validate_object_with_context():
    with pytest.raises(Exception, match="Required object 'test_obj' is None"):
        validate_object(None, "test_obj", context={"source": "test"})


# Test validate_type
def test_require_type_valid():
    assert validate_type("hello", "test_param", str) == "hello"
    assert validate_type(123, "test_param", int) == 123


def test_require_type_invalid():
    with pytest.raises(ValueError, match="Invalid test_param: expected str, got int"):
        validate_type(123, "test_param", str)


def test_require_type_none():
    with pytest.raises(Exception, match="Required object 'test_param' is None"):
        validate_type(None, "test_param", str)


def test_require_type_with_context():
    with pytest.raises(ValueError, match="Invalid test_param: expected str, got int"):
        validate_type(123, "test_param", str, context={"source": "test"})


# Test ensure_string
def test_ensure_string_already_string():
    assert ensure_string("hello", "test_param") == "hello"


def test_ensure_string_from_int(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_string(123, "test_param")
        assert result == "123"
        assert "test_param should be string, got: int, converting" in caplog.text


def test_ensure_string_from_none(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_string(None, "test_param")
        assert result == ""
        assert "test_param should be string, got: NoneType, converting" in caplog.text


def test_ensure_string_with_custom_default(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_string(None, "test_param", default="default_str")
        assert result == "default_str"


# Test ensure_non_negative_int
def test_ensure_non_negative_int_valid():
    assert ensure_non_negative_int(5, "test_param") == 5
    assert ensure_non_negative_int(0, "test_param") == 0


def test_ensure_non_negative_int_negative(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_non_negative_int(-5, "test_param")
        assert result == 0
        assert (
            "test_param must be non-negative integer, got: -5, correcting to 0"
            in caplog.text
        )


def test_ensure_non_negative_int_float(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_non_negative_int(5.7, "test_param")
        assert result == 5
        assert (
            "test_param must be non-negative integer, got: 5.7, correcting to 0"
            in caplog.text
        )


def test_ensure_non_negative_int_string(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_non_negative_int("abc", "test_param")
        assert result == 0
        assert (
            "test_param must be non-negative integer, got: abc, correcting to 0"
            in caplog.text
        )


def test_ensure_non_negative_int_none(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_non_negative_int(None, "test_param")
        assert result == 0
        assert (
            "test_param must be non-negative integer, got: None, correcting to 0"
            in caplog.text
        )


def test_ensure_non_negative_int_custom_default(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_non_negative_int("abc", "test_param", default=10)
        assert result == 10
        assert "correcting to 10" in caplog.text


# Test ensure_int_in_range
def test_ensure_int_in_range_valid():
    assert ensure_int_in_range(5, "test_param", 0, 10) == 5


def test_ensure_int_in_range_below_min(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_int_in_range(-5, "test_param", 0, 10)
        assert result == 0
        assert (
            "test_param must be integer between 0 and 10, got: -5, correcting to 0"
            in caplog.text
        )


def test_ensure_int_in_range_above_max(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_int_in_range(15, "test_param", 0, 10)
        assert result == 10
        assert (
            "test_param must be integer between 0 and 10, got: 15, correcting to 0"
            in caplog.text
        )


def test_ensure_int_in_range_no_max():
    assert ensure_int_in_range(100, "test_param", 0, None) == 100
    assert ensure_int_in_range(-5, "test_param", 0, None) == 0


def test_ensure_int_in_range_float(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_int_in_range(5.7, "test_param", 0, 10)
        assert result == 5


def test_ensure_int_in_range_string(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_int_in_range("abc", "test_param", 0, 10)
        assert result == 0
        assert (
            "test_param must be integer between 0 and 10, got: abc, correcting to 0"
            in caplog.text
        )


def test_ensure_int_in_range_none(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_int_in_range(None, "test_param", 0, 10)
        assert result == 0


def test_ensure_int_in_range_custom_default(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_int_in_range("abc", "test_param", 0, 10, default=5)
        assert result == 5
        assert "correcting to 5" in caplog.text


# Test ensure_list_of_type
def test_ensure_list_of_type_valid():
    assert ensure_list_of_type([1, 2, 3], "test_param", int) == [1, 2, 3]
    assert ensure_list_of_type(["a", "b"], "test_param", str) == ["a", "b"]


def test_ensure_list_of_type_none_input():
    assert ensure_list_of_type(None, "test_param", int) == []


def test_ensure_list_of_type_non_list_input(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_list_of_type("not a list", "test_param", int)
        assert result == []
        assert "test_param should be list, got: str, using default" in caplog.text


def test_ensure_list_of_type_mixed_types_no_converter(caplog):
    with caplog.at_level(logging.WARNING):
        result = ensure_list_of_type(
            values=[1, "2", 3.0, None],
            name="test_param",
            expected_type=int,
            allow_none=False,
        )
        assert result == [1, 2, 3]


def test_ensure_list_of_type_with_converter(caplog):
    def str_to_int_converter(s):
        return int(s)

    with caplog.at_level(logging.WARNING):
        result = ensure_list_of_type(
            values=[1, "2", 3.0, "invalid"],
            name="test_param",
            expected_type=int,
            allow_none=False,
            converter=str_to_int_converter,
        )
        assert result == [1, 2, 3]
        assert "test_param[3] failed validation, skipping item: invalid" in caplog.text


def test_ensure_list_of_type_with_validator(caplog):
    def is_positive(n):
        return n > 0

    with caplog.at_level(logging.WARNING):
        result = ensure_list_of_type(
            [1, -2, 3], "test_param", int, validator=is_positive
        )
        assert result == [1, 3]
        assert "test_param[1] failed validation, skipping item: -2" in caplog.text


def test_ensure_list_of_type_converter_and_validator(caplog):
    def converter(object: str) -> int:
        return int(object)

    def is_positive(object: int) -> bool:
        return object > 0

    with caplog.at_level(logging.WARNING):
        result = ensure_list_of_type(
            [1, "2", -3, "4", "invalid"],
            "test_param",
            int,
            converter=converter,
            validator=is_positive,
        )
        assert result == [1, 2, 4]


def test_ensure_list_of_type_custom_default():
    assert ensure_list_of_type(None, "test_param", int, default=[99]) == [99]


# Test safe_get_attribute
def test_safe_get_attribute_exists():
    class MyClass:
        def __init__(self):
            self.attr = 123

    obj = MyClass()
    assert safe_get_attribute(obj, "attr") == 123


def test_safe_get_attribute_not_exists(caplog):
    class MyClass:
        pass

    obj = MyClass()
    with caplog.at_level(logging.WARNING):
        result = safe_get_attribute(obj, "non_existent_attr", default="default_val")
        assert result == "default_val"
        assert (
            "MyClass missing attribute 'non_existent_attr', using default: default_val"
            in caplog.text
        )


def test_safe_get_attribute_none_obj():
    assert safe_get_attribute(None, "attr", default="default_val") == "default_val"


def test_safe_get_attribute_custom_default():
    class MyClass:
        pass

    obj = MyClass()
    assert safe_get_attribute(obj, "non_existent_attr", default=None) is None


def test_safe_get_attribute_custom_param_name(caplog):
    class MyClass:
        pass

    obj = MyClass()
    with caplog.at_level(logging.WARNING):
        safe_get_attribute(obj, "non_existent_attr", "my_object")
        assert "MyClass missing attribute 'non_existent_attr'" in caplog.text
