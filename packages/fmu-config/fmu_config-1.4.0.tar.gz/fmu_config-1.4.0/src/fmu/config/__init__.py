"""Top-level package for fmu_config"""

try:
    from .version import __version__
except ImportError:
    __version__ = "0.0.0"

from .configparserfmu import ConfigParserFMU

__all__ = ["__version__", "ConfigParserFMU"]
