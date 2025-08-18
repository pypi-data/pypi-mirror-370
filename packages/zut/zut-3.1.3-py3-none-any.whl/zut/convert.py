"""
Flexible convert functions.
"""
from __future__ import annotations

import inspect
import json
import re
import sys
import unicodedata
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Callable, Iterable, Mapping, Sequence, Set, TypeVar

if TYPE_CHECKING:
    from typing import Literal

from zut import NotImplementedBy, NotSupportedBy

T = TypeVar('T')


#region Protocols

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    Protocol = object


class GoogleMoney(Protocol):
    """
    Represents an amount of money with its currency type, as defined by Google.
    
    See https://developers.google.com/actions-center/verticals/things-to-do/reference/feed-spec/google-types?hl=fr#googletypemoney_definition
    """

    currency_code: str
    """ 3-letter currency code defined in ISO 4217. """

    units: int|float
    """ Number of units of the amount (should be integers but float are accepted). """

    nanos: int
    """ Number of nano (10^-9) units of the amount. """

#endregion


#region From strings (mostly) to misc.
    
def parse_bool(value: bool|str) -> bool:
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise TypeError(f"value: {type(value.__name__)}")

    lower = value.lower()
    # same rules as RawConfigParser.BOOLEAN_STATES
    if lower in {'1', 'yes', 'true', 'on'}:
        return True
    elif lower in {'0', 'no', 'false', 'off'}:
        return False
    else:
        raise ValueError('Not a boolean: %s' % lower)


def parse_datetime(value: str|date, *, use_locale = False) -> datetime:
    if isinstance(value, datetime):
        raise TypeError(f"value: {type(value).__name__}")  # a datetime is also a date so we need it here (before checking for date) to avoid transforming datetimes by mistake
    elif isinstance(value, date):
        return datetime(value.year, value.month, value.day, 0)
    elif not isinstance(value, str):
        raise TypeError(f"value: {type(value).__name__}")
    
    if 'T' in value: # ISO separator between date and time
        return datetime.fromisoformat(value)
    
    
    pos = value.rfind(' ')
    if pos == -1:
        pos = len(value)

    datepart = value[0:pos]
    timepart = value[pos+1:]

    d = parse_date(datepart, use_locale=use_locale)
    if not d:
        raise ValueError(f"Invalid date in {value}")

    value = d.isoformat() + ' ' + (timepart if timepart else '00:00:00')
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f %z') # format not accepted by fromisoformat (contrary to other non-ISO but still frequent "%Y-%m-%d %H:%M:%S.%f")


def parse_month(text: str|int) -> int:
    if isinstance(text, int):
        return text
    elif re.match(r'^\d+$', text):
        return int(text)
    
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    if norm.startswith(('jan',)):
        return 1
    elif norm.startswith(('feb','fev')):
        return 2
    elif norm.startswith(('mar',)):
        return 3
    elif norm.startswith(('apr','avr')):
        return 4
    elif norm.startswith(('may','mai')):
        return 5
    elif norm.startswith(('jun','juin')):
        return 6
    elif norm.startswith(('jul','juil')):
        return 7
    elif norm.startswith(('aug','aou')):
        return 8
    elif norm.startswith(('sep')):
        return 9
    elif norm.startswith(('oct',)):
        return 10
    elif norm.startswith(('nov',)):
        return 11
    elif norm.startswith(('dec',)):
        return 12
    else:
        raise ValueError(f"Unknown month: {text}")


