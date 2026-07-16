from importlib.metadata import PackageNotFoundError, version

try:
    # Single source of truth: read the installed distribution's version so it
    # always matches pyproject.toml instead of drifting (was hardcoded "0.1.0").
    __version__ = version("canvas-cli")
except PackageNotFoundError:  # running from a source tree that isn't installed
    __version__ = "0.4.0"

__all__ = ["__version__"]
