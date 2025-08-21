"""Configuration constants for b10-tcache.

This module defines configuration constants for the PyTorch compilation cache system.
Some values can be overridden by environment variables, but security caps are enforced
to prevent malicious or accidental misuse in production environments.
"""

import os
from enum import Enum

# Cache directories
TORCH_CACHE_DIR = os.getenv("TORCH_CACHE_DIR", "/tmp/torchinductor_root")
B10FS_CACHE_DIR = os.getenv("B10FS_CACHE_DIR", "/cache/model/compile_cache")
LOCAL_WORK_DIR = os.getenv("LOCAL_WORK_DIR", "/app")

# Security caps to prevent resource exhaustion
_MAX_CACHE_SIZE_CAP_MB = 1 * 1024  # 1GB hard limit per cache archive
_MAX_CONCURRENT_SAVES_CAP = 100  # Maximum concurrent save operations (only used as estimate for b10fs space requirements/thresholding)


def _apply_cap(value: int, cap: int, name: str) -> int:
    """
    Apply security cap to user-provided values.
    Not amazing (doesn't prevent the user from modifying the pip package
    source code), but at least it prevents accidental environment variable
    setting that could cause resource exhaustion.
    """
    if value > cap:
        import logging

        logging.getLogger(__name__).warning(
            f"{name} capped at {cap} (requested {value}) for security/stability"
        )
        return cap
    return value


# Cache limits (capped for security)
_user_max_cache_size = int(os.getenv("MAX_CACHE_SIZE_MB", "1024"))
MAX_CACHE_SIZE_MB = _apply_cap(
    _user_max_cache_size, _MAX_CACHE_SIZE_CAP_MB, "MAX_CACHE_SIZE_MB"
)

_user_max_concurrent_saves = int(os.getenv("MAX_CONCURRENT_SAVES", "50"))
MAX_CONCURRENT_SAVES = _apply_cap(
    _user_max_concurrent_saves, _MAX_CONCURRENT_SAVES_CAP, "MAX_CONCURRENT_SAVES"
)

# Space requirements
MIN_LOCAL_SPACE_MB = 50 * 1024  # 50GB minimum space on local machine
REQUIRED_B10FS_SPACE_MB = max(MAX_CONCURRENT_SAVES * MAX_CACHE_SIZE_MB, 100_000)

# B10FS configuration
# The default is "0" (disabled) to prevent accidental enabling.
# But this does limit the ability to enable b10fs for debugging purposes.
# Probably should use B10FS_ENABLED instead for thta.
BASETEN_FS_ENABLED = os.getenv("BASETEN_FS_ENABLED", "0")

# File naming patterns
CACHE_FILE_EXTENSION = ".tar.gz"
CACHE_LATEST_SUFFIX = ".latest"
CACHE_INCOMPLETE_SUFFIX = ".incomplete"
CACHE_PREFIX = "cache_"

# Archive settings
_user_tar_compression = int(os.getenv("TAR_COMPRESSION_LEVEL", "3"))
TAR_COMPRESSION_LEVEL = max(
    1, min(9, _user_tar_compression)
)  # Bounded between 1-9 inclusive

# Space monitoring settings
SPACE_MONITOR_CHECK_INTERVAL_SECONDS = (
    0.5  # How often to check disk space during operations
)


# Worker process result status enum
class WorkerStatus(Enum):
    """Status values for worker process results."""

    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"
