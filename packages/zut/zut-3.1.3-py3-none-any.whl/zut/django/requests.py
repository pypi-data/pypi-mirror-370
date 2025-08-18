from __future__ import annotations

import re

from django.http import HttpRequest


def get_request_ip(request: HttpRequest) -> str|None:
    """
    Get the client IP address.

    Make sure you have reverse proxy (if any) configured correctly (e.g. mod_rpaf installed for Apache).

    See: https://stackoverflow.com/a/4581997
    """
    x_forwarded_for: str|None = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')


def get_request_country(request: HttpRequest) -> str|None:
    """
    Guess the client country code, from its IP address, or from its Accept-Language header.

    Requires geoip2.
    """
    ip = get_request_ip(request)
    if ip:
        country_code = get_ip_country(ip)
        if country_code:
            return country_code

    if 'Accept-Language' in request.headers:
        selected_country_code = None
        selected_priority = None
        for lang in request.headers['Accept-Language'].split(','):
            m = re.match(r'^[a-z]{2}\-([A-Z]{2})(?:;q=([0-9\.]+))?$', lang, re.IGNORECASE)
            if m:
                country_code = m[1].upper()
                priority = float(m[2] or 1)
                if selected_priority is None or priority > selected_priority:
                    selected_country_code = country_code
                    selected_priority = priority

        return selected_country_code


def get_ip_country(ip: str) -> str|None:
    """
    Get the country code for an IP address. Returns None if unknown.

    Requires geoip2.
    """
    from django.contrib.gis.geoip2 import GeoIP2
    from geoip2.errors import AddressNotFoundError  # type: ignore

    g = GeoIP2()
    try:
        result = g.country(ip)
        return result['country_code']
    except AddressNotFoundError:
        return None
