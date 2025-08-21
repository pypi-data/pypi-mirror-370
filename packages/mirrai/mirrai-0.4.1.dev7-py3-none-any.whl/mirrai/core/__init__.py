_FALLBACK_VERSION = "0.4.1"

try:
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("mirrai")
    except PackageNotFoundError:
        __version__ = _FALLBACK_VERSION
except ImportError:
    __version__ = _FALLBACK_VERSION
