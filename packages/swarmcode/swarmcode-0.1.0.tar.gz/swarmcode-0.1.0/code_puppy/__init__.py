import importlib.metadata

try:
    __version__ = importlib.metadata.version("swarmcode")
except importlib.metadata.PackageNotFoundError:
    # Fallback for development installation
    __version__ = "0.1.0"
