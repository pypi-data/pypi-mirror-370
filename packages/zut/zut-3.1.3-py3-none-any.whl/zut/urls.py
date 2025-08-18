"""
Build URLs.
"""
from __future__ import annotations

import re
from ipaddress import AddressValueError, IPv4Address, IPv6Address
from typing import Mapping, Sequence
from urllib.parse import ParseResult, quote, quote_plus, unquote, urlencode, urlparse, urlunparse

from zut import DelayedStr


def build_url(result: ParseResult|None = None, *, scheme: str = '', hostname: str|IPv4Address|IPv6Address|None = None, port: int|str|None = None, username: str|None = None, password: str|DelayedStr|None = None, path: str|None = None, params: str|None = None, query: Mapping|Sequence|str|None = None, fragment: str|None = None, noquote = False, hide_password = False):
    if result:
        if scheme == '' and result.scheme:
            scheme = result.scheme
        if hostname is None and result.hostname is not None:
            hostname = unquote(result.hostname)
        if port is None and result.port is not None:
            port = result.port
        if username is None and result.username is not None:
            username = unquote(result.username)
        if password is None and result.password is not None:
            password = unquote(result.password)
        if path is None and result.path is not None:
            path = unquote(result.path)
        if params is None and result.params is not None:
            params = unquote(result.params)
        if query is None and result.query is not None:
            query = unquote(result.query)
        if fragment is None and result.fragment is not None:
            fragment = unquote(result.fragment)

    netloc = build_netloc(hostname=hostname, port=port, username=username, password=password, noquote=noquote, hide_password=hide_password)

    if isinstance(query, str):
        actual_query = query if noquote else quote_plus(query or '')
    if isinstance(query, Mapping):
        actual_query = urlencode(query)
    elif isinstance(query, Sequence):
        named_parts = []
        unnamed_parts = []
        for part in query:
            if isinstance(part, tuple):
                named_parts.append(part)
            else:
                unnamed_parts.append(part)
        actual_query = urlencode(named_parts, quote_via=quote_plus)
        actual_query += ('&' if actual_query else '') + '&'.join(quote_plus(part) for part in unnamed_parts)
    else:
        actual_query = None

    return urlunparse((
        scheme or '',
        netloc or '',
        (path or '') if noquote else quote(path or ''),
        (params or '') if noquote else quote_plus(params or ''),
        actual_query,
        (fragment or '') if noquote else quote_plus(fragment or ''))
    )


def build_netloc(*, hostname: str|IPv4Address|IPv6Address|None = None, port: int|str|None = None, username: str|None = None, password: str|DelayedStr|None = None, noquote = False, hide_password = False):
    netloc = ''
    if username or hostname:
        if username:
            netloc += username if noquote else quote_plus(username)
            password = DelayedStr.ensure_value(password)
            if password:
                if hide_password:
                    password = '***'
                else:
                    if not noquote:
                        password = quote_plus(password) # type: ignore
                netloc += f':{password}'
            netloc += '@'

        if hostname:
            if isinstance(hostname, IPv4Address):
                netloc += hostname.compressed
            elif isinstance(hostname, IPv6Address):
                netloc += f"[{hostname.compressed}]"
            else:
                ipv6 = None
                if ':' in hostname:
                    try:
                        ipv6 = IPv6Address(hostname)
                    except AddressValueError:
                        pass

                if ipv6:
                    netloc += f"[{ipv6.compressed}]"
                else:
                    netloc += hostname if noquote else quote_plus(hostname)

            if port:
                if not (isinstance(port, int) or (isinstance(port, str) and re.match(r'^\d+$', port))):
                    raise ValueError(f"invalid type for port: {type(port)}")
                netloc += f':{port}'
    elif port:
        raise ValueError("Argument 'port' cannot be given without a hostname")
    elif password:
        raise ValueError("Argument 'password' cannot be given without a username")

    return netloc


def hide_url_password(url: str, *, always_password = False):
    r = urlparse(url)
    password = r.password
    if not password and always_password:
        password = '***'
    return build_url(scheme=r.scheme, hostname=r.hostname, port=r.port, username=r.username, password=password, path=r.path, params=r.params, query=r.query, fragment=r.fragment, noquote=True, hide_password=True)
