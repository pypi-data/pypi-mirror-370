"""
Configure and access configuration of the system: logging, dotenv, locale.

User functions (such as `get_logger` and `log_warnings`) are defined in the top-level API (but are also available from this module as shortcut).
"""
from __future__ import annotations

import atexit
import locale
import logging
import logging.config
import os
import re
import subprocess
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from traceback import format_exception
from types import TracebackType
from typing import Callable, Iterator, Mapping

from zut import Color, Secret, get_logger, log_warnings, skip_utf8_bom

__shortcuts__ = (Secret, get_logger, log_warnings)


#region Logging

_logging_configured = False

def configure_logging(level: str|int|None = None, *, names: bool|None = None, file_level: str|int|None = None, loggers: Mapping[str,str|int|dict|None]|None = None, count = True, exit_handler = True, override = False):
    global _logging_configured
    if not override and _logging_configured:
        return
    config = get_logging_config(level=level, names=names, file_level=file_level, loggers=loggers, count=count, exit_handler=exit_handler)
    logging.config.dictConfig(config)
    _logging_configured = True


def get_logging_config(level: str|int|None = None, *, names: bool|None = None, file_level: str|int|None = None, loggers: Mapping[str,str|int|dict|None]|None = None, count = True, exit_handler = True):
    if not isinstance(level, str):
        if isinstance(level, int):
            level = logging.getLevelName(level)
        else:
            level = os.environ.get('LOG_LEVEL', '').upper() or 'INFO'
            if level == 'DEBUG' and names is None:
                names = True
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(levelname)-8s [%(name)s] %(message)s' if names else '%(levelname)-8s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'default',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': level,
        },
        'loggers': {
            'django': { 'level': 'INFO', 'propagate': False },
            'daphne': { 'level': 'INFO', 'propagate': False },
            'asyncio': { 'level': 'INFO', 'propagate': False },
            'urllib3': { 'level': 'INFO', 'propagate': False },
            'botocore': { 'level': 'INFO', 'propagate': False },
            'boto3': { 'level': 'INFO', 'propagate': False },
            's3transfer': { 'level': 'INFO', 'propagate': False },
            'PIL': { 'level': 'INFO', 'propagate': False },
            'celery.utils.functional': { 'level': 'INFO', 'propagate': False },
            'smbprotocol': { 'level': 'WARNING', 'propagate': False },
        },
    }

    if loggers:
        for logger_name, logger_config in loggers.items():
            if logger_config is None:
                config['loggers'].pop(logger_name, None)
                continue
            
            if isinstance(logger_config, str):
                logger_config = { 'level': logger_config, 'propagate': False }
            elif isinstance(logger_config, int):
                logger_config = { 'level': logging.getLevelName(logger_config), 'propagate': False }
            config['loggers'][logger_name] = logger_config

    if not Color.NO_COLORS:
        config['formatters']['colored'] = {
            '()': ColoredFormatter.__module__ + '.' + ColoredFormatter.__qualname__,
            'format': '%(log_color)s%(levelname)-8s%(reset)s %(light_black)s[%(name)s]%(reset)s %(message)s' if names else '%(log_color)s%(levelname)-8s%(reset)s %(message)s',
        }

        config['handlers']['console']['formatter'] = 'colored'

    file = os.environ.get('LOG_FILE')
    if file:
        if not isinstance(file_level, str):
            if isinstance(file_level, int):
                file_level = logging.getLevelName(file_level)
            else:
                file_level = os.environ.get('LOG_FILE_LEVEL', '').upper() or level

        log_dir = os.path.dirname(file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        config['formatters']['file'] = {
            'format': '%(asctime)s %(levelname)s [%(name)s] %(message)s',
        }
        config['handlers']['file'] = {
            'class': 'logging.FileHandler',
            'level': file_level,
            'formatter': 'file',
            'filename': file,
            'encoding': 'utf-8',
        }

        config['root']['handlers'].append('file')
    
        file_intlevel = logging.getLevelName(file_level)
        intlevel = logging.getLevelName(level)
        if file_intlevel < intlevel:
            config['root']['level'] = file_level
    
    if count or exit_handler:
        config['handlers']['counter'] = {
            'class': LogCounter.__module__ + '.' + LogCounter.__qualname__,
            'level': 'WARNING',
            'exit_handler': exit_handler,
        }

        config['root']['handlers'].append('counter')

    return config


class ColoredRecord:
    LOG_COLORS = {
        logging.DEBUG:     Color.GRAY,
        logging.INFO:      Color.CYAN,
        logging.WARNING:   Color.YELLOW,
        logging.ERROR:     Color.RED,
        logging.CRITICAL:  Color.BG_RED,
    }

    def __init__(self, record: logging.LogRecord):
        # The internal dict is used by Python logging library when formatting the message.
        # (inspired from library "colorlog").
        self.__dict__.update(record.__dict__)
        
        self.log_color = self.LOG_COLORS.get(record.levelno, '')

        for attname, value in Color.__dict__.items():
            if attname == 'NO_COLORS' or attname.startswith('_'):
                continue
            setattr(self, attname.lower(), value)


class ColoredFormatter(logging.Formatter):
    def formatMessage(self, record: logging.LogRecord) -> str:
        """Format a message from a record object."""
        wrapper = ColoredRecord(record)
        message = super().formatMessage(wrapper) # type: ignore
        return message


class LogCounter(logging.Handler):
    """
    A logging handler that counts warnings and errors.
    
    If warnings and errors occured during the program execution, display counts at exit
    and set exit code (if it was not explicitely set with `sys.exit` function).
    """
    counts: dict[int, int]

    error_exit_code = 199
    warning_exit_code = 198

    
    _detected_exception: tuple[type[BaseException], BaseException, TracebackType|None]|None = None
    _detected_exit_code = 0
    _original_exit: Callable[[int],None] = sys.exit
    _original_excepthook = sys.excepthook

    _registered = False
    _logger: logging.Logger

    def __init__(self, *, level = logging.WARNING, exit_handler = False):
        if not hasattr(self.__class__, 'counts'):
            self.__class__.counts = {}
        
        if exit_handler and not self.__class__._registered:
            sys.exit = self.__class__._exit
            sys.excepthook = self.__class__._excepthook
            atexit.register(self.__class__._exit_handler)
            self.__class__._logger = get_logger(f'{self.__class__.__module__}.{self.__class__.__qualname__}')
            self.__class__._registered = True
        
        super().__init__(level=level)

    def emit(self, record: logging.LogRecord):        
        if not record.levelno in self.__class__.counts:
            self.__class__.counts[record.levelno] = 1
        else:
            self.__class__.counts[record.levelno] += 1
    
    @classmethod
    def _exit(cls, code: int = 0):
        cls._detected_exit_code = code
        cls._original_exit(code)
    
    @classmethod
    def _excepthook(cls, exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType|None):
        cls._detected_exception = exc_type, exc_value, exc_traceback
        cls._original_exit(1)

    @classmethod
    def _exit_handler(cls):
        if cls._detected_exception:
            exc_type, exc_value, exc_traceback = cls._detected_exception

            msg = 'An unhandled exception occured\n'
            msg += ''.join(format_exception(exc_type, exc_value, exc_traceback)).strip()
            cls._logger.critical(msg)

        else:
            error_count = 0
            warning_count = 0
            for level, count in cls.counts.items():
                if level >= logging.ERROR:
                    error_count += count
                elif level >= logging.WARNING:
                    warning_count += count
            
            msg = ''
            if error_count > 0:
                msg += (', ' if msg else 'Logged ') + f"{error_count:,} error{'s' if error_count > 1 else ''}"
            if warning_count > 0:
                msg += (', ' if msg else 'Logged ') + f"{warning_count:,} warning{'s' if warning_count > 1 else ''}"
            
            if msg:
                cls._logger.log(logging.ERROR if error_count > 0 else logging.WARNING, msg)                             
                # Change exit code if it was not originally set explicitely to another value using `sys.exit()`
                if cls._detected_exit_code == 0:
                    os._exit(cls.error_exit_code if error_count > 0 else cls.warning_exit_code)

#endregion


#region Dotenv

_loaded_dotenv_paths: set[str|None] = set()

def load_dotenv(path: os.PathLike|str|None = None, *, encoding = 'utf-8', override = False, parents = False) -> str|None:
    """
    Load `.env` from the given or current directory (or the given file if any) to environment variables.    
    If the given file is a directory, search `.env` in this directory.
    If `parents` is True, also search if parent directories until a `.env` file is found.

    Usage example:

    ```
    # Load configuration files
    load_dotenv() # load `.env` in the current working directory
    load_dotenv(os.path.dirname(__file__), parents=True) # load `.env` in the Python module installation directory or its parents
    load_dotenv(f'C:\\ProgramData\\my-app\\my-app.env' if sys.platform == 'win32' else f'/etc/my-app/my-app.env') # load `.env` in the system configuration directory
    ```
    """
    given_path_was_none = False
    if not path:
        if None in _loaded_dotenv_paths and not override:
            return None # already loaded
        given_path_was_none = True
        path = find_to_root('.env') if parents else '.env'
    elif os.path.isdir(path):
        path = find_to_root('.env', path) if parents else os.path.join(path, '.env')
    elif not os.path.isfile(path) and parents:
        path = find_to_root(os.path.basename(path), os.path.dirname(path))
        if not path: # not found
            return None
    elif isinstance(path, os.PathLike):
        path = str(path)
    elif not isinstance(path, str):
        raise TypeError('path')
    
    if not path or not os.path.isfile(path):
        return None # does not exist
    
    if path in _loaded_dotenv_paths and not override:
        return None # already loaded
        
    get_logger(__name__).debug("Load dotenv file: %s", path)
    with open(path, 'r', encoding=encoding, newline=None) as fp:
        skip_utf8_bom(fp, encoding=encoding)
        for name, value in parse_properties(fp.read()):
            if not override:
                if name in os.environ:
                    continue
            os.environ[name] = value

    _loaded_dotenv_paths.add(path)
    if given_path_was_none:
        _loaded_dotenv_paths.add(None)
    return path


def find_to_root(name: str, start_dir: str|os.PathLike|None = None) -> str|None:
    """
    Find the given file name from the given start directory (or current working directory if none given), up to the root.

    Return None if not found.
    """    
    if start_dir:            
        if not os.path.exists(start_dir):
            raise IOError('Starting directory not found')
        elif not os.path.isdir(start_dir):
            start_dir = os.path.dirname(start_dir)
    else:
        start_dir = os.getcwd()

    last_dir = None
    current_dir = os.path.abspath(start_dir)
    while last_dir != current_dir:
        path = os.path.join(current_dir, name)
        if os.path.exists(path):
            return path
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir

    return None


def parse_properties(content: str) -> Iterator[tuple[str,str]]:
    """
    Parse properties/ini/env file content.
    """
    def find_nonspace_on_same_line(start: int):
        pos = start
        while pos < len(content):
            c = content[pos]
            if c == '\n' or not c.isspace():
                return pos
            else:
                pos += 1
        return None

    def find_closing_quote(start: int):
        """ Return the unquoted value and the next position """
        pos = content.find('"', start)
        if pos == -1:
            return content[start:], None
        elif pos+1 < len(content) and content[pos+1] == '"': # escaped
            begining_content = content[start:pos+1]
            remaining_content, remaining_pos = find_closing_quote(pos+2)
            return begining_content + remaining_content, remaining_pos
        else:
            return content[start:pos], pos

    name = None
    value = '' # value being build (or name being build if variable `name` is None)
    i = find_nonspace_on_same_line(0)
    while i is not None and i < len(content):
        c = content[i]
        if c == '"':
            unquoted, end = find_closing_quote(i+1)
            value += unquoted
            if end is None:
                return
            i = end + 1
        elif c == '=' and name is None:
            name = value
            value = ''
            i += 1
        elif c == '\n':
            if name or value:
                yield (name, value) if name is not None else (value, '')
            name = None
            value = ''
            i += 1            
        elif c == '#': # start of comment
            if name or value:
                yield (name, value) if name is not None else (value, '')
            name = None
            value = ''
            pos = content.find('\n', i+1)
            if pos == -1:
                return
            else:
                i = pos + 1
        elif c.isspace(): # start of whitespace
            end = find_nonspace_on_same_line(i+1)
            if value:
                if end is None or content[end] in ({'#', '\n', '='} if name is None else {'#', '\n'}):
                    pass # strip end
                else:
                    value += content[i:end]
            i = end
        else:
            value += c
            i += 1

    if name or value:
        yield (name, value) if name is not None else (value, '')

#endregion


#region Detection util

_in_docker_container: bool|None = None

def in_docker_container():
    """
    Indicate whether the application is running in a Docker container.
    """
    global _in_docker_container
    if _in_docker_container is None:
        _in_docker_container = os.path.exists('/.dockerenv')
    return _in_docker_container

_desktop_environment: str|None = None

def get_desktop_environment() -> str:
    # From http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=1139057
    global _desktop_environment
    if _desktop_environment is not None:
        return _desktop_environment
    
    if sys.platform in ["win32", "cygwin"]:
        _desktop_environment = 'windows'
        return _desktop_environment
    elif sys.platform == "darwin":
        _desktop_environment = 'mac'
        return _desktop_environment        
    else: # Most likely either a POSIX system or something not much common
        def is_running(process):
            # From http://www.bloggerpolis.com/2011/05/how-to-check-if-a-process-is-running-using-python/
            # and http://richarddingwall.name/2009/06/18/windows-equivalents-of-ps-and-kill-commands/
            try: # Linux/Unix
                s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE, text=True)
            except: # Windows
                s = subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE, text=True)
            if s.stdout is not None:
                for x in s.stdout:
                    if re.search(process, x):
                        return True
            return False

        def detect() -> str:
            desktop_session = os.environ.get("DESKTOP_SESSION")
            if desktop_session is not None: #easier to match if we doesn't have  to deal with caracter cases
                desktop_session = desktop_session.lower()
                if desktop_session in ["gnome","unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox", 
                                        "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde"]:
                    return desktop_session
                ## Special cases ##
                # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
                # There is no guarantee that they will not do the same with the other desktop environments.
                elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                    return "xfce4"
                elif desktop_session.startswith('ubuntustudio'):
                    return 'kde'
                elif desktop_session.startswith('ubuntu'):
                    return 'gnome'     
                elif desktop_session.startswith("lubuntu"):
                    return "lxde" 
                elif desktop_session.startswith("kubuntu"): 
                    return "kde" 
                elif desktop_session.startswith("razor"): # e.g. razorkwin
                    return "razor-qt"
                elif desktop_session.startswith("wmaker"): # e.g. wmaker-common
                    return "windowmaker"
            if os.environ.get('KDE_FULL_SESSION') == 'true':
                return "kde"
            elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID', ''):
                    return "gnome2"
            #From http://ubuntuforums.org/showthread.php?t=652320
            elif is_running("xfce-mcs-manage"):
                return "xfce4"
            elif is_running("ksmserver"):
                return "kde"
            return "unknown"
            
        _desktop_environment = detect()
        return _desktop_environment

