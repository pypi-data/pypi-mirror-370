"""
A JSON-oriented API client using only Python standard library.
"""
from __future__ import annotations

import json
import logging
import re
import ssl
from http import HTTPStatus
from http.client import HTTPMessage, HTTPResponse
from io import IOBase
from typing import Any, Generator, Literal, Mapping, MutableMapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from http.client import RemoteDisconnected

from zut import get_logger, NotFound

class ApiClient:
    """
    A JSON API client using only Python standard library.
    """

    base_url : str|None = None

    timeout: float|None = None
    """ Timeout in seconds. """

    force_trailing_slash: bool = False

    default_headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json; charset=utf-8',
    }

    json_encoder_cls: type[json.JSONEncoder]|None = None
    json_decoder_cls: type[json.JSONDecoder] = json.JSONDecoder
    
    default_retries = 3
    error_message_maxlen = 400

    no_ssl_verify = False

    iter_results_key = 'results'
    iter_next_key = 'next'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # necessary to allow this class to be used as a mixin
        self._logger = get_logger(type(self))
        self._ssl_context = None
        if self.no_ssl_verify or kwargs.get('no_ssl_verify'):
            self._ssl_context = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

        if not self.__class__.json_encoder_cls:            
            from zut.json import ExtendedJSONEncoder
            self.__class__.json_encoder_cls = ExtendedJSONEncoder


    def __enter__(self):
        return self


    def __exit__(self, exc_type = None, exc_value = None, exc_traceback = None):
        pass


    def get(self, endpoint: str, *, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None, retries: int|None = None) -> dict[str,Any]:
        result = self.request(endpoint, method='GET', params=params, headers=headers, retries=retries)
        if not isinstance(result, dict):
            raise ApiClientError("Response is not a dictionnary", result, message_maxlen=self.error_message_maxlen)
        return result


    def iter(self, endpoint: str, *, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None, retries: int|None = None) -> Generator[dict[str,Any],Any,None]:
        data = self.request(endpoint, method='GET', params=params, headers=headers, retries=retries)
        if isinstance(data, list):
            yield from iter(data)
        elif isinstance(data, dict) and self.iter_results_key in data and self.iter_next_key in data and isinstance(data[self.iter_results_key], list):
            while True:
                for result in data[self.iter_results_key]:
                    yield result

                next_url = data[self.iter_next_key]
                if not next_url:
                    break
                data = self.get(next_url)
        else:
            raise ApiClientError("Response data is not iterable", data, message_maxlen=self.error_message_maxlen)


    def get_list(self, endpoint: str, *, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None, retries: int|None = None) -> list[Any]:
        return [data for data in self.iter(endpoint, params=params, headers=headers, retries=retries)]


    def post(self, endpoint: str, data = None, *, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None, content_type: str|None = None, content_length: int|None = None, content_filename: str |None= None, retries: int|None = None) -> dict[str,Any]:
        result = self.request(endpoint, data, method='POST', params=params, headers=headers, content_type=content_type, content_length=content_length, content_filename=content_filename, retries=retries)
        if not isinstance(result, dict):
            raise ApiClientError("Response is not a dictionnary", result, message_maxlen=self.error_message_maxlen)
        return result
    

    def put(self, endpoint: str, data = None, *, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None, content_type: str|None = None, content_length: int|None = None, content_filename: str |None= None, retries: int|None = None) -> dict[str,Any]:
        result = self.request(endpoint, data, method='PUT', params=params, headers=headers, content_type=content_type, content_length=content_length, content_filename=content_filename, retries=retries)
        if not isinstance(result, dict):
            raise ApiClientError("Response is not a dictionnary", result, message_maxlen=self.error_message_maxlen)
        return result
   

    def request(self, endpoint: str, data = None, *, method = None, params: Mapping|None = None, headers: MutableMapping[str,str]|None = None, content_type: str|None = None, content_length: int|None = None, content_filename: str|None = None, retries: int|None = None) -> list[Any]|dict[str,Any]:
        url = self.prepare_url(endpoint, params=params)

        all_headers = self.get_request_headers(url)
        if headers:
            for key, value in headers.items():
                all_headers[key] = value
                if key == 'Content-Type' and not content_type:
                    content_type = value
                elif key == 'Content-Length' and content_length is None:
                    content_length = int(value) if isinstance(value, str) else value
                elif key == 'Content-Disposition' and not content_filename:
                    m = re.search(r'attachment\s*;\s*filename\s*=\s*(.+)', value)
                    if m:
                        content_filename = m[1].strip()

        if content_type:
            all_headers['Content-Type'] = content_type
        if content_length is not None:
            all_headers['Content-Length'] = str(content_length)
        if content_filename:
            all_headers['Content-Disposition'] = f"attachment; filename={content_filename}"
                
        if data is not None:
            if not method:
                method = 'POST'

            if isinstance(data, IOBase) or (content_type and not 'application/json' in content_type):
                # keep data as is: this is assumed to be an uploaded file
                if not content_type:
                    content_type = 'application/octet-stream'
            elif isinstance(data, str) and data.lstrip().startswith('{') and data.rstrip().endswith('}'):
                data = data.encode('utf-8') # already JSON encoded
            elif isinstance(data, bytes):
                pass # already JSON encoded
            else:
                data = json.dumps(data, ensure_ascii=False, cls=self.json_encoder_cls).encode('utf-8')
            
            self._logger.debug('%s %s', method, url)
            request = Request(url,
                method = method,
                headers = all_headers,
                data = data,
            )
        else:
            if not method:
                method = 'GET'
            
            self._logger.debug('%s %s', method, url)
            request = Request(url,
                method = method,
                headers = all_headers,
            )

        if retries is None:
            retries = self.default_retries

        try:
            response: HTTPResponse
            with urlopen(request, timeout=self.timeout, context=self._ssl_context) as response:
                if self._logger.isEnabledFor(logging.DEBUG):
                    response_content_length = response.length if response.length is not None else '-'
                    response_content_type = response.headers.get('Content-Type', '-')
                    self._logger.debug('%s %s %s %s', response.status, url, response_content_length, response_content_type)
                result = self._get_response_or_raise_error(response)
                self.handle_response_headers(url, response.headers, result)
                return result
        
        except HTTPError as error:
            with error:
                http_data = self._get_response_or_str_error(error)
            if error.code == HTTPStatus.NOT_FOUND.value:
                raise NotFound(_prepare_error_message(error, http_data, message_maxlen=self.error_message_maxlen)) from error
            else:
                raise ApiClientError(error, http_data, message_maxlen=self.error_message_maxlen) from error

        except Exception as error:
            if retries is not None and retries > 0 and (isinstance(error, URLError) and error.errno == 104) or isinstance(error, RemoteDisconnected):
                # Retry on:
                # - <urlopen error [Errno 104] Connection reset by peer>
                # - Remote end closed connection without response (http.client.RemoteDisconnected)
                self._logger.warning("Received %s at %s, retrying (%s more time)", _prepare_error_message(error, None, message_maxlen=self.error_message_maxlen), url, retries)
                return self.request(url, data, method=method, params=params, headers=headers, content_type=content_type, content_length=content_length, content_filename=content_filename, retries=retries-1) # type: ignore
            raise ApiClientError(error, message_maxlen=self.error_message_maxlen) from error


    def prepare_url(self, endpoint: str, *, params: Mapping|None = None):
        if '://' in endpoint or not self.base_url:
            url = endpoint            
        else:            
            if endpoint.startswith('/'):
                if self.base_url.endswith('/'):                    
                    endpoint = endpoint[1:]
            else:
                if not self.base_url.endswith('/') and endpoint:
                    endpoint = f'/{endpoint}'
            
            if self.force_trailing_slash and not endpoint.endswith('/'):
                endpoint = f'{endpoint}/'

            url = f'{self.base_url}{endpoint}'

        if params:
            url += "?" + urlencode(params)
        
        return url
    

    def get_endpoint(self, url: str):
        if not self.base_url:
            return url
        if url.startswith(self.base_url):
            url = url[len(self.base_url):]
        if not url.startswith('/'):
            url = f'/{url}'
        return url
    

    def get_request_headers(self, url: str) -> MutableMapping[str,str]:
        headers = {**self.default_headers}
        return headers


    def handle_response_headers(self, url: str, headers: HTTPMessage, result: list[Any]|dict[str,Any]):
        pass


    def _get_response_or_str_error(self, response: HTTPResponse|HTTPError) -> list[Any]|dict[str,Any]|str:
        result = self._decode_response(response)
        if isinstance(result, Exception):
            return str(result)
        return result


    def _get_response_or_raise_error(self, response: HTTPResponse|HTTPError) -> list[Any]|dict[str,Any]:
        result = self._decode_response(response)
        if isinstance(result, Exception):
            raise result from None        
        return result


    def _decode_response(self, response: HTTPResponse|HTTPError) -> list[Any]|dict[str,Any]|Exception:
        rawdata = response.read()
        try:
            strdata = rawdata.decode('utf-8')
        except UnicodeDecodeError:
            strdata = str(rawdata)
            return ApiClientError("Response is not valid UTF-8", strdata, message_maxlen=self.error_message_maxlen)
        
        try:
            result = json.loads(strdata, cls=self.json_decoder_cls)
        except json.JSONDecodeError:
            return ApiClientError("Response is not valid JSON", strdata, message_maxlen=self.error_message_maxlen)
        
        if not isinstance(result, (list,dict)):
            return ApiClientError("Response is not a dictionnary or a list", strdata, message_maxlen=self.error_message_maxlen)
        
        return result
        

