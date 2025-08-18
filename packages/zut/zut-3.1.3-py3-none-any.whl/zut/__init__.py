"""
Top-level API: most commonly reused utilities (Color, encoding, errors, etc).
"""
from __future__ import annotations

import inspect
import logging
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from http import HTTPStatus
from io import IOBase, UnsupportedOperation
from pathlib import Path
from shutil import which
from typing import IO, TYPE_CHECKING, Any, Callable, TypeVar, Union, overload
from warnings import catch_warnings

if TYPE_CHECKING:
    from typing import Literal

try:
    from django.http import Http404 as _BaseNotFoundException
except ModuleNotFoundError:
    _BaseNotFoundException = Exception

__prog__ = 'zut'

__version__: str
__version_tuple__: tuple[int|str, ...]
try:
    from zut._version import __version__, __version_tuple__  # type: ignore
except ModuleNotFoundError:
    __version__ = '?'
    __version_tuple__ = (0, 0, 0, '?')


T = TypeVar('T')


#region Encoding

UTF8_BOM = '\ufeff'
UTF8_BOM_BINARY = UTF8_BOM.encode('utf-8')

SURROGATE_MIN_ORD = ord('\uDC80')
SURROGATE_MAX_ORD = ord('\uDCFF')


def skip_utf8_bom(fp: IO, encoding: str|None = None):
    """
    Skip UTF8 byte order mark, if any.
    - `fp`: open file pointer.
    - `encoding`: if given, do nothing unless encoding is utf-8 or alike.
    """
    if encoding and not encoding in {'utf8', 'utf-8', 'utf-8-sig'}:
        return False

    try:
        start_pos = fp.tell()
    except UnsupportedOperation: # e.g. empty file
        start_pos = 0

    try:
        data = fp.read(1)
    except UnsupportedOperation: # e.g. empty file
        return False
    
    if isinstance(data, str): # text mode
        if len(data) >= 1 and data[0] == UTF8_BOM:
            return True
        
    elif isinstance(data, bytes): # binary mode
        if len(data) >= 1 and data[0] == UTF8_BOM_BINARY[0]:
            data += fp.read(2) # type: ignore (data bytes => fp reads bytes)
            if data[0:3] == UTF8_BOM_BINARY:
                return True
    
    fp.seek(start_pos)
    return False


def fix_utf8_surrogateescape(text: str, potential_encoding = 'cp1252') -> tuple[str,bool]:
    """ Fix potential encoding issues for files open with `open('r', encoding='utf-8', errors='surrogateescape')`. """
    fixed = False
    for c in text:
        c_ord = ord(c)
        if c_ord >= SURROGATE_MIN_ORD and c_ord <= SURROGATE_MAX_ORD:
            fixed = True
            break

    if not fixed:
        return text, False
    
    return text.encode('utf-8', 'surrogateescape').decode(potential_encoding, 'replace'), fixed


def fix_restricted_xml_control_characters(text: str, replace = '?'):
    """
    Replace invalid XML control characters. See: https://www.w3.org/TR/xml11/#charsets.
    """
    if text is None:
        return None
    
    replaced_line = ''
    for c in text:
        n = ord(c)
        if (n >= 0x01 and n <= 0x08) or (n >= 0x0B and n <= 0x0C) or (n >= 0x0E and n <= 0x1F) or (n >= 0x7F and n <= 0x84) or (n >= 0x86 and n <= 0x9F):
            c = replace
        replaced_line += c
    return replaced_line

#endregion


#region Colors

class Color:
    RESET = '\033[0m'

    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    GRAY = LIGHT_BLACK = '\033[0;90m'
    BG_RED = '\033[0;41m'

    # Disable coloring if environment variable NO_COLORS is set to 1 or if stderr is piped/redirected
    NO_COLORS = False
    if os.environ.get('NO_COLORS', '').lower() in {'1', 'yes', 'true', 'on'} or not sys.stderr.isatty():
        NO_COLORS = True
        for _ in dir():
            if isinstance(_, str) and _[0] != '_' and _ not in ['NO_COLORS']:
                locals()[_] = ''

    # Set Windows console in VT mode
    if not NO_COLORS and sys.platform == 'win32':
        import ctypes
        _kernel32 = ctypes.windll.kernel32
        _kernel32.SetConsoleMode(_kernel32.GetStdHandle(-11), 7)
        del _kernel32

#endregion


#region Errors

