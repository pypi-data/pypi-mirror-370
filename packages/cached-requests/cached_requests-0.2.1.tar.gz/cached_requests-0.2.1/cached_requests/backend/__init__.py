from .base import CacheBackend, CacheEvictionPolicie, MetaData
from .filesystem import FileSystem as FileCacheBackend

LRU = CacheEvictionPolicie.LRU
FIFO = CacheEvictionPolicie.FIFO
LFU = CacheEvictionPolicie.LFU

__all__ = [
    "CacheBackend",
    "CacheEvictionPolicie",
    "FileCacheBackend",
    "MetaData",
    "LRU",
    "FIFO",
    "LFU",
]