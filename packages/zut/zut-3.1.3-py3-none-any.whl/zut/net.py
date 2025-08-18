"""
Resolve network information (DNS resolution with a timeout, port status, system proxy, etc).
"""
from __future__ import annotations

import logging
import re
import socket
import struct
from http.client import HTTPResponse
from ipaddress import ip_address
from threading import Thread
from time import sleep, time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from zut import get_logger
from zut.polyfills import cached_property

_logger = get_logger(__name__)


#region Host and ports

def get_host_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def get_linux_default_gateway_ip(iface: str|None = None):
    with open("/proc/net/route") as fp:
        for line in fp:
            fields = line.strip().split()
            
            if iface and fields[0] != iface:
                continue

            if fields[1] != '00000000' or not int(fields[3], 16) & 2: # if not default route or not RTF_GATEWAY, skip it
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def resolve_host(host: str, *, timeout: float|None = None, ip_version: int|None = None) -> list[str]:
    """
    Make a DNS resolution with a timeout.
    """
    try:
        # If host is already an ip address, return it
        ip = ip_address(host)
        if not ip_version or ip.version == ip_version:
            return [ip.compressed]
    except ValueError:
        pass
    
    if ip_version is None:
        family = 0
    elif ip_version == 4:
        family = socket.AddressFamily.AF_INET
    elif ip_version == 6:
        family = socket.AddressFamily.AF_INET6
    else:
        raise ValueError(f"Invalid ip version: {ip_version}")

    addresses = []
    exception = None

    def target():
        nonlocal addresses, exception
        try:
            for af, socktype, proto, canonname, sa in socket.getaddrinfo(host, port=0, family=family):
                addresses.append(sa[0])
        except BaseException as err:
            exception = err

    if timeout is not None:
        thread = Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        if thread.is_alive():
            raise TimeoutError(f"Name resolution for host \"{host}\" timed out")

    else:
        target()

    if exception:
        err = NameError(str(exception))
        err.name = host
        raise err
        
    return addresses

def check_port(hostport: str|tuple[str,int]|list[str|tuple[str,int]], port: int|None = None, *, timeout: float|None = None) -> tuple[str,int]|None:
    """
    Check whether at least one of the given host and port is open.

    If yes, return the first open (host, port). Otherwise return None.
    """
    if port is not None:
        if not isinstance(port, int):
            raise TypeError(f"port: {type(port).__name__}")
        
    def normalize_hostport(value) -> tuple[str, int]:
        if isinstance(value, str):
            m = re.match(r'^(.+):(\d+)$', value)
            if m:
                return (m[1], int(m[2]))
            elif port is not None:
                return (value, port)
            else:
                raise TypeError(f"Port required for host {host}")
        elif isinstance(value, tuple):
            return value
        else:
            raise TypeError(f"hostport: {type(value).__name__}")

    if isinstance(hostport, (str,tuple)):
        hostports = [normalize_hostport(hostport)]
    elif isinstance(hostport, list):
        hostports = [normalize_hostport(value) for value in hostport]
    else:
        raise TypeError(f"hostport: {type(hostport).__name__}")

    open_list: list[tuple[str,int]] = []

    def target(host: str, port: int):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            if result == 0:
                _logger.debug("Host %s, port %s: open", host, port)
                open_list.append((host, port))
            else:
                _logger.debug("Host %s, port %s: not open", host, port)
        except Exception as err:
            _logger.debug("Host %s, port %s: %s", host, port, err)
        finally:
            if sock:
                sock.close()

    threads: list[Thread] = []
    for host, port in hostports:
        thread = Thread(target=target, args=[host, port], daemon=True)
        thread.start()
        threads.append(thread)

    # Wait for all threads
    if timeout is not None:
        stop_time = time() + timeout
        while time() < stop_time:
            if any(t.is_alive() for t in threads):
                sleep(0.1)
            else:
                break
    else:
        for thread in threads:
            thread.join()

    # Return
    if open_list:
        return open_list[0]
    else:
        return None

#endregion


#region WPAD

def get_wpad_proxy_url(*, timeout: float = 1.0) -> str|None:
    wpad = get_wpad_config(timeout=timeout)
    return wpad.proxy_url if wpad else None


_default_wpad: WPADConfig|None = None
_default_wpad_requested = False

