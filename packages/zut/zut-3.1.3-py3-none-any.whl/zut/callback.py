"""
HTTP callback server (for redirects of authorization flows).
"""
from __future__ import annotations

import inspect
import logging
from functools import cached_property
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer, ThreadingMixIn
from typing import Any, Callable, TypeVar
from urllib.parse import parse_qs, urlparse


class CallbackServer(ThreadingMixIn, TCPServer):
    """
    A temporary HTTP server launched to wait callback GET request (typically used for redirects of authorization flows).
    """
    def __init__(self, callback_function: Callable[[CallbackRequest],Any]|Callable[[],Any], callback_path: str|None = None, *, listening_address: str='127.0.0.1', listening_port: int = 0):
        """
        :param callback_function: The callback function to be called when a GET request is received.
            The function may have a `CallbackRequest` argument if it needs to analyze the received request.
            The callback server is interrupted after the callback function has finished running, except if it raised an exception.
            If the exception raised contains a `code` attribute between 400 and 599, it is used as the HTTP return code. If it contains a `reason` attribute, it is used as the HTTP response text.
        :param callback_path: If set, the callback function will be called only for the given path.
        """
        super().__init__((listening_address, listening_port), self._Handler)
        self._logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__qualname__}')
        self.callback_function = callback_function
        self.callback_path = callback_path
        self.base_url = f"http://{self.server_address[0]}:{self.server_address[1]}"
        self._callback_function_has_parameter = True if inspect.signature(self.callback_function).parameters else False

    def run(self):
        with self:
            self._logger.info("Callback server listening on %s (press CTRL+C, possibly multiple times, to exit)", self.base_url)
            try:
                self.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                self._logger.debug("Closing callback server listening on %s", self.base_url)
                self.server_close() # Must be called after server_forever() to close the listening socket - See https://stackoverflow.com/a/35576127


    class _Handler(BaseHTTPRequestHandler):
        """
        Instanciated once for each request.
        """  
        server: CallbackServer # pyright: ignore[reportIncompatibleVariableOverride]
        
        def do_GET(self):
            info = CallbackRequest(self)
            if self.server.callback_path is not None and info.path != self.server.callback_path:
                self._respond(HTTPStatus.BAD_REQUEST)
                return

            try:
                if self.server._callback_function_has_parameter:
                    self.server.callback_function(info) # type: ignore
                else:
                    self.server.callback_function() # type: ignore
            except Exception as err:
                self.server._logger.exception("An error occurred while running the callback function")
                code = getattr(err, 'code', None)
                reason = getattr(err, 'reason', None)
                if not isinstance(code, int) or not (code >= 400 and code <= 599):
                    code = HTTPStatus.INTERNAL_SERVER_ERROR.value
                if not isinstance(reason, str) or reason.strip() == '':
                    reason = "An error occured."
                self._respond(code, reason)
                return

            self._respond(200, "OK. You may close this window.")
            self.server.shutdown()

        def _respond(self, code: int|HTTPStatus, message: str|None = None):
            if isinstance(code, HTTPStatus):
                reason = code.phrase
                code = code.value
            else:
                try:
                    status = HTTPStatus(code)
                except ValueError:
                    status = HTTPStatus.INTERNAL_SERVER_ERROR
                code = status.value
                reason = status.phrase
            
            self.send_response(code, reason)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            if not message:
                message = reason
            self.wfile.write(message.encode(encoding='utf-8'))


T = TypeVar('T')

class CallbackRequest:
    def __init__(self, handler):
        self.server: CallbackServer = handler.server
        self.url = f"{self.server.base_url}{handler.path}"

    @cached_property
    def parsed_url(self):
        return urlparse(self.url)

    @cached_property
    def parsed_query(self):
        return parse_qs(self.parsed_url.query)

    @cached_property
    def path(self):
        return self.parsed_url.path
    
    def get(self, name: str, default: T = None) -> str|T:
        values = self.parsed_query.get(name, None)
        if values is None or len(values) == 0:
            return default
        return values[-1]