def parse_date(value: str|datetime, *, use_locale = False) -> date:
    if isinstance(value, datetime):
        return value.date()
    elif isinstance(value, date):
        return value
    elif not isinstance(value, str):
        raise TypeError(f"value: {type(value).__name__}")
    
    m = re.match(r'^(?P<val1>\d{1,4}|[a-z]{3,4})(?P<sep1>[/\.\-])(?P<val2>\d{1,2}|[a-z]{3,4})(?P<sep2>[/\.\-])(?P<val3>\d{1,4}|[a-z]{3,4})$', value)
    if not m or m['sep1'] != m['sep2']:
        raise ValueError(f"Invalid date string: {value}")
    
    vals = [m['val1'], m['val2'], m['val3']]

    if m['sep1'] == '-':
        return date(int(vals[0]), parse_month(vals[1]), int(vals[2]))
    elif m['sep1'] == '.':
        return date(int(vals[2]), parse_month(vals[1]), int(vals[0]))
    
    years: list[int] = []
    months: list[int] = []
    months_from_str: list[int] = []
    days: list[int] = []
    for val in vals:
        ival = parse_month(val)
        if ival <= 12:
            (months if re.match(r'^\d+$', val) else months_from_str).append(ival)
        elif ival <= 31:
            days.append(ival)
        else:
            years.append(ival)

    if any(months_from_str):
        days += months
        months = months_from_str
    
    if len(years) == 1 and len(months) == 1 and len(days) == 1:
        return date(years[0], months[0], days[0])

    ldf = None        
    if use_locale:
        from zut.config import get_locale_date_format
        ldf = get_locale_date_format()
    
    if not ldf:
        raise ValueError(f"Ambiguous date string: {value}")
    
    fmt = re.sub(r'[^ymd]', '', ldf.lower())
    
    if len(fmt) == 3:
        y_index = fmt.rfind('y')
        m_index = fmt.rfind('m')
        d_index = fmt.rfind('d')
        if y_index >= 0 and m_index >= 0 and d_index >= 0:
            return date(int(vals[y_index]), int(vals[m_index]), int(vals[d_index]))
    
    raise ValueError(f"Unexpected locale date format: {fmt}")


def parse_float(value: str|GoogleMoney, *, decimal_separator: Literal['.',',','detect'] = '.') -> float:
    if isinstance(value, str):
        return float(_handle_decimal_str(value, decimal_separator))
    elif hasattr(value, 'units') and hasattr(value, 'nanos'): # GoogleMoney
        return float(getattr(value, 'units') + getattr(value, 'nanos') / 1E9)
    else:
        raise TypeError(f"value: {type(value).__name__}")


def parse_decimal(value: Decimal|str|float|GoogleMoney, *, max_decimals: int|None = None, reduce_decimals:int|Sequence[int]|bool = False, decimal_separator: Literal['.',',','detect'] = '.') -> Decimal:
    """
    Parse a Decimal value.

    :param value:               The value to convert.
    :param max_decimals:        Maximal number of decimal digits to use (the value will be rounded if necessary).
    :param reduce_decimals:     If set, reduce the number of decimal digits to the given number if this can be done without rounding (if set to True, try to reduce to 2 digits, otherwise to 5).
    :param decimal_separator:   Indicate if `.` or `,` is used as decimal separator, or `detect` to detect it (use with caution: might introduce errors if the values can have thousands separators).
    """
    decimal_value: Decimal
    if isinstance(value, Decimal):
        decimal_value = value
    elif isinstance(value, (float,int)):
        decimal_value = Decimal(value)
    elif isinstance(value, str):
        decimal_value = Decimal(_handle_decimal_str(value, decimal_separator))
    elif hasattr(value, 'units') and hasattr(value, 'nanos'): # GoogleMoney
        decimal_value = Decimal(getattr(value, 'units') + getattr(value, 'nanos') / 1E9)
        if max_decimals is None:
            max_decimals = 9
    else:
        raise TypeError(f"value: {type(value).__name__}")

    if max_decimals is not None:
        decimal_value = round(decimal_value, max_decimals)

    if reduce_decimals is False or reduce_decimals is None:
        lower_boundaries = []
    elif reduce_decimals is True:
        lower_boundaries = [2, 5]
    elif isinstance(reduce_decimals, int):
        lower_boundaries = [reduce_decimals]
    elif isinstance(reduce_decimals, Sequence):
        lower_boundaries = sorted(reduce_decimals)
    else:
        raise TypeError(f"reduce_decimals: {type(reduce_decimals).__name__}")
    
    for boundary in lower_boundaries:
        expo = decimal_value * 10 ** boundary
        remaining = expo - int(expo)
        if remaining == 0:
            return round(decimal_value, boundary)
    
    return decimal_value


