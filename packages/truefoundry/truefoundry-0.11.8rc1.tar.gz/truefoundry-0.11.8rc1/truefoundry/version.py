try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata

try:
    __version__ = importlib_metadata.version("truefoundry")
except Exception:
    __version__ = "NA"
