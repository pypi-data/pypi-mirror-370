import os
import time
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Any

from .constants import BASETEN_FS_ENABLED, B10FS_CACHE_DIR

logger = logging.getLogger(__name__)


class CacheError(Exception):
    """Base cache operation error."""

    pass


class CacheValidationError(CacheError):
    """Path validation or compatibility check failed."""

    pass


def timed_fn(logger=logger, name=None):
    """Decorator to log function execution time.

    This decorator logs when a function starts and finishes, including the
    total execution time in seconds.

    Args:
        logger: Logger instance to use for logging. Defaults to module logger.
        name: Custom name to use in log messages. If None, uses function name.

    Returns:
        Decorator function that wraps the target function with timing logic.
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            logger.info(f"{name or fn.__name__} started")
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            logger.info(
                f"{name or fn.__name__} finished in {time.perf_counter() - start:.2f}s"
            )
            return result

        return wrapper

    return decorator


def safe_execute(error_message: str, default_return: Any = None):
    """Decorator to safely execute a function with error handling.

    This decorator catches all exceptions from the wrapped function and logs
    them with a custom error message, then returns a default value instead
    of propagating the exception.

    Args:
        error_message: Message to log when an exception occurs.
        default_return: Value to return if the function raises an exception.
                       Defaults to None.

    Returns:
        Decorator function that wraps the target function with error handling.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{error_message}: {e}")
                return default_return

        return wrapper

    return decorator


def critical_section_b10fs_file_lock(name):
    """Decorator to ensure critical section for b10fs file operations.

    This decorator ensures that the decorated function runs in a critical section
    where no other b10fs file operations can interfere. It uses a lock file to
    synchronize access.

    Args:
        name: The name of the operation, used for the lock file name.

    Returns:
        The decorated function with critical section handling.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            lock_dir = Path(B10FS_CACHE_DIR)
            lock_dir.mkdir(parents=True, exist_ok=True)

            lock_file = lock_dir / f"{name}.lock"
            while lock_file.exists():
                logger.debug("Waiting for lock file to be released...")
                time.sleep(1)

            lock_file.touch()
            try:
                return func(*args, **kwargs)
            finally:
                lock_file.unlink(missing_ok=True)

        return wrapper

    return decorator


def safe_unlink(
    file_path: Path, error_message: str, success_message: str = None
) -> None:
    """Safely unlink a file with dead mount filesystem protection.

    This function attempts to delete a file while gracefully handling cases
    where the filesystem (like b10fs) becomes unavailable or dead during
    the operation. It uses missing_ok=True to handle missing files.

    Args:
        file_path: Path to the file to delete.
        error_message: Message to log if deletion fails.
        success_message: Optional message to log if deletion succeeds.

    Raises:
        No exceptions are raised; all errors are caught and logged.
    """
    try:
        file_path.unlink(missing_ok=True)
        if success_message:
            logger.debug(success_message)
    except Exception as e:
        logger.error(f"{error_message}: {e}")


@contextmanager
def temp_file_cleanup(temp_path: Path) -> Generator[Path, None, None]:
    """Context manager for temporary file with automatic safe cleanup.

    This context manager ensures that temporary files are cleaned up even
    if the filesystem becomes unavailable during the operation. It uses
    safe_unlink to handle dead mount scenarios gracefully.

    Args:
        temp_path: Path to the temporary file to manage.

    Yields:
        Path: The temporary file path for use within the context.

    Raises:
        Cleanup errors are handled gracefully and logged but not raised.
    """
    try:
        yield temp_path
    finally:
        safe_unlink(temp_path, f"Failed to delete temporary file {temp_path}")


def _is_b10fs_enabled() -> bool:
    """Check if b10fs filesystem is enabled via environment variable.

    This function checks the BASETEN_FS_ENABLED environment variable to
    determine if the b10fs shared filesystem is available for cache operations.

    Returns:
        bool: True if BASETEN_FS_ENABLED is set to "1" or "True", False otherwise.
    """
    return BASETEN_FS_ENABLED in ("1", "True", "true")


def _validate_b10fs_available() -> None:
    """Validate that b10fs filesystem is available for cache operations.

    This function checks if b10fs is enabled and raises an exception if not.
    It should be called before any operations that require b10fs access.

    Raises:
        CacheValidationError: If b10fs is not enabled (BASETEN_FS_ENABLED
                            is not set to "1" or "True").
    """
    if not _is_b10fs_enabled():
        raise CacheValidationError(
            "b10fs is not enabled. Set BASETEN_FS_ENABLED=1 or BASETEN_FS_ENABLED=True to enable cache operations."
        )


@contextmanager
def cache_operation(operation_name: str) -> Generator[None, None, None]:
    """Context manager for cache operations with b10fs validation and error handling.

    This context manager validates that b10fs is available before executing
    cache operations and provides consistent error logging. It should wrap
    any operations that require b10fs access.

    Args:
        operation_name: Name of the operation for error logging (e.g., "Load", "Save").

    Yields:
        None: Context for the operation to execute.

    Raises:
        CacheValidationError: If b10fs is not available (re-raised after logging).
        Exception: Any other errors during the operation (re-raised after logging).
    """
    try:
        _validate_b10fs_available()
        yield
    except CacheValidationError as e:
        logger.debug(f"{operation_name} failed: {e}")
        raise
    except Exception as e:
        logger.debug(f"{operation_name} failed: {e}")
        raise