def _handle_decimal_str(value: str, decimal_separator: Literal['.',',','detect']):
    # Remove spaces and non-break spaces that may be used as thousands separators
    value = re.sub(r'[ \u00A0\u202F]', '', value)

    if decimal_separator == 'detect':
        comma_rfind = value.rfind(',')
        dot_rfind = value.rfind('.')

        if dot_rfind >= 0 and comma_rfind > dot_rfind: # comma after dot
            return _remove_thousand_separator(value, '.').replace(',', '.')

        elif comma_rfind >= 0 and dot_rfind > comma_rfind: # dot after comma
            return _remove_thousand_separator(value, ',')

        elif comma_rfind >= 0: # comma only
            if not _check_thousand_separator(value, ','):
                return value.replace(',', '.')

        elif dot_rfind >= 0: # dot only
            if not _check_thousand_separator(value, '.'):
                return value

        else: # no comma or dot (no need to make a conversion)
            return value
        
        # Here, there is only one comma or one dot, and it may be a thousand separator (or a decimal separator)
        # => we rely on the locale configuration to determine what is the decimal separator
        from zut.config import get_locale_decimal_separator
        if get_locale_decimal_separator() == ',':
            return value.replace(',', '.')
        else:
            return value
    
    elif decimal_separator == '.':
        return _remove_thousand_separator(value, ',')
    else:
        return _remove_thousand_separator(value, '.').replace(decimal_separator, '.')


def _remove_thousand_separator(text: str, thousand_separator: str):
    """
    Return `text` with `thousand_separator` removed if it actually is compatible with a thousands separator. Otherwise a `ValueError` is raised.
    """
    if _check_thousand_separator(text, thousand_separator):
        return text.replace(thousand_separator, '')
    else:
        raise ValueError(f"Invalid thousands separator `{thousand_separator}` in `{text}`")


def _check_thousand_separator(text: str, thousand_separator: str):
    """
    Determine if the given separator may be a thousands separator of the text.
    """
    decimal_separator = '.' if thousand_separator == ',' else ','
    decimal_separator_pos = text.rfind(decimal_separator)

    group_i = 0
    at_least_one_separator = False
    for char in reversed(text[0:decimal_separator_pos] if decimal_separator_pos >= 0 else text):
        if group_i < 3:
            if not char.isdigit():
                return False
            group_i += 1
        else: # group_i == 3
            if char != thousand_separator:
                return False
            at_least_one_separator = True
            group_i = 0 # next group will start

    return at_least_one_separator


def parse_list(value: str|list, *, separator='|') -> list[str]:
    if isinstance(value, list):
        return value
    elif not isinstance(value, str):
        raise TypeError(f"value: {type(value).__name__}")
    
    value = value.strip()
    if value == '':
        return []

    # Assume format depending on first character
    if value.startswith('{'):
        return parse_pg_array(value)
    elif value.startswith('['):
        return json.loads(value)
    else:
        return [element.strip() for element in value.split(separator)]


def parse_dict(value: str, *, separator='|') -> dict[str,str|Literal[True]]:
    if value is None:
        return None
    elif isinstance(value, dict):
        return value
    elif not isinstance(value, str):
        raise TypeError(f"value: {type(value.__name__)}")
    
    value = value.strip()
    if value == '':
        raise ValueError("Invalid dict value: empty string")

    # Assume format depending on first character
    if value.startswith('{'):
        return json.loads(value)
    else:
        result: dict[str,str|Literal[True]] = {}
        for element in value.split(separator):
            element = element.strip()
            try:
                pos = element.index('=')
                key = element[:pos].strip()
                result[key] = element[pos+1:].strip()
            except ValueError:
                key = element
                result[key] = True
        return result


