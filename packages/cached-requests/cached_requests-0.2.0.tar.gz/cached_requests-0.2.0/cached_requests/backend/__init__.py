from .base import CacheBackend, CacheEvictionPolicie, MetaData

LRU = CacheEvictionPolicie.LRU
FIFO = CacheEvictionPolicie.FIFO
LFU = CacheEvictionPolicie.LFU