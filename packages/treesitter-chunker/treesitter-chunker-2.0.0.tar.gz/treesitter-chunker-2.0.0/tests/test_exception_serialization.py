"""Test exception serialization for inter-process communication (IPC).

This test module verifies that exceptions can be properly serialized
and deserialized when passed between processes in multiprocessing scenarios.
"""

import multiprocessing
import pickle
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import pytest


class SimpleChunkerError(Exception):
    """Test base exception."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.args = message, details

    def __reduce__(self):
        return self.__class__, self.args


class SimpleLanguageError(Exception):
    """Test language error."""

    def __init__(self, language: str, available: list):
        message = f"Language '{language}' not found"
        super().__init__(message)
        self.language = language
        self.available = available
        self.args = language, available

    def __reduce__(self):
        return self.__class__, self.args


class CustomNonSerializableError(Exception):
    """Custom error with non-serializable attributes."""

    def __init__(self, message: str, non_serializable_obj: Any):
        super().__init__(message)
        self.non_serializable_obj = non_serializable_obj
        self.file_handle = Path(__file__).open("r", encoding="utf-8")

    def __del__(self):
        if hasattr(self, "file_handle") and not self.file_handle.closed:
            self.file_handle.close()


def worker_with_standard_exception():
    """Worker that raises a standard exception."""
    raise ValueError("Standard exception from worker process")


def worker_with_chunker_exception():
    """Worker that raises a chunker-specific exception."""
    raise SimpleLanguageError("python-extended", ["python", "javascript", "rust"])


def worker_with_nested_exception():
    """Worker that raises nested exceptions."""
    try:
        try:
            raise ValueError("Inner exception")
        except ValueError as e:
            raise SimpleChunkerError(
                "Parser failed",
                {"language": "python"},
            ) from e
    except SimpleChunkerError as e:
        raise RuntimeError("Config error: chunk_size must be positive") from e


def worker_with_custom_exception():
    """Worker that raises a non-serializable exception."""
    raise CustomNonSerializableError("Custom error", {"key": "value"})


def worker_with_traceback_info():
    """Worker that includes rich traceback information."""

    def level_3():
        x = 42
        y = "test"
        raise RuntimeError(f"Error at level 3 with x={x}, y={y}")

    def level_2():
        level_3()

    def level_1():
        level_2()

    level_1()


def worker_sometimes_fails(worker_id):
    """Worker that fails for certain IDs."""
    if worker_id % 3 == 0:
        raise ValueError(f"Worker {worker_id} failed")
    return f"Worker {worker_id} succeeded"


class TestExceptionSerialization:
    """Test exception serialization for IPC."""

    @classmethod
    def test_standard_exception_serialization(cls):
        """Test that standard exceptions can be serialized across processes."""
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(worker_with_standard_exception)
            with pytest.raises(ValueError) as exc_info:
                future.result()
            assert "Standard exception from worker process" in str(exc_info.value)

    @classmethod
    def test_chunker_exception_serialization(cls):
        """Test that chunker-specific exceptions can be serialized."""
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(worker_with_chunker_exception)
            with pytest.raises(SimpleLanguageError) as exc_info:
                future.result()
            error = exc_info.value
            assert error.language == "python-extended"
            assert "python" in error.available
            assert len(error.available) == 3

    @classmethod
    def test_nested_exception_serialization(cls):
        """Test that exception chains are preserved across processes."""
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(worker_with_nested_exception)
            with pytest.raises(RuntimeError) as exc_info:
                future.result()
            error = exc_info.value
            assert "Config error" in str(error)
            assert "chunk_size must be positive" in str(error)
            if hasattr(error, "__cause__"):
                cause_str = str(error.__cause__)
                assert "SimpleChunkerError" in cause_str
                assert "Parser failed" in cause_str
                assert "language" in cause_str
                assert "python" in cause_str
                assert "ValueError" in cause_str
                assert "Inner exception" in cause_str

    @classmethod
    def test_non_serializable_exception_handling(cls):
        """Test handling of exceptions that cannot be serialized."""
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(worker_with_custom_exception)
            with pytest.raises(TypeError) as exc_info:
                future.result()
            assert "cannot pickle" in str(exc_info.value)
            assert "TextIOWrapper" in str(exc_info.value)

    @classmethod
    def test_traceback_preservation(cls):
        """Test that traceback information is preserved across processes."""
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(worker_with_traceback_info)
            with pytest.raises(RuntimeError) as exc_info:
                future.result()
            tb_str = "".join(
                traceback.format_exception(
                    type(
                        exc_info.value,
                    ),
                    exc_info.value,
                    exc_info.tb,
                ),
            )
            assert "Error at level 3" in tb_str
            assert "x=42" in tb_str
            assert "y=test" in tb_str
            assert "level_3" in tb_str or "worker_with_traceback_info" in tb_str

    @classmethod
    def test_exception_pickling_directly(cls):
        """Test direct pickling of various exception types."""
        exceptions_to_test = [
            ValueError("Simple error"),
            RuntimeError("Runtime error"),
            SimpleChunkerError("Chunker error", {"key": "value"}),
            SimpleLanguageError("go", ["python", "rust"]),
            TypeError("Type error"),
            KeyError("missing_key"),
        ]
        for original_exc in exceptions_to_test:
            pickled = pickle.dumps(original_exc)
            restored_exc = pickle.loads(
                pickled,
            )
            assert isinstance(restored_exc, type(original_exc))
            assert str(restored_exc) == str(original_exc)
            if hasattr(original_exc, "language"):
                assert restored_exc.language == original_exc.language
            if hasattr(original_exc, "available"):
                assert restored_exc.available == original_exc.available
            if hasattr(original_exc, "details"):
                assert restored_exc.details == original_exc.details

    @classmethod
    def test_multiprocessing_queue_exception_passing(cls):
        """Test passing exceptions through multiprocessing Queue."""
        queue = multiprocessing.Queue()

        def worker_with_queue(q):
            try:
                raise SimpleChunkerError("Queue test error", {"language": "python"})
            except SimpleChunkerError as e:
                q.put(("error", e, traceback.format_exc()))

        process = multiprocessing.Process(target=worker_with_queue, args=(queue,))
        process.start()
        process.join()
        result_type, exc, tb_str = queue.get()
        assert result_type == "error"
        assert isinstance(exc, SimpleChunkerError)
        assert exc.details.get("language") == "python"
        assert "Queue test error" in str(exc)
        assert "SimpleChunkerError" in tb_str

    @classmethod
    def test_exception_with_large_context(cls):
        """Test serialization of exceptions with large context data."""
        large_data = "x" * (1024 * 1024)
        original_exc = SimpleChunkerError(
            "Error with large context",
            {"data": large_data},
        )
        pickled = pickle.dumps(original_exc)
        restored_exc = pickle.loads(
            pickled,
        )
        assert isinstance(restored_exc, SimpleChunkerError)
        assert len(restored_exc.details["data"]) == len(large_data)
        assert restored_exc.details["data"] == large_data

    @classmethod
    def test_exception_in_result_aggregation(cls):
        """Test exception handling when aggregating results from multiple workers."""
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(10):
                future = executor.submit(worker_sometimes_fails, i)
                futures.append((i, future))
            results = []
            errors = []
            for worker_id, future in futures:
                try:
                    result = future.result()
                    results.append((worker_id, result))
                except Exception as e:
                    errors.append((worker_id, type(e).__name__, str(e)))
            assert len(results) == 6
            assert len(errors) == 4
            for worker_id, exc_type, exc_msg in errors:
                assert exc_type == "ValueError"
                assert f"Worker {worker_id} failed" in exc_msg
                assert worker_id % 3 == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
