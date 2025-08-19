import hashlib
import pickle
from requests import (
    Request as BaseRequest,
    PreparedRequest as BasePreparedRequest
)
from typing import BinaryIO

def hash_request(
    prepared: BasePreparedRequest,
    cert: str | None | tuple[str, str]
) -> str:
    canonicals = hashlib.sha256()
    if prepared.method is not None:
        canonicals.update(prepared.method.encode().replace(b'\x00', b'\x00\x00'))
    canonicals.update(b'\x00')
    if prepared.url is not None:
        canonicals.update(prepared.url.encode().replace(b'\x00', b'\x00\x00'))
    canonicals.update(b'\x00')
    
    # BUG: random boundary string in multipart/form-data is not handled
    boundary: str | None = None # FIX:
    if (
        (content_type := prepared.headers.get('Content-Type')) and 
        content_type[:len('multipart/form-data; boundary=')] == 'multipart/form-data; boundary='
    ):
        boundary = content_type[len('multipart/form-data; boundary='):]
    for k, v in sorted(prepared.headers.items()):
        canonicals.update(k.encode().replace(b'\x00', b'\x00\x00').replace(b'\x01', b'\x01\x01'))
        canonicals.update(b'\x01')
        if k == 'Content-Type' and boundary:
            canonicals.update(v.replace(boundary, '<|boundary|>').encode().replace(b'\x00', b'\x00\x00').replace(b'\x01', b'\x01\x01'))
        else:
            canonicals.update(v.encode().replace(b'\x00', b'\x00\x00').replace(b'\x01', b'\x01\x01'))
        canonicals.update(b'\x01')
    canonicals.update(b'\x00')
    if prepared.body is not None:
        if not isinstance(prepared.body, (str, bytes, bytearray, memoryview)):
            raise ValueError(f'Unknow type of prepared.body, type: {type(prepared.body)}')
        if boundary is not None:
            canonicals.update(
                prepared.body.replace(boundary, '<|boundary|>').encode().replace(b'\x00', b'\x00\x00')
                if isinstance(prepared.body, str) else 
                bytes(prepared.body).replace(boundary.encode(), b'<|boundary|>').replace(b'\x00', b'\x00\x00')
            )
        else:
            canonicals.update(
                prepared.body.encode().replace(b'\x00', b'\x00\x00')
                if isinstance(prepared.body, str) else 
                bytes(prepared.body).replace(b'\x00', b'\x00\x00')
            )
    canonicals.update(b'\x00')
    if cert is not None:
        if isinstance(cert, str):
            canonicals.update(cert.encode().replace(b'\x00', b'\x00\x00').replace(b'\x01', b'\x01\x01'))
        else:
            k, v = cert
            canonicals.update(k.encode().replace(b'\x00', b'\x00\x00').replace(b'\x01', b'\x01\x01'))
            canonicals.update(b'\x01')
            canonicals.update(v.encode().replace(b'\x00', b'\x00\x00').replace(b'\x01', b'\x01\x01'))
    return canonicals.hexdigest()


def dump_prepared_debug_info(prep: BasePreparedRequest, file: BinaryIO | str):
    data = {
        'method': prep.method,
        'url': prep.url,
        'headers': prep.headers,
        'body': prep.body
    }
    if isinstance(file, str):
        with open(file, "wb") as f:
            pickle.dump(data, f, fix_imports=False)
    else:
        pickle.dump(data, file, fix_imports=False)      
def load_prepared_debug_info(file: BinaryIO | str) -> BasePreparedRequest:
    if isinstance(file, str):
        with open(file, "rb") as f:
            data = pickle.load(f, fix_imports=False)
    else:
        data = pickle.load(file, fix_imports=False)
    prep = BasePreparedRequest()
    prep.method = data['method']
    prep.url = data['url']
    prep.headers = data['headers']
    prep.body = data['body']
    return prep