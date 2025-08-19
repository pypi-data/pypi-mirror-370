from requests.sessions import (
    RequestsCookieJar,
    _HeadersUpdateMapping,
    _TextMapping,
    _HooksInput,
    _Settings,
    _Params,
    _Data,
    _Files,
    _Auth,
    _Timeout,
    _Verify,
    _Cert,
)
from requests.models import (
    Response,
    _JSON
)
from requests import (
    Request as BaseRequest,
    PreparedRequest as BasePreparedRequest,
    Response as BaseResponse,
)
from typing import Protocol, Any, Self, Generator
from types import EllipsisType
import os
import functools
from datetime import timedelta, datetime, timezone
from .utils import hash_request
from .backend import CacheBackend, CacheEvictionPolicie, MetaData
from .backend.filesystem import FileSystem
from contextlib import contextmanager
from dataclasses import dataclass

class HashRequestFn(Protocol):
    def __call__(self, prepared: BasePreparedRequest, cert: _Cert | None = None) -> str: ...
class BaseCacheSessionProtocol(Protocol):
    def prepare_request(self, request: BaseRequest) -> BasePreparedRequest: ...
    def send(
        self,
        request: BasePreparedRequest,
        *,
        stream: bool | None = ...,
        verify: _Verify | None = ...,
        proxies: _TextMapping | None = ...,
        cert: _Cert | None = ...,
        timeout: _Timeout | None = ...,
        allow_redirects: bool = ...,
        **kwargs: Any
    ) -> BaseResponse: ...
    def merge_environment_settings(
        self,
        url: str | bytes | None,
        proxies: _TextMapping | None,
        stream: bool | None,
        verify: _Verify | None,
        cert: _Cert | None,
    ) -> _Settings: ...



@dataclass(frozen=True)
class BaseCacheConfig:
    cache_backend: CacheBackend | None = FileSystem('.cache-cached_requests') # '.cache-cached_requests'
    hash_request_fn: HashRequestFn = hash_request
    refresh_after: timedelta | None = None
    refresh_on_error: bool = False
    force_refresh: bool = False
    offline_only: bool = False
    
    max_cache_files_count: int = -1
    cache_eviction_policie: CacheEvictionPolicie = CacheEvictionPolicie.LRU
    
    
class BaseCacheSession(BaseCacheSessionProtocol):
    config: BaseCacheConfig
    def __init__(self, config: BaseCacheConfig | EllipsisType = ...) -> None: ...
    
    @contextmanager
    def configure(
        self, 
        cache_backend: CacheBackend | None | EllipsisType = ...,
        hash_request_fn: HashRequestFn | EllipsisType = ...,
        refresh_after: timedelta | None | EllipsisType = ...,
        refresh_on_error: bool | EllipsisType = ...,
        force_refresh: bool | EllipsisType = ...,
        offline_only: bool | EllipsisType = ...,
        
        max_cache_files_count: int | EllipsisType = ...,
        cache_eviction_policie: CacheEvictionPolicie | EllipsisType = ...
    ) -> Generator[Self, None, None]: ...
    def request(
        self,
        method: str | bytes,
        url: str | bytes,
        params: _Params | None = None,
        data: _Data | None = None,
        headers: _HeadersUpdateMapping | None = None,
        cookies: None | RequestsCookieJar | _TextMapping = None,
        files: _Files | None = None,
        auth: _Auth | None = None,
        timeout: _Timeout | None = None,
        allow_redirects: bool = True,
        proxies: _TextMapping | None = None,
        hooks: _HooksInput | None = None,
        stream: bool | None = None,
        verify: _Verify | None = None,
        cert: _Cert | None = None,
        json: _JSON | None = None,
    ) -> BaseResponse: ...
