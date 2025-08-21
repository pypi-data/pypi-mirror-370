# Not sure if these libraries should be nestled inside the code.

import hashlib
import logging
import os
import platform

# Optional imports - may not be available in all environments
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

try:
    import triton

    TRITON_AVAILABLE = True
except ImportError:
    triton = None
    TRITON_AVAILABLE = False

logger = logging.getLogger(__name__)


# FIXME(SR): I wonder if there's a race here if the environment info is trying to be extracted while we're importing torch/triton.


def get_environment_key() -> str:
    """Generate unique environment key based on PyTorch/Triton/GPU configuration.

    This function creates a deterministic hash key that uniquely identifies
    the current runtime environment, including PyTorch version, CUDA version,
    GPU compute capability, and Triton version. This ensures cache compatibility
    across different environments.

    Returns:
        str: A 12-character hex hash uniquely identifying the environment.
             Falls back to a deterministic string based on system properties
             if PyTorch/Triton are unavailable.

    Raises:
        No exceptions are raised; errors are handled gracefully with fallbacks.
    """
    try:
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available")

        components = []

        # PyTorch version
        torch_version = torch.__version__.split("+")[0]
        components.append(f"torch-{torch_version}")

        # CUDA/GPU info
        if torch.cuda.is_available():
            cuda_version = torch.version.cuda or "unknown"
            components.append(f"cuda-{cuda_version}")

            try:
                gpu_capability = torch.cuda.get_device_capability(0)
                components.append(f"cc-{gpu_capability[0]}.{gpu_capability[1]}")
            except Exception as e:
                logger.debug(f"Failed to get GPU capability: {e}")
                components.append("gpu-unknown")
        else:
            components.append("cpu")

        # Triton version
        if TRITON_AVAILABLE:
            triton_version = triton.__version__.split("+")[0]
            components.append(f"triton-{triton_version}")
        else:
            components.append("triton-none")

        # Create hash
        env_string = "_".join(components)
        env_hash = hashlib.sha256(env_string.encode()).hexdigest()[:12]

        return env_hash

    except Exception as e:
        logger.debug(f"Environment key generation failed: {e}")
        # Use deterministic fallback based on stable system properties
        fallback = f"fallback-{platform.machine()}-{platform.python_version()}-{platform.system()}"
        return hashlib.sha256(fallback.encode()).hexdigest()[:12]


def get_cache_filename() -> str:
    """Get the cache filename prefix for the current environment.

    This function generates a cache filename prefix that includes the
    environment key to ensure cache files are environment-specific.

    Returns:
        str: Cache filename prefix in format "cache_{environment_key}".
    """
    env_key = get_environment_key()
    return f"cache_{env_key}"


def get_hostname() -> str:
    """Get the hostname of the current machine.

    This function retrieves the hostname from the system, falling back to
    the HOSTNAME environment variable if the system hostname is unavailable.

    Returns:
        str: The machine hostname, or "unknown-host" if unavailable.
    """
    hostname = os.uname().nodename or os.getenv("HOSTNAME", "unknown-host")
    return hostname