def get_wpad_config(host: str = 'wpad', *, timeout: float = 1.0) -> WPADConfig|None:
    global _default_wpad, _default_wpad_requested
    if host == 'wpad' and _default_wpad_requested:
        return _default_wpad

    # Determine actual URL and host
    if '://' in host:
        url = host
        parts = urlparse(url)
        if not parts.hostname:
            raise ValueError(f"Invalid URL: {url}")
        host = parts.hostname
    else:
        url = f"http://{host}/wpad.dat"

    # Try to connect to WPAD (allow to avoid unavalability of timeout when resolving hostname)
    if not check_port(host, 80, timeout=timeout):
        if host == 'wpad':
            _default_wpad_requested = True
        return None

    # Request WPAD url    
    request = Request(url)
    response: HTTPResponse
    try:
        with urlopen(request, timeout=timeout) as response:
            _logger.debug("WPAD response: %s %s - Content-Type: %s", response.status, response.reason, response.headers.get('Content-Type'))
            body = response.read().decode('utf-8')
    except HTTPError as err:
        _logger.error(f"Cannot retrieve WPAD: HTTP {err.status} {err.reason}")
        if host == 'wpad':
            _default_wpad_requested = True
        return None
    except URLError as err:
        _logger.log(logging.DEBUG if err.errno == 5 else logging.ERROR,f"Cannot retrieve WPAD: {err.reason}")
        if host == 'wpad':
            _default_wpad_requested = True
        return None
    
    no_proxy = []

    def append_domain(domain: str):
        no_proxy.append(domain)

    def append_urlpattern(pattern: str):
        m = re.match(r'^https?://([^/]+)/\*$', pattern)
        if m:
            append_domain(m[1])
        else:
            _logger.warning(f"Ignore unknown URL pattern \"{pattern}\" in WPAD response")
    
    def append_net(network: str, mask: str):
        if network == '127.0.0.1':
            no_proxy.append('127.*')
            return
        
        if network == '172.16.0.0' and mask == '255.240.0.0':
            for i in range(16, 32):
                no_proxy.append(f'172.{i}.*')
            return
        
        if mask == '255.255.255.255':
            no_proxy.append(network)
            return
        
        asterisk_start = None
        if mask == '255.0.0.0':
            asterisk_start = 1
        elif mask == '255.255.0.0':
            asterisk_start = 2
        elif mask == '255.255.255.0':
            asterisk_start = 3

        if asterisk_start is not None:
            parts = network.split('.')
            if len(parts) == 4:
                no_proxy.append('.'.join(parts[0:asterisk_start]) + '.*')
                return

        _logger.warning(f"Ignore network with specific mask \"{network}/{mask}\" in WPAD response")
    
    proxy_host = None
    proxy_port = None
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith('//') or line in {'{', '}', 'function FindProxyForURL(url, host)'}:
            continue

        m = re.match(r'^return "PROXY\s*([^\s"\:]+)\:(\d+)";$', line, re.IGNORECASE)
        if m:
            proxy_host = m[1]
            proxy_port = int(m[2])
        else:
            m = re.match(r'^if \(isInNet\(host, "(?P<network>[^"]+)", "(?P<mask>[^"]+)"\)\) \{return "DIRECT";\}$', line, re.IGNORECASE)
            if m:
                append_net(m['network'], m['mask'])
            else:
                m = re.match(r'^if \((?P<function>[a-z]+)\((?:host|url), "(?P<value>[^"]+)"\)\) \{return "DIRECT";\}$', line, re.IGNORECASE)
                if m:
                    if m['function'] == 'dnsDomainIs':
                        append_domain(m['value'])
                    elif m['function'] == 'shExpMatch':
                        append_urlpattern(m['value'])
                    else:
                        _logger.warning(f"Ignore line with unknown function \"{m['function']}\" in WPAD response: {line}")
                else:
                    _logger.warning(f"Ignore unexpected line in WPAD response: {line}")

    wpad = WPADConfig(proxy_host, proxy_port, ','.join(no_proxy))
    if host == 'wpad':
        _default_wpad = wpad
        _default_wpad_requested = True
    return wpad


class WPADConfig:
    def __init__(self, proxy_host: str|None = None, proxy_port: int|None = None, noproxy: str|None = None):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.no_proxy = noproxy

    @cached_property
    def proxy_url(self) -> str|None:
        if not self.proxy_host:
            return None
        return f"http://{self.proxy_host}:{self.proxy_port}"

    @cached_property
    def proxy_domain(self) -> str|None:
        if not self.proxy_host:
            return None

        m = re.match(r'^[^\.]+\.(.+)$', self.proxy_host)
        if m:
            return m[1]
        else:
            return None

#endregion