#endregion


#region Data dir

def get_app_data_dir(base_name: str, base_dir: Path|None = None) -> Path:
    _value = os.environ.get(f'{base_name.upper()}_DATA_DIR')
    if _value:
        return Path(_value)
    
    _value = os.environ.get('DATA_DIR')
    if _value:
        return Path(_value).joinpath(base_name.lower())
    
    if base_dir:
        _value = base_dir.joinpath('data')
        if _value.exists():
            return _value
        
    return Path(os.environ.get('APPDATA', '~\\AppData\\Roaming' if sys.platform == 'win32' else '~/.local/share')).expanduser().joinpath(base_name.lower())

#endregion


#region Locale

def register_locale(name: str = ''):
    """
    Register a locale for the entire application (system default locale if non name is given).
    """
    locale.setlocale(locale.LC_ALL, _prepare_locale_name(name))


@contextmanager
def use_locale(name: str = ''):
    """
    Use a locale temporary (in the following thread-local block/context).

    See: https://stackoverflow.com/a/24070673
    """
    with _locale_lock:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, _prepare_locale_name(name))
        finally:
            locale.setlocale(locale.LC_ALL, saved)

_locale_lock = threading.Lock()


def _prepare_locale_name(name: str):
    if not name:
        return ''
    if not '.' in name:
        if sys.platform == 'win32':
            name += '.1252'
        else:
            name += '.UTF-8'
    return name


