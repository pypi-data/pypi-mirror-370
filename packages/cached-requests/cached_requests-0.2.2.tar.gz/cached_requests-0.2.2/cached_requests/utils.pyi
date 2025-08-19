from requests.sessions import (
    RequestsCookieJar,
    _HeadersUpdateMapping,
    _TextMapping,
    _Params,
    _Data,
    _Files,
    _Auth,
    _Cert
)
from requests.models import _JSON

from requests import (
    Request as BaseRequest,
    PreparedRequest as BasePreparedRequest
)

from typing import BinaryIO

def hash_request(
    prepared: BasePreparedRequest,
    cert: _Cert | None = None,
) -> str: ...


def dump_prepared_debug_info(prep: BasePreparedRequest, file: BinaryIO | str): ...
def load_prepared_debug_info(file: BinaryIO | str) -> BasePreparedRequest: ...