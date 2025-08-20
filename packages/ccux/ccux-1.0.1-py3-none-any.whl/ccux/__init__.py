import importlib.metadata

try:
    __version__ = importlib.metadata.version('ccux')
except importlib.metadata.PackageNotFoundError:
    __version__ = 'unknown'
