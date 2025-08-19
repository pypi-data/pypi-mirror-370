from requests.sessions import (
    CaseInsensitiveDict as BaseCaseInsensitiveDict, 
    RequestsCookieJar as BaseRequestsCookieJar
)
from requests import (
    Response as BaseResponse,
    PreparedRequest as BasePreparedRequest,
)
import pickle
from typing import BinaryIO, IO, overload, Iterator, TypedDict
from datetime import datetime, timedelta, timezone

class ResponseMeta(TypedDict):
    _content: bytes | None
    status_code: int
    headers: dict[str, str]
    url: str
    encoding: str | None
    reason: str
    cookies: dict[str, str]
    elapsed: float
class RequestMeta(TypedDict):
    method: str | None
    url: str | None
    headers: dict[str, str]
    body: bytes | str | None
class DataMeta(TypedDict):
    response: ResponseMeta
    request: RequestMeta
def dumps_response(response: BaseResponse) -> bytes:
    request: BasePreparedRequest = response.request
    request_data: RequestMeta = {
        'method': request.method,
        'url': request.url,
        'headers': dict(request.headers),
        'body': request.body
    }
    response_data: ResponseMeta = {
        "_content": response._content,
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "url": response.url,
        "encoding": response.encoding,
        "reason": response.reason,
        "cookies": response.cookies.get_dict(),
        "elapsed": response.elapsed.total_seconds(),
    }
    data: DataMeta = {
        "response": response_data,
        "request": request_data
    }
    return pickle.dumps(data, fix_imports=False)


def loads_response(content: bytes) -> BaseResponse:
    data: DataMeta = pickle.loads(content, fix_imports=False)
    request_data: RequestMeta = data['request']
    response_data: ResponseMeta = data['response']
    resp = BaseResponse()
    resp._content = response_data["_content"]
    resp._content_consumed = True  # type: ignore
    resp._next = None  # type: ignore
    resp.status_code = response_data["status_code"]
    resp.headers = BaseCaseInsensitiveDict(response_data['headers'])
    resp.raw = None
    resp.url = response_data["url"]
    resp.encoding = response_data["encoding"]
    resp.history = []  # redirect
    resp.reason = response_data["reason"]
    resp.cookies = BaseRequestsCookieJar()
    resp.cookies.update(response_data["cookies"])
    resp.elapsed = timedelta(seconds=response_data["elapsed"])
    req = BasePreparedRequest()
    req.body = request_data["body"]
    req.method = request_data["method"]
    req.url = request_data["url"]
    req.headers = BaseCaseInsensitiveDict(request_data["headers"])
    resp.request = req
    return resp
