"""Module to expose version information."""
from importlib import metadata

try:
    __version__ = metadata.version("llm_api_client")
except metadata.PackageNotFoundError:
    # Fallback when running from source without installation
    __version__ = "0.0.0"

__version_info__ = tuple(__version__.split("."))