class SimpleError(ValueError):
    """
    An error that should result to only an error message being printed on the console, without a stack trace.
    """


class InternalError(ValueError):
    """
    Mark a condition which should not happen, except in case of logical/algorithmic error.
    """
    code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    reason = "Internal Error"

    def __init__(self, message: str|None = None):
        super().__init__(message if message else self.reason)


class NotFound(_BaseNotFoundException): # type: ignore
    code = HTTPStatus.NOT_FOUND.value
    reason = HTTPStatus.NOT_FOUND.phrase

    def __init__(self, message: str|None = None):
        super().__init__(message if message else self.reason)


class BadRequest(Exception):
    code = HTTPStatus.BAD_REQUEST.value
    reason = HTTPStatus.BAD_REQUEST.phrase

    def __init__(self, message: str|None = None):
        super().__init__(message if message else self.reason)


class SeveralFound(Exception):
    code = HTTPStatus.CONFLICT.value
    reason = "Several Found"

    def __init__(self, message: str|None = None):
        super().__init__(message if message else self.reason)


class NotImplementedBy(NotImplementedError):
    code = HTTPStatus.NOT_IMPLEMENTED.value
    reason = HTTPStatus.NOT_IMPLEMENTED.phrase

    def __init__(self, by: type|str, feature: str|None = None):
        self.by = by
        self.feature = feature or f"{inspect.stack()[1].function}()"
        by_name = self.by.__name__ if isinstance(self.by, type) else self.by
        super().__init__(f"Not implemented by {by_name}: {self.feature}")


class NotSupportedBy(Exception):
    code = HTTPStatus.NOT_IMPLEMENTED.value
    reason = "Not Supported"

    def __init__(self, by: type|str, feature: str|None = None):
        self.by = by
        self.feature = feature or f"{inspect.stack()[1].function}()"
        by_name = self.by.__name__ if isinstance(self.by, type) else self.by
        super().__init__(f"Not supported by {by_name}: {self.feature}")

#endregion


#region Secrets

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    Protocol = object

    def runtime_checkable(cls):
        return cls

@runtime_checkable
class DelayedStr(Protocol):
    @property
    def value(self) -> str|None:
        ...

    @classmethod
    def ensure_value(cls, obj: str|DelayedStr|None) -> str|None:
        if obj is None or isinstance(obj, str):
            return obj
        else:
            return obj.value

    @classmethod
    def ensure_value_notnull(cls, obj: str|DelayedStr|None) -> str:
        value = cls.ensure_value(obj)
        if value is None:
            raise ValueError("Password value cannot be null")
        return value

    @classmethod
    def ensure_value_notblank(cls, obj: str|DelayedStr|None) -> str:
        value = cls.ensure_value(obj)
        if not value:
            raise ValueError("Password value cannot be blank")
        return value
        

class Secret(DelayedStr):
    def __init__(self, name: str, default: type[SecretNotFound]|str|None = None):
        self.name = name
        self.default = default
        self._is_evaluated = False
        self._value = None
    
    def __str__(self):
        return f"Secret({self.name})"
    
    def __repr__(self):
        return f"Secret({self.name})"

    @property
    def is_evaluated(self):
        return self._is_evaluated
    
    @property
    def value(self) -> str|None:
        if not self._is_evaluated:
            get_logger(__name__).debug("Evaluate secret %s", self.name)
            self._value = get_secret_value(self.name, self.default)
            self._is_evaluated = True
        return self._value