def get_locale_name():
    """
    Return the current locale name, for example: `fr_FR.UTF-8` on Linux or `French_France.1252` on Windows.
    """
    global _locale_name
    if _locale_name is None:
        with use_locale():
            region, encoding = locale.getlocale()
            _locale_name = f"{region or ''}.{encoding or ''}"

    return _locale_name

_locale_name = None


def get_locale_decimal_separator(name: str = ''):
    """
    Return locale decimal separator (use current locale if name is empty).
    """
    global _locale_decimal_separator
    if not name and _locale_decimal_separator is not None:
        return _locale_decimal_separator
    
    with use_locale(name):
        value = locale.localeconv()["decimal_point"]
    
    if not name:
        _locale_decimal_separator = value
    return value

_locale_decimal_separator = None


def get_locale_date_format(name: str = '') -> str|None:
    """
    Return locale date format, if known (e.g. "%d/%m/%Y") (use current locale if name is empty).
    """
    global _locale_date_format
    if not name and _locale_date_format is not None:
        return _locale_date_format
    
    with use_locale(name):
        try:
            value = locale.nl_langinfo(locale.D_FMT) # type: ignore
        except AttributeError:
            name = get_locale_name()
            if name.startswith(('fr_FR.', 'French_France.')):
                value = '%d/%m/%Y'
            else:
                value = None

    if not name:
        _locale_date_format = value
    return value

_locale_date_format = None

#endregion