def parse_func_parameters(func: Callable, *args: str):
    """
    Convert `args` (list of strings typically comming from the command line) into typed args and kwargs for `func`.
    """
    if not args:
        return tuple(), dict()
    
    # Determine argument types
    signature = inspect.signature(func)
    var_positional_type = None
    var_keyword_type = None
    parameter_types = {}
    positional_types = []
    for parameter in signature.parameters.values():
        parameter_type = None if parameter.annotation is inspect.Parameter.empty else parameter.annotation
        if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
            var_positional_type = parameter_type
        elif parameter.kind == inspect.Parameter.VAR_KEYWORD:
            var_keyword_type = parameter_type
        else:
            parameter_types[parameter.name] = parameter_type
            if parameter.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
                positional_types.append(parameter_type)
    
    # Distinguish args and kwargs
    positionnal_args = []
    keyword_args = {}
    for arg in args:
        m = re.match(r'^([a-z0-9_]+)=(.+)$', arg)
        if m:
            keyword_args[m[1]] = m[2]
        else:
            positionnal_args.append(arg)

    # Convert kwargs
    for parameter, value in keyword_args.items():
        if parameter in parameter_types:
            target_type = parameter_types[parameter]
            if target_type:
                value = convert(value, target_type)
                keyword_args[parameter] = value

        elif var_keyword_type:
            keyword_args[parameter] = convert(value, var_keyword_type)

    # Convert args
    for i, value in enumerate(positionnal_args):
        if i < len(positional_types):
            target_type = positional_types[i]
            if target_type:
                positionnal_args[i] = convert(value, target_type)

        elif var_positional_type:
            positionnal_args[i] = convert(value, var_positional_type)

    return tuple(positionnal_args), keyword_args


def parse_pg_array(value: str) -> list[str]:
    """ Parse an array literal (using PostgreSQL syntax) into a list. """
    # See: https://www.postgresql.org/docs/current/arrays.html#ARRAYS-INPUT
    if not isinstance(value, str):
        raise TypeError(f"value: {type(value.__name__)}")

    if len(value) == 0:
        raise ValueError(f"Invalid postgresql array literal: empty string")
    elif value[0] != '{' or value[-1] != '}':
        raise ValueError(f"Invalid postgresql array literal '{value}': does not start with '{{' and end with '}}'")
        
    def split(text: str):
        pos = 0

        def get_quoted_part(start_pos: int):
            nonlocal pos
            pos = start_pos
            while True:
                try:
                    next_pos = text.index('"', pos + 1)
                except ValueError:
                    raise ValueError(f"Unclosed quote from position {pos}: {text[pos:]}")
                
                pos = next_pos
                if text[pos - 1] == '\\' and (pos <= 2 or text[pos - 2] != '\\'): # escaped quote
                    pos += 1 # will search next quote
                else:
                    value = text[start_pos+1:pos]
                    pos += 1
                    if pos == len(text): # end
                        pass
                    else:
                        if text[pos] != ',':
                            raise ValueError(f"Quoted part \"{value}\" is followed by \"{text[pos]}\", expected a comma")
                        pos += 1
                    return value

        def get_unquoted_part(start_pos: int):
            nonlocal pos
            try:
                pos = text.index(',', start_pos)
                value = text[start_pos:pos]
                pos += 1
            except ValueError:
                pos = len(text) # end
                value = text[start_pos:]

            if value.lower() == 'null':
                return None
            return value

        def unescape(part: str|None):
            if part is None:
                return part
            return part.replace('\\"', '"').replace('\\\\', '\\')
        
        parts: list[str] = []
        while pos < len(text):
            char = text[pos]
            if char == ',':
                part = ''
                pos += 1
            elif char == '"':
                part = get_quoted_part(pos)
            elif char == '{':
                raise NotImplementedBy("zut librabry", "parse sub arrays") # ROADMAP
            else:
                part = get_unquoted_part(pos)
            parts.append(unescape(part)) # type: ignore (part not None so unescape cannot be None)

        return parts

    return split(value[1:-1])

#endregion


#region From misc to strings

