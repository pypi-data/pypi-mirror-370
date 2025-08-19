import importlib.metadata

try:
    __version__ = importlib.metadata.version("memory")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0"  # fallback version

from memory.client.main import AsyncMemoryClient, MemoryClient  # noqa
from memory.memory.main import AsyncMemory, Memory  # noqa
