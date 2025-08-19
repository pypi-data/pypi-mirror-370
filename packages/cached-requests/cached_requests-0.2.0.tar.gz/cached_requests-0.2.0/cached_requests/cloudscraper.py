from requests import (
    Request as BaseRequest,
    PreparedRequest as BasePreparedRequest,
    Response as BaseResponse,
)
from cloudscraper import CloudScraper as BaseCloudScraper
from .base import BaseCacheSession, BaseCacheConfig
from types import EllipsisType
import random


class CacheCloudScraper(BaseCacheSession, BaseCloudScraper):
    prepare_request = BaseCloudScraper.prepare_request
    send = BaseCloudScraper.send
    merge_environment_settings = BaseCloudScraper.merge_environment_settings
    def __init__(self, user_agent_seed: int = 42, config: BaseCacheConfig | EllipsisType = ..., *args, **kwargs) -> None:
        BaseCacheSession.__init__(self, config=config)  
        # NOTE: monkey patching...  
        random_SystemRandom = random.SystemRandom
        if user_agent_seed != -1:
            random.SystemRandom = lambda: random.Random(user_agent_seed)
        BaseCloudScraper.__init__(self, *args, **kwargs)
        random.SystemRandom = random_SystemRandom
    request = BaseCloudScraper.request # type: ignore
    perform_request = BaseCacheSession.request # type: ignore