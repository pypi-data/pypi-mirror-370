try:
    import importlib.metadata as version_reader
except ImportError:
    import importlib_metadata as version_reader

try:
    __version__ = version_reader.version("sibi-dst")
except version_reader.PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "__version__",
]

from . import df_helper as df_helper
from . import osmnx_helper as osmnx_helper
from . import geopy_helper as geopy_helper
from . import utils as sibi_utils