class ApiClientError(Exception):
    def __init__(self, origin: str|Exception|None, data: list|dict|str|None = None, *, message_maxlen: int|None = 400):        
        self.nature: Literal['HTTP','URL','OS']|None
        self.code: int|None
        self.reason: str|None
        if isinstance(origin, HTTPError):
            self.nature = 'HTTP'
            self.code = origin.status
            self.reason = origin.reason
        elif isinstance(origin, URLError):
            self.nature = 'URL'
            self.code = origin.errno
            self.reason = str(origin.reason) if not isinstance(origin.reason, str) else origin.reason
        elif isinstance(origin, OSError):
            self.nature = 'OS'
            self.code = origin.errno
            self.reason = None
        else:            
            self.nature = None
            self.code = None
            self.reason = None

        self.message = _prepare_error_message(origin, data, message_maxlen=message_maxlen)
        self.origin = origin
        self.data = data

        super().__init__(self.message)


def _prepare_error_message(orig: str|Exception|None, data: list|dict|str|None = None, *, message_maxlen: int|None = 400):
    if isinstance(orig, HTTPError):
        message = f"[HTTP {orig.status}] {orig}"
    elif isinstance(orig, URLError):
        message = str(orig)
        if orig.errno and not 'errno' in message.lower():
            message = f"[Connection errno {orig.errno}] {orig}"
    elif isinstance(orig, Exception):
        message = str(orig)
        if not type(orig).__name__ in message:
            message = f"[{type(orig).__name__}] {orig}"
    elif isinstance(orig, str):
        message = orig
    else:
        message = ''

    if data:
        if isinstance(data, dict):
            for key, value in data.items():
                message = (message + '\n' if message else '') + f"{key}: {value}"
        else:
            message = (message + '\n' if message else '') + str(data)

    if message_maxlen is not None and len(message) > message_maxlen:
        message = message[0:message_maxlen] + '…'

    return message
