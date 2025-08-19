"""Version information."""

try:
    # Get the version from the installed package metadata
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("day2")
except (PackageNotFoundError, ModuleNotFoundError):
    # If the package is not installed or importlib.metadata is not available
    # use a default version
    __version__ = "0.0.1-dev"
