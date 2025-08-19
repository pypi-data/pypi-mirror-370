import os
import json
import pickle
import shutil
from typing import Protocol, BinaryIO, Iterator, TypedDict, overload, Literal
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from requests import Response as BaseResponse

class MetaData(TypedDict):
    timestamp: datetime # lru
    access_timestamp: datetime # fifo
    access_count: int # lfu

class CacheEvictionPolicie(Enum):
    LRU = "LRU"
    FIFO = "FIFO"
    LFU = "LFU"

class CacheBackendProtocol(Protocol):
    """
    A protocol that defines the interface for a cache backend.
    """
    
    def get_metas(self) -> dict[str, MetaData]:
        """Retrieve a CacheResponse's key and meta pair from the cache."""
        raise NotImplementedError
    
    def get_meta(self, key: str) -> MetaData | None:
        """Retrieve a CacheResponse's meta from the cache by its key."""
        raise NotImplementedError
    
    def get_response(self, key: str) -> BaseResponse | None:
        """Retrieve a CacheResponse from the cache by its key."""
        raise NotImplementedError
    
    def update_meta(self, key: str, meta: MetaData) -> None:
        """Store a CacheResponse's meta in the cache with a given key."""
        raise NotImplementedError
    
    def update_response(self, key: str, response: BaseResponse) -> None:
        """Store a CacheResponse in the cache with a given key."""
        raise NotImplementedError
    
    def delete(self, key: str) -> None:
        """Delete a responses and meta from the cache by its key."""
        raise NotImplementedError
    
    
    def clear(self) -> None:
        """Clear the entire cache."""
        raise NotImplementedError
    
    def keys(self) -> Iterator[str]:
        """List all keys in the cache."""
        raise NotImplementedError

    def size(self) -> int:
        """Number of keys in the cache."""
        raise NotImplementedError
    
class CacheBackend(CacheBackendProtocol):
    def get(self, key: str) -> BaseResponse | None:
        resp = self.get_response(key=key)
        if not resp: return None
        meta = self.get_meta(key=key)
        now = datetime.now(tz=timezone.utc)
        if meta is None:
            meta = MetaData(
                timestamp=now,
                access_count=0,    
                access_timestamp=now
            )
        new_meta = MetaData(
            timestamp=meta['timestamp'],
            access_count=meta['access_count'] + 1,
            access_timestamp=now
        )
        self.update_meta(key=key, meta=new_meta)
        return resp
    def set(self, key: str, response: BaseResponse, remove_item: int = -1, remove_policie: CacheEvictionPolicie = CacheEvictionPolicie.LRU) -> None:
        if remove_item > 0:
            metas: list[tuple[str, MetaData]] = list(self.get_metas().items())
            if remove_policie == CacheEvictionPolicie.LRU:
                metas.sort(key=lambda k: k[1]["timestamp"], reverse=False)
            elif remove_policie == CacheEvictionPolicie.FIFO:
                metas.sort(key=lambda k: k[1]["timestamp"], reverse=False)
            elif remove_policie == CacheEvictionPolicie.LFU:
                metas.sort(key=lambda k: k[1]["access_count"], reverse=False)
            else: 
                raise NotImplementedError
            for k, _ in metas[:remove_item]:
                self.delete(key=k)
        self.update_response(key=key, response=response)
        now = datetime.now(tz=timezone.utc)
        new_meta = MetaData(
            timestamp=now,
            access_count=1,    
            access_timestamp=now
        )
        self.update_meta(key=key, meta=new_meta)
    