from requests import (
    Session as BaseSession,
    Request as BaseRequest,
    PreparedRequest as BasePreparedRequest,
    Response as BaseResponse,
)
from .base import BaseCacheSession, BaseCacheConfig
from types import EllipsisType

class CacheSession(BaseCacheSession, BaseSession):
    prepare_request = BaseSession.prepare_request
    send = BaseSession.send
    merge_environment_settings = BaseSession.merge_environment_settings
    def __init__(self, config: BaseCacheConfig | EllipsisType = ...) -> None:
        BaseCacheSession.__init__(self, config=config)
        BaseSession.__init__(self)
