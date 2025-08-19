from requests import Response as BaseResponse

from .base import CacheBackend, MetaData
from .utils import loads_response, dumps_response
import os
import json
from datetime import timedelta, datetime, timezone
from typing import Iterator


class FileSystem(CacheBackend):
    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = cache_dir
        self.responses_dir = os.path.join(self.cache_dir, "responses")
        self.responses_meta_dir = os.path.join(self.cache_dir, "responses-meta")
        # self.debug_requests_dir = os.path.join(self.cache_dir, 'requests-debug')
        os.makedirs(self.responses_dir, exist_ok=True)
        os.makedirs(self.responses_meta_dir, exist_ok=True)
        # os.makedirs(self.debug_requests_dir, exist_ok=True)
        
        self._metas: dict[str, MetaData] = {}
        for key in os.listdir(self.responses_meta_dir):
            filepath = os.path.join(self.responses_meta_dir, key)
            with open(filepath, "rb") as f:
                data = json.load(f)
            self._metas[key] = MetaData(
                timestamp=datetime.fromisoformat(data["timestamp"]),
                access_timestamp=datetime.fromisoformat(data["access_timestamp"]),
                access_count=data["access_count"],
            )
    
    def get_metas(self) -> dict[str, MetaData]:
        return self._metas

    def get_response(self, key: str) -> BaseResponse | None:
        filepath = os.path.join(self.responses_dir, key)
        if not os.path.exists(filepath):
            return None
        with open(filepath, "rb") as f:
            resp = loads_response(f.read())
        return resp

    def update_response(self, key: str, response: BaseResponse) -> None:
        filepath = os.path.join(self.responses_dir, key)
        with open(filepath, "wb") as f:
            f.write(dumps_response(response))

    def get_meta(self, key: str) -> MetaData | None:
        return self._metas.get(key)

    def update_meta(self, key: str, meta: MetaData) -> None:
        filepath = os.path.join(self.responses_meta_dir, key)
        self._metas[key] = meta
        with open(filepath, "w") as f:
            json.dump(
                {
                    "timestamp": meta["timestamp"].isoformat(),
                    "access_timestamp": meta["access_timestamp"].isoformat(),
                    "access_count": meta["access_count"],
                },
                f,
            )

    def delete(self, key: str) -> None:
        filepath = os.path.join(self.responses_dir, key)
        meta_filepath = os.path.join(self.responses_meta_dir, key)
        os.remove(filepath)
        os.remove(meta_filepath)
        
        self._metas.pop(key)

    def keys(self) -> Iterator[str]:
        return iter(self._metas.keys())

    def clear(self) -> None:
        for filename in os.listdir(self.responses_dir):
            os.remove(os.path.join(self.responses_dir, filename))
        for filename in os.listdir(self.responses_meta_dir):
            os.remove(os.path.join(self.responses_meta_dir, filename))
            
        self._metas = {}

    def size(self) -> int:
        return len(self._metas)
