from dataclasses import dataclass

from typing import overload, Protocol, Any
from types import EllipsisType

from requests import (
    Request as BaseRequest,
    PreparedRequest as BasePreparedRequest,
    Response as BaseResponse,
    ConnectionError as BaseConnectionError
)
import os
from datetime import timedelta, datetime, timezone
from .utils import hash_request
from .backend import CacheBackend, CacheEvictionPolicie, MetaData
from .backend.filesystem import FileSystem
from contextlib import contextmanager

class HashRequestFn(Protocol):
    def __call__(self, prepared: BasePreparedRequest, cert = None) -> str: raise NotImplementedError
class BaseCacheSessionProtocol(Protocol):
    def prepare_request(self, request: BaseRequest) -> BasePreparedRequest: raise NotImplementedError
    def send(self, request: BasePreparedRequest, **kwargs) -> BaseResponse: raise NotImplementedError
    def merge_environment_settings(
        self, url, proxies, stream, verify, cert
    ) -> dict: raise NotImplementedError

@dataclass(frozen=True)
class BaseCacheConfig:
    cache_backend: CacheBackend | None = None
    hash_request_fn: HashRequestFn = hash_request
    refresh_after: timedelta | None = None
    refresh_on_error: bool = False
    force_refresh: bool = False
    offline_only: bool = False
    
    max_cache_files_count: int = -1
    cache_eviction_policie: CacheEvictionPolicie = CacheEvictionPolicie.LRU
    
class BaseCacheSession(BaseCacheSessionProtocol):
    def __init__(self, config: BaseCacheConfig | EllipsisType = ...) -> None:
        self.config: BaseCacheConfig = config if config is not ... else BaseCacheConfig()
    
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
    ):
        old_config = self.config
        try:
            self.config = BaseCacheConfig(
                cache_backend=cache_backend if cache_backend is not ... else old_config.cache_backend,
                hash_request_fn=hash_request_fn if hash_request_fn is not ... else old_config.hash_request_fn,
                refresh_after=refresh_after if refresh_after is not ... else old_config.refresh_after,
                refresh_on_error=refresh_on_error if refresh_on_error is not ... else old_config.refresh_on_error,
                force_refresh=force_refresh if force_refresh is not ... else old_config.force_refresh,
                offline_only=offline_only if offline_only is not ... else old_config.offline_only,
                max_cache_files_count=max_cache_files_count if max_cache_files_count is not ... else old_config.max_cache_files_count,
                cache_eviction_policie=cache_eviction_policie if cache_eviction_policie is not ... else old_config.cache_eviction_policie
            )
            yield self
        finally:
            self.config = old_config
    
    def request(
        self,
        method: str | bytes,
        url: str | bytes,
        params=None,
        data=None,
        headers=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=None,
        allow_redirects: bool = True,
        proxies=None,
        hooks=None,
        stream: bool | None = None,
        verify=None,
        cert=None,
        json=None,
    ) -> BaseResponse:
        # Create the Request.
        req: BaseRequest = BaseRequest(
            method=method.upper(),
            url=url,
            headers=headers,
            files=files,
            data=data or {},
            json=json,
            params=params or {},
            auth=auth,
            cookies=cookies,
            hooks=hooks,
        )
        prep: BasePreparedRequest = self.prepare_request(req)
        
        filename: str | None = None
        meta: MetaData | None = None
        if self.config.cache_backend is not None:
            filename = self.config.hash_request_fn(prep, cert)
            meta = self.config.cache_backend.get_meta(filename)
            
        if not self.config.force_refresh and meta is not None and filename and self.config.cache_backend is not None and (
            cach_resp := self.config.cache_backend.get(filename)
        ) is not None:
            if self.config.refresh_after is not None:
                since = datetime.now(tz=timezone.utc) - meta['timestamp']
                if since < self.config.refresh_after and (
                    not self.config.refresh_on_error or cach_resp.ok
                ):
                    return cach_resp
            elif not self.config.refresh_on_error or cach_resp.ok:
                return cach_resp
        if self.config.offline_only:
            raise BaseConnectionError('Network access is disabled (offline_only=True)')
        proxies = proxies or {}
        
        settings = self.merge_environment_settings(
            prep.url, proxies, stream, verify, cert
        )

        # Send the request.
        send_kwargs = {
            "timeout": timeout,
            "allow_redirects": allow_redirects,
        }
        send_kwargs.update(settings)
        resp = self.send(prep, **send_kwargs)
        if filename and (cache_backend := self.config.cache_backend) is not None:
            size: int = cache_backend.size()
            remove_item: int = 1 + size - self.config.max_cache_files_count
            if self.config.max_cache_files_count < 0: remove_item = 0
            cache_eviction_policie = self.config.cache_eviction_policie
            if stream:  
                # NOTE: monkey patching...  
                resp_close = resp.close
                def callback():
                    cache_backend.set(filename, resp, remove_item, cache_eviction_policie)
                    resp_close()
                resp.close = callback
            else:
                cache_backend.set(filename, resp, remove_item, cache_eviction_policie)
        return resp