def get_number_str(value: float|Decimal|int, *, max_decimals = 15, decimal_separator = '.', no_scientific_notation = False):
    """
    Display the number as a digits string without using scientifical notation, with integer part, decimal separator and decimal part (if any).
    
    This is less accurate for small decimals but more readable and portable when approximations are OK.
    """
    if isinstance(value, int):
        return str(value)
    else:
        text = format(value, f".{max_decimals}{'f' if no_scientific_notation else 'g'}")
        if not 'e' in text:
            pos = text.rfind('.')
            if pos > 0:
                last = len(text) - 1
                while last > pos:
                    if text.endswith('0'):
                        text = text[:-1]
                    else:
                        break
                if text.endswith('.'):
                    text = text[:-1]
        if decimal_separator != '.':
            return text.replace('.', decimal_separator)
        return text


def human_bytes(value: int, *, unit: str = 'iB', divider: int = 1024, decimals: int = 1, max_multiple: str|None = None) -> str:
    """
    Get a human-readable representation of a number of bytes.
    
    :param max_multiple: may be `K`, `M`, `G` or `T`.
    """
    return human_number(value, unit=unit, divider=divider, decimals=decimals, max_multiple=max_multiple)


def human_number(value: int, *, unit: str = '', divider: int = 1000, decimals: int = 1, max_multiple: str|None = None) -> str:
    """
    Get a human-readable representation of a number.

    :param max_multiple: may be `K`, `M`, `G` or `T`.
    """
    if value is None:
        return None

    suffixes = []

    # Append non-multiple suffix (bytes)
    # (if unit is 'iB' we dont display the 'i' as it makes more sens to display "123 B" than "123 iB")
    if unit:
        suffixes.append(' ' + (unit[1:] if len(unit) >= 2 and unit[0] == 'i' else unit))
    else:
        suffixes.append('')

    # Append multiple suffixes
    for multiple in ['K', 'M', 'G', 'T']:
        suffixes.append(f' {multiple}{unit}')
        if max_multiple and max_multiple.upper() == multiple:
            break

    i = 0
    suffix = suffixes[i]
    divided_value = value

    while divided_value > 1000 and i < len(suffixes) - 1:
        divided_value /= divider
        i += 1
        suffix = suffixes[i]

    # Format value
    formatted_value = ('{0:,.'+('0' if i == 0 else str(decimals))+'f}').format(divided_value)
    
    # Display formatted value with suffix
    return f'{formatted_value}{suffix}'


def get_pg_array_str(values: Iterable) -> str:
    """ Parse an Iterable into an array literal (using PostgreSQL syntax). """
    # See: https://www.postgresql.org/docs/current/arrays.html#ARRAYS-INPUT

    if values is None:
        return None
    
    escaped: list[str] = []
    for value in values:
        if value is None:
            value = "null"
        elif isinstance(value, (list,tuple)):
            value = get_pg_array_str(value)
        else:
            if not isinstance(value, str):
                value = str(value)
            if value.lower() == "null":
                value = f'"{value}"'
            elif ',' in value or '"' in value or '\\' in value or '{' in value or '}' in value:
                value = '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
        escaped.append(value)

    return '{' + ','.join(escaped) + '}'


def get_json_str(data):
    from zut.json import ExtendedJSONEncoder
    return json.dumps(data, ensure_ascii=False, cls=ExtendedJSONEncoder)
    

def get_visual_list_str(values: Iterable, *, separator = '|') -> str:
    target_str = ''

    for value in values:
        value = get_str(value)
        
        if separator in value:
            return get_json_str(values)
        
        if not target_str:
            if value.startswith(('{', '[')):
                return get_json_str(values) # avoid ambiguity with postgresql literal or with JSON dump
            target_str = value
        else:        
            target_str += f'{separator}{value}'
    
    return target_str


def get_visual_dict_str(values: Mapping, *, separator = '|'):    
    target_str = ''
    
    for key, value in values.items():
        key = get_str(key)
        value = get_str(value)
        
        if '=' in key or separator in key or '=' in value or separator in value:
            return get_json_str(values)
        elif not target_str and key.startswith(('{', '[')):
            return get_json_str(values) # avoid ambiguity with postgresql literal or with JSON dump
        
        target_str += (separator if target_str else '') + (f'{key}={value}' if value else key)

    return target_str


