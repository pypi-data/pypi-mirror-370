"""
Parse and convert timezones.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone, tzinfo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal

# ZoneInfo: introduced in Python 3.9
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None
    

_local_tz: tzinfo|None = None
_dst_dt = datetime(datetime.now().year, 8, 1)

def _is_local_tz_spec(tz: tzinfo|str|None):
    return tz is None or tz == 'local' or tz == 'localtime'

def parse_tz(tz: tzinfo|Literal['local','utc']|str|None = 'local') -> tzinfo:
    if _is_local_tz_spec(tz):
        return get_local_tz()
    elif isinstance(tz, tzinfo):
        return tz
    elif tz == 'utc' or tz == 'UTC':
        return timezone.utc
    elif isinstance(tz, str):
        if not ZoneInfo:
            # pytz: used to parse timezones on Python < 3.9 (no ZoneInfo available)
            try:
                import pytz  # type: ignore
            except ModuleNotFoundError:
                raise ModuleNotFoundError(f"Module 'pytz' is required on Python < 3.9 to parse timezones from strings") from None
            return pytz.timezone(tz)
        if sys.platform == 'win32':
            # tzdata: used to parse timezones from strings through ZoneInfo on Windows (Windows does not maintain a database of timezones)
            try:
                import tzdata
            except ModuleNotFoundError:
                raise ModuleNotFoundError(f"Module 'tzdata' is required on Windows to parse timezones from strings") from None
        return ZoneInfo(tz)
    else:
        raise TypeError(f"Invalid timezone type: {tz} ({type(tz).__name__})")


def get_local_tz() -> tzinfo:
    global _local_tz

    if _local_tz is None:
        if not ZoneInfo or sys.platform == 'win32':
            # tzlocal: used to parse timezones from strings on Windows (Windows does not maintain a database of timezones and `tzdata` only is not enough)
            try:
                import tzlocal  # type: ignore
            except ModuleNotFoundError:
                raise ModuleNotFoundError(f"Module 'tzlocal' is required on Windows or on Python < 3.9 to retrieve local timezone") from None
            tz: tzinfo = tzlocal.get_localzone()
            _local_tz = tz
        else:
            _local_tz = ZoneInfo('localtime')
    
    return _local_tz


def get_tz_key(tz: tzinfo|Literal['local','utc']|None = 'local') -> str:
    if not isinstance(tz, tzinfo):
        tz = parse_tz(tz)
    key = getattr(tz, 'key', None)
    if key:
        return key
    raise ValueError(f"{type(tz).__name__} object has no key")


def is_local_tz(tz: tzinfo) -> bool:
    local_tz = get_local_tz()
    return tz == local_tz or (tz.utcoffset(_dst_dt) == local_tz.utcoffset(_dst_dt) and tz.dst(_dst_dt) == local_tz.dst(_dst_dt))


def is_utc_tz(tz: tzinfo) -> bool:
    utc_tz = timezone.utc
    return tz == utc_tz or (tz.utcoffset(_dst_dt) == utc_tz.utcoffset(_dst_dt) and tz.dst(_dst_dt) == utc_tz.dst(_dst_dt))


def make_aware(value: datetime, tz: tzinfo|Literal['local','utc']|str|None = 'local') -> datetime:
    """
    Make a naive datetime aware in the given timezone (use `tz='local'` for the system local timezone or `tz='utc' for UTC`).
    """
    if value is None:
        return None
    
    if value.tzinfo:
        raise ValueError(f"Datetime is already aware: {value.tzinfo}")
    
    if not isinstance(tz, tzinfo):
        tz = parse_tz(tz)
    
    if hasattr(tz, 'localize'):
        # See: https://stackoverflow.com/a/6411149
        return tz.localize(value) # type: ignore
    else:
        return value.replace(tzinfo=tz)


def make_naive(value: datetime, tz: tzinfo|Literal['local','utc']|str|None = 'local') -> datetime:
    """
    Make an aware datetime naive in the given timezone (use `tz='local'` for the system local timezone or `tz='utc' for UTC`).
    """
    if value is None:
        return None

    if not value.tzinfo:
        raise ValueError(f"Datetime is already naive: {value}")
    
    if value.year >= 2999: # avoid astimezone() issue for conversion of datetimes such as 9999-12-31 23:59:59.999999+00:00 or 4000-01-02 23:00:00+00:00
        return value.replace(tzinfo=None)
    
    value = value.astimezone(None if _is_local_tz_spec(tz) else parse_tz(tz))
    return value.replace(tzinfo=None)


def now_aware(tz: tzinfo|Literal['local','utc']|str|None = 'local', *, no_microseconds = False):
    """
    Get the current aware datetime in the given timezone (use `tz='local'` for the system local timezone or `tz='utc' for UTC`).
    """
    now = datetime.now().astimezone(None if _is_local_tz_spec(tz) else parse_tz(tz))
    if no_microseconds:
        now = now.replace(microsecond=0)
    return now


def now_naive(tz: tzinfo|Literal['local','utc']|str|None = 'local', *, no_microseconds = False):
    """
    Get the current naive datetime in the given timezone (use `tz='local'` for the system local timezone or `tz='utc' for UTC`).
    """
    if _is_local_tz_spec(tz):
        now = datetime.now()
    else:
        tz = parse_tz(tz)
        now = datetime.now(tz=tz).replace(tzinfo=None)

    if no_microseconds:
        now = now.replace(microsecond=0)
    return now
