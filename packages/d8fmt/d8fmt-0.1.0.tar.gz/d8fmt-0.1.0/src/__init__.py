from importlib.metadata import version, PackageNotFoundError

# Fetch the version from package metadata
try:
    __version__ = version("d8fmt")
except PackageNotFoundError:
    __version__ = "unknown"  # Fallback if the package metadata isn't available


# Import attributes, functions, and classes to be exposed as part of the public API
from .d8fmt import (
    dt,
    CANONICAL,
    DATETIME_LOOKUP_TABLE,
    is_zone_free,
    snap_fmt,
    datetime_snap,
)

# Define the public API with __all__
__all__ = [
    "dt",
    "CANONICAL",
    "DATETIME_LOOKUP_TABLE",
    "is_zone_free",
    "snap_fmt",
    "datetime_snap",
]