def get_duration_str(duration: timedelta) -> str:
    # Adapted from: django.utils.duration.duration_iso_string
    if duration < timedelta(0):
        sign = "-"
        duration *= -1
    else:
        sign = ""

    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)
    ms = ".{:06d}".format(microseconds) if microseconds else ""
    return "{}P{}DT{:02d}H{:02d}M{:02d}{}S".format(
        sign, days, hours, minutes, seconds, ms
    )


def _get_duration_components(duration: timedelta):
    days = duration.days
    seconds = duration.seconds
    microseconds = duration.microseconds

    minutes = seconds // 60
    seconds = seconds % 60

    hours = minutes // 60
    minutes = minutes % 60

    return days, hours, minutes, seconds, microseconds


def get_str(value: Any, default: Callable[[Any],str] = str) -> str:
    if value is None:
        return ''
    elif isinstance(value, str):
        return value
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (float,Decimal,int)):
        return get_number_str(value)
    elif isinstance(value, Mapping):
        return get_visual_dict_str(value)
    elif isinstance(value, (Sequence,Set)):
        return get_visual_list_str(value)
    else:
        return default(value)

#endregion


#region Flexible conversion

def convert(value: Any, to: type[T]|Callable[[Any],T], *, use_locale = True, max_decimals: int|None = None, reduce_decimals: int|Sequence[int]|bool = False, decimal_separator: Literal['.',',','detect'] = 'detect', list_separator = '|') -> T|None:
    if value is None:
        return None
    
    if isinstance(to, type):
        if isinstance(value, to):
            return value
        
        if issubclass(to, str):
            converted_value = get_str(value)
        
        elif issubclass(to, bool):
            converted_value = parse_bool(value)

        elif issubclass(to, float):
            converted_value = parse_float(value, decimal_separator=decimal_separator)

        elif issubclass(to, Decimal):
            converted_value = parse_decimal(value, max_decimals=max_decimals, reduce_decimals=reduce_decimals, decimal_separator=decimal_separator)
        
        elif issubclass(to, (datetime,time)):
            converted_value = parse_datetime(value, use_locale=use_locale)
        
        elif issubclass(to, date):
            converted_value = parse_date(value, use_locale=use_locale)

        elif issubclass(to, Mapping):
            converted_value = parse_dict(value, separator=list_separator)
        
        elif issubclass(to, (Sequence,Set)):
            converted_value = parse_list(value, separator=list_separator)
            if converted_value is not None:
                element_to = get_element_type(to)
                if element_to: # type: ignore
                    converted_value = [convert(element, element_to, max_decimals=max_decimals, reduce_decimals=reduce_decimals, use_locale=use_locale, list_separator=list_separator) for element in converted_value]
                
                if to != list:
                    converted_value = to(converted_value)  # type: ignore
    
    elif callable(to):
        converted_value = to(value) # type: ignore

    else:
        raise NotSupportedBy("zut library", f"convert type {type(value).__name__} to {to}")

    return converted_value # type: ignore


def recognize_datetime(value: Any) -> datetime|Any:
    """
    If value is recognized as a datetime ISO string, convert it as datetime, otherwise, let it as is.
    
    This is used to handle datetime values (ypically coming from APIs with JSON-encoded data) as datetimes, notably to perform CSV and JSON parsing and timezone handling.
    """
    if isinstance(value, str) and re.match(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?(?:Z|[\+\-]\d{2}(?::?\d{2})?)?$', value):
        return datetime.fromisoformat(value)
    else:
        return value


def get_element_type(to: type[Sequence|Set]) -> type|None:
    if not issubclass(to, (Sequence,Set)):
        raise TypeError(f"Not a subclass of list, tuple or set: {to}")

    try:
        from types import GenericAlias
    except ImportError:
        # GenericAlias: was introducted in Python 3.9
        return None

    if isinstance(to, GenericAlias):
        from typing import get_args, get_origin
        type_args = get_args(to)
        to = get_origin(to)
        if len(type_args) != 1:
            raise ValueError(f"Only one generic type parameter may be used for {to}")
        return type_args[0]
    else:
        return None

#endregion