class SecretNotFound(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Secret '{name}' not found")


@overload
def get_secret_value(name: str, default: type[SecretNotFound]|str) -> str:
    ...

@overload
def get_secret_value(name: str, default: None = None) -> str|None:
    ...

def get_secret_value(name: str, default: type[SecretNotFound]|str|None = None) -> str|None:
    # Search in standard files
    name = name.lower()

    path = Path(f'/run/secrets/{name}')
    if path.exists(): # usefull in Docker containers
        return path.read_text(encoding='utf-8')
    
    path = Path.cwd().joinpath(f'secrets/{name}')
    if path.exists(): # usefull during local development
        return path.read_text(encoding='utf-8')
    
    # Search in environment variables
    name = name.upper()
    value = os.environ.get(name)
    if value:
        return value
    
    file = os.environ.get(f'{name}_FILE')
    if file:
        m = re.match(r'^pass:(?P<pass_name>.+)$', file)
        if m:
            from zut.gpg import get_pass
            return get_pass(m['pass_name'], default)
        
        else:
            with open(file, 'r', encoding='utf-8-sig') as fp:
                return fp.read().rstrip('\r\n')

    # Return default
    if isinstance(default, type):
        raise default(name)
    return default


def is_secret_defined(name: str):
    # Search in standard files
    name = name.lower()
    if Path(f'/run/secrets/{name}').exists(): # usefull in Docker containers
        return True
    elif Path.cwd().joinpath(f'secrets/{name}').exists(): # usefull during local development
        return True
    
    # Search in environment variables
    name = name.upper()
    if os.environ.get(name):
        return True
    elif os.environ.get(f'{name}_FILE'):
        return True
    
    # Return default
    return False

#endregion


#region Sudo
# Used in both zut.process and zut.files modules

_sudo_available: bool|Literal['non-interactive']|None = None

def is_sudo_available(*, non_interactive = False) -> bool:
    global _sudo_available
    if _sudo_available is None:
        if not which('sudo'):
            _sudo_available = False
        else:
            try:
                return_code = subprocess.call(['sudo', '-n', 'sh', '-c', 'id -u >/dev/null'], stderr=subprocess.DEVNULL)
                _sudo_available = 'non-interactive' if return_code == 0 else True
            except BaseException: # e.g. SIGINT / CTRL+C
                _sudo_available = False
    if non_interactive:
        return _sudo_available == 'non-interactive'
    return True if _sudo_available else False


class SudoNotAvailable(subprocess.SubprocessError):
    def __init__(self):
        super().__init__("Sudo is not available")

#endregion


#region Columns

class Column:
    """
    Column name with details, used in databases and CSV files.
    """
    name: str
    """ Name of the column. """

    # type : see property below

    precision: int|None
    """ SQL precision specification for the SQL type (ignored if already in `type`) """

    scale: int|None
    """ SQL scale specification for the SQL type (ignored if already in `type`) """

    not_null: bool|None
    """ Indicate whether the column has a NOT NULL contraint. """

    primary_key: bool|None
    """ Indicate whether the column is part of the primary key. """

    identity: bool|None
    """ Indicate whether the column is an identity column. """

    default: Any|None
    """ Default value. Use `now` or `now()` for the current timestamp in the default timezone. Use `sql:...` to use direct sql. """

    converter: Callable[[Any],Any]|Any|None
    """ A converter callable, or a constant value. """

    def __init__(self, name: str, type: str|type|None = None, precision: int|None = None, scale: int|None = None, *, not_null: bool|None = None, primary_key: bool|None = None, identity: bool|None = None, default: Any|None = None, converter: Callable[[Any],Any]|Any|None = None):
        self.name = name
    
        self._python_type: type|None = None
        self.type = type
        
        self.precision = precision
        self.scale = scale
        self.not_null = not_null
        self.primary_key = primary_key
        self.identity = identity
        self.default = default
        self.converter = converter

        if isinstance(self._type, str):
            self._type = self._merge_precision_and_scale(self._type, self.precision, self.scale)
            self.precision = None
            self.scale = None

    @property
    def type(self) -> type|str|None:
        """
        The Python type of the column or the SQL type (a string, optionally including precision and scale).    
        Use `Db.get_sql_type()` or `Db.get_python_type()` functions to pass from one to the other.
        """
        if isinstance(self._type, str):        
            self._type = Column._merge_precision_and_scale(self._type, self.precision, self.scale)
        return self._type
    
    @type.setter
    def type(self, value: type|str|None):
        if isinstance(value, type):
            self._python_type = value
        else:
            self._python_type = None
        self._type = value

    def __str__(self):
        return self.name
    
    def __repr__(self):
        result = f'Column({self.name}'
        if self.type is not None:
            result += f',type={self.type}'
        if self.precision is not None:
            result += f',precision={self.precision}'
        if self.scale is not None:
            result += f',scale={self.scale}'
        if self.not_null is not None:
            result += f',not_null={self.not_null}'
        if self.primary_key is not None:
            result += f',primary_key={self.primary_key}'
        if self.identity is not None:
            result += f',identity={self.identity}'
        if self.identity is not None:
            result += f',identity={self.identity}'
        if self.default is not None:
            result += f',default={self.default}'
        if self.converter is not None:
            result += f',converter={self.converter}'
        result += ')'
        return result

    def replace(self, *,
            name: str|None = None,
            type: str|type|None = None,
            precision: int|None = None,
            scale: int|None = None,
            not_null: bool|None = None,
            primary_key: bool|None = None,
            identity: bool|None = None,
            default: Any|None = None,
            converter: Callable[[Any],Any]|Any|None = None) -> Column:
        
        return Column(
            name = name if name is not None else self.name,
            type = type if type is not None else self.type,
            precision = precision if precision is not None else self.precision,
            scale = scale if scale is not None else self.scale,
            not_null = not_null if not_null is not None else self.not_null,
            primary_key = primary_key if primary_key is not None else self.primary_key,
            identity = identity if identity is not None else self.identity,
            default = default if default is not None else self.default,
            converter = converter if converter is not None else self.converter,
        )
    
    @classmethod
    def _merge_precision_and_scale(cls, sql_type: str, precision: int|None, scale: int|None):
        sql_type = sql_type.lower()

        if '(' in sql_type:
            return sql_type
        
        if precision is not None or scale is not None:
            sql_type += '('
            if precision is not None:
                sql_type += str(precision)
            if precision is not None and scale is not None:
                sql_type += ','
            if scale is not None:
                sql_type += str(scale)
            sql_type += ')'
        
        return sql_type

#endregion


#region Base directory

T_Str_IO_None = TypeVar('T_Str_IO_None', bound=Union[str,IO[str],None])

def in_dir(path: os.PathLike|T_Str_IO_None, dir: str|os.PathLike|None = None, *, mkparent = False) -> str|T_Str_IO_None:
    """
    Usefull for flexible `--out` arguments of command-line applications, see also `zut.csv.dump_csv_or_tabulate()`.
    """
    if path is None or isinstance(path, IOBase):
        return path # type: ignore
    if path == 'stdout':
        return sys.stdout # type: ignore
    if path == 'stderr':
        return sys.stderr # type: ignore
    
    str_path = path if isinstance(path, str) else str(path)

    def relative_if_in_curdir(path: str):
        if path.startswith(os.curdir + os.sep):
            return path[len(os.curdir + os.sep):]
        if re.match(r'^([a-z0-9]+\:)(.+)$', path, re.IGNORECASE): # contains a protocol (or drive letter)
            return path
        relative_path = os.path.relpath(path, os.curdir)
        if relative_path.startswith('.'):
            return path
        return relative_path        

    if '/' in str_path or '\\' in str_path: # already expressed as a directory
        if mkparent:
            from zut.files import dirname, makedirs
            parent = dirname(str_path)
            if parent:
                makedirs(parent, exist_ok=True)
        return relative_if_in_curdir(str_path)

    if not dir:
        return relative_if_in_curdir(str_path)
        
    from zut.files import join
    return relative_if_in_curdir(join(dir, str_path, mkparent=mkparent))

#endregion


#region Logging usage
# (see `zut.config` for configuration of logging)

def get_logger(obj: str|type|object):
    if isinstance(obj, str):
        name = obj
    else:
        if isinstance(obj, type):
            name = f'{obj.__module__}.{obj.__qualname__}'
        elif hasattr(obj, '__class__'):
            name = f'{obj.__class__.__module__}.{obj.__class__.__qualname__}'
        else:
            raise TypeError(f"Invalid type for `get_logger` argument: {type(obj).__name__}")

    try:
        from celery.utils.log import get_task_logger  # type: ignore
        return get_task_logger(name)
    except ModuleNotFoundError:
        return logging.getLogger(name)


@contextmanager
def log_warnings(*, ignore: str|re.Pattern|list[str|re.Pattern]|None = None, logger: logging.Logger|None = None):
    catch = catch_warnings(record=True)
    ctx = None
    try:
        ctx = catch.__enter__()
        yield None
    
    finally:
        if not logger:
            logger = get_logger(__name__)
        if isinstance(ignore, (str,re.Pattern)):
            ignore = [ignore]

        if ctx is not None:
            for warning in ctx:
                ignored = False
                if ignore:
                    message = str(warning.message)
                    for spec in ignore:
                        if isinstance(spec, re.Pattern):
                            if spec.match(message):
                                ignored = True
                                break
                        elif spec == message:
                            ignored = True
                            break
                
                if not ignored:
                    logger.warning("%s: %s", warning.category.__name__, warning.message)
        
        catch.__exit__(None, None, None)

#endregion
