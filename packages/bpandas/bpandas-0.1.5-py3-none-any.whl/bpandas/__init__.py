from .btables import bfrequencies
from .bgraphics import blinebar

try:
    from importlib.metadata import version as _pkg_version

    __version__ = _pkg_version("bpandas")
except Exception:
    __version__ = "0.0.0+dev"
