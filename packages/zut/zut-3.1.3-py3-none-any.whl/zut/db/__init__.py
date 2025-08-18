"""
A standardized interface to access different database backends.
"""
from __future__ import annotations

import atexit
import logging
import os
import re
import sys
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timezone, tzinfo
from decimal import Decimal
from enum import Enum, Flag
from pathlib import Path
from secrets import token_hex
from typing import IO, TYPE_CHECKING, Any, Callable, Generator, Generic, Iterable, Iterator, Mapping, NamedTuple, Sequence, Set, TypeVar, overload
from urllib.parse import ParseResult, quote, urlparse
from uuid import UUID

from zut import Column, DelayedStr, NotFound, NotImplementedBy, NotSupportedBy, Secret, SeveralFound, T, files, get_logger, is_secret_defined
from zut.convert import convert, get_element_type, get_json_str, get_visual_dict_str, get_visual_list_str
from zut.net import check_port
from zut.polyfills import cached_property
from zut.tabulate import tabulate
from zut.tz import is_local_tz, is_utc_tz, make_aware, make_naive, now_aware, now_naive, parse_tz
from zut.urls import build_url

if TYPE_CHECKING:
    from typing import Literal

    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.models import Model
    from django.utils.connection import ConnectionProxy


#region Protocols

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    Protocol = object


class Cursor(Protocol):
    def execute(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None):
        ...

    def __iter__(self) -> Iterator[tuple[Any,...]]:
        ...

    @property
    def rowcount(self) -> int|None:
        """
        The number of rows modified by the last SQL statement. Has the value of -1 or None if the number of rows is unknown or unavailable.
        """
        ...

    @property
    def lastrowid(self) -> int|None:
        """
        The rowid of the last inserted row. None if no inserted rowid.
        """
        ...

    @property
    def description(self) -> tuple[tuple[str, type|int|str|None, int|None, int|None, int|None, int|None, bool|int|None]]:
        """
        The metadata for the columns returned in the last SQL SELECT statement, in
        the form of a list of tuples. Each tuple contains seven fields:

        0. name of the column (or column alias)
        1. type information (pyodbc: type code, the Python-equivalent class of the column, e.g. str for VARCHAR)
        2. display size (pyodbc: does not set this value)
        3. internal size (in bytes)
        4. precision
        5. scale
        6. nullable (True/False)

        ref: https://peps.python.org/pep-0249/#description
        """
        ...

    def close(self):
        ...

T_Connection = TypeVar('T_Connection')

#endregion


class Db(Generic[T_Connection]):
    #region Connections and transactions

    slug: str|None
    name: str|None
    host: str|None
    port: int|str|None
    user: str|None
    password: str|DelayedStr|None
    password_required: bool|None
    encrypt: bool|None
    no_autocommit: bool|None
    tz: Literal['local','utc']|None
    migrations_dir: str|os.PathLike|None

    # Fixed in code
    scheme: str
    default_port: int

    def __init__(self,
                 connection_or_slug: T_Connection|BaseDatabaseWrapper|ConnectionProxy|str|None = None, *,
                 slug: str|None = None,
                 name: str|None = None,
                 host: str|None = None,
                 port: int|str|None = None,
                 user: str|None = None,
                 password: str|DelayedStr|None = None,
                 password_required: bool|None = None,
                 encrypt: bool|str|None = None,
                 no_autocommit: bool|str|None = None,
                 tz: Literal['local','utc']|None = None,
                 migrations_dir: str|os.PathLike|None = None):
        """
        :param tz: If set, aware datetimes are written to the db as naive datetimes in the given timezone, and naive datetimes read from the db are considered as aware datetimes in the given timezone.
        """
        self._logger = get_logger(self)

        self.slug: str|None
        self._connection: T_Connection|None
        self._connection_is_external: bool
        if not connection_or_slug:
            self.slug = slug
            self._connection = None
            self._connection_is_external = False
        elif isinstance(connection_or_slug, str):
            self.slug = slug if slug else connection_or_slug
            self._connection = None
            self._connection_is_external = False
        elif hasattr(connection_or_slug, 'cursor'):
            self.slug = slug
            self._connection = connection_or_slug # type: ignore
            self._connection_is_external = True
        else:
            raise TypeError(f"connection_or_slug: {type(connection_or_slug).__module__}.{type(connection_or_slug).__name__}")

        self._env_prefix = f'{self.slug.upper()}_' if self.slug else None

        self.name = self._get_param_value('name', name)
        self.host = self._get_param_value('host', host)
        self.port = self._get_param_value('port', port, int)
        self.user = self._get_param_value('user', user)
    
        self.password: str|DelayedStr|None = self._get_param_value('password', password, secret=True)
        self.password_required = self._get_param_value('password_required', password_required, bool, default=False)

        self.encrypt = self._get_param_value('encrypt', encrypt, bool)
        self.no_autocommit = self._get_param_value('no_autocommit', no_autocommit, bool, default=False)
        self.migrations_dir = self._get_param_value('migrations_dir', migrations_dir, Path)
        
        self._tz: tzinfo|None
        tz = self._get_param_value('tz', tz)
        if not tz:
            self.tz = None
            self._tz = None
        elif tz == 'local' or tz == 'localtime':
            self.tz = 'local'
            self._tz = parse_tz('local')
        elif tz == 'utc' or tz == 'UTC':
            self.tz = 'utc'
            self._tz = timezone.utc
        else:
            self._tz = parse_tz(tz)
            if is_local_tz(self._tz):
                self.tz = 'local'
            elif is_utc_tz(self._tz):
                self.tz = 'utc'
            else:
                self.tz = None

        self._unclosed_results: set[ResultManager] = set()
        atexit.register(self._warn_unclosed_executes)

    def _get_param_value(self, name: str, specified_value: Any, target_type: type|None = None, *, default = None, secret = False) -> Any:
        # Environment variable have either priority
        value = None
        if self._env_prefix:
            env_name = f'{self._env_prefix}{name.upper()}'
            value = os.environ.get(env_name)
            
            if not value and secret:
                if is_secret_defined(env_name):
                    value = Secret(env_name)

        # Then the value passed to the class constructor
        if not value:
            value = specified_value

        # Otherwise take the value passed as a class attribute
        if value is None:
            value = getattr(self.__class__, name.lower(), None)

        if value is not None:
            if target_type is not None and value != '' and not isinstance(value, target_type):
                if target_type == bool and isinstance(value, str):
                    value = value.lower() in {'1', 'yes', 'true', 'on'}
                else:
                    value = target_type(value)

        # Otherwise, take default value
        if value is None:
            return default        
        return value
    
    def _warn_unclosed_executes(self):
        count = len(self._unclosed_results)
        if count > 0:
            message = f"{self.scheme}{f'[{self.name}]' if self.name else ''}: {count} unclosed execution result cursor(s). Did you enclosed all calls to `{self.__class__.__name__}.execute_*_result()` methods using `with` blocks?"
            for result in self._unclosed_results:
                message += f"\n- Result {result.num}"
                if result.sql is not None:
                    message += f", sql: " + result.sql[:100] + ('…' if len(result.sql) > 100 else '')
            self._logger.warning(message)
            self._unclosed_results.clear()

    def close(self):
        self._warn_unclosed_executes()
        if not self._connection_is_external and self._connection is not None:
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Close %s (%s) connection to %s", type(self).__name__, type(self._connection).__module__ + '.' + type(self._connection).__qualname__, self.get_url(hide_password=True))
            self._connection.close() # type: ignore

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type = None, exc = None, exc_tb = None):
        self.close()

    @property
    def connection(self) -> T_Connection:
        if self._connection is None:
            if isinstance(self.password, Secret):
                self.password = self.password.value
            if self.password_required and not self.password:
                raise ValueError(f"Missing required password for {self.name} ({self.__class__.__name__})")
            
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Open %s connection to %s", type(self).__name__, self.get_url(hide_password=True))
            self._connection = self.create_connection()

            if self.migrations_dir:
                self.migrate(self.migrations_dir)

        return self._connection
    
    def create_connection(self, autocommit: bool|None = None) -> T_Connection:
        raise NotImplementedBy(self.__class__)
    
    @property
    def autocommit(self) -> bool:
        if not self._connection:
            return False if self.no_autocommit else True
        else:
            return self._connection.autocommit # type: ignore

    def transaction(self) -> AbstractContextManager:    
        try:
            from django.db import transaction
            from django.db.backends.base.base import BaseDatabaseWrapper
            from django.utils.connection import ConnectionProxy
            if isinstance(self.connection, (BaseDatabaseWrapper,ConnectionProxy)):
                return transaction.atomic()
        except ModuleNotFoundError:
            pass
        return self._create_transaction()
        
    @contextmanager
    def _create_transaction(self):
        if not self.in_transaction:
            self.execute(self._start_transaction_sql)
            self._in_transaction = True
        
        try:
            yield None
            self.execute("COMMIT")
        except:
            self.execute("ROLLBACK")
            raise
        finally:
            self._in_transaction = False

    @property
    def in_transaction(self) -> bool:
        return getattr(self, '_transaction', False)

    def commit(self) -> None:
        self.connection.commit() # type: ignore

    def rollback(self) -> None:
        self.connection.rollback() # type: ignore

    def check_port(self) -> bool:
        host = self.host or '127.0.0.1'
        port: int = self.port if self.port is not None else self.default_port # type: ignore
        return True if check_port(host, port) else False      

    def is_available(self, *, migrations: str|tuple[str,str]|Sequence[str|tuple[str,str]]|Literal['*']|None = None):
        """
        Try to connect to the database. Return True in case of success, False otherwise.

        :param migrations: A list of `(app_label, migration_name)` indicating Django migration(s) that must be applied. Use '*' if all migrations must be applied.
        """
        _migrations: list[str] = []
        if migrations:
            def parse_migration_identifier(identifier) -> str:
                if isinstance(identifier, tuple) and len(identifier) == 2:
                    return f"{identifier[0]}:{identifier[1]}"
                elif isinstance(identifier, str) and (pos := identifier.find(':')) >= 1:
                    return f"{identifier[0:pos]}:{identifier[pos+1:]}"
                else:
                    raise TypeError(f"migration: {type(identifier).__name__}")

            if migrations == '*':
                from django.db.migrations.loader import MigrationLoader
                loader = MigrationLoader(self.connection)
                _migrations = [f"{app_label}:{migration_name}" for app_label, migration_name in loader.disk_migrations]
            elif isinstance(migrations, (str,tuple)):
                _migrations = [parse_migration_identifier(migrations)]
            else:
                _migrations = [parse_migration_identifier(migration) for migration in migrations]

        must_exit = False
        try:
            cursor: Cursor = self.connection.cursor() # type: ignore
            if hasattr(cursor, '__enter__'):
                cursor = cursor.__enter__() # type: ignore
                must_exit = True
            cursor.execute('SELECT 1')

            if _migrations:
                from django.db.migrations.recorder import MigrationRecorder
                recorder = MigrationRecorder(self.connection) # type: ignore
                applied_migrations = set(f"{app_label}:{migration_name}" for app_label, migration_name in recorder.applied_migrations().keys())
                for migration in _migrations:
                    if not migration in applied_migrations:
                        self._logger.debug("Migration %s not applied", migration)
                        return False
                return True
            else:
                return True
        except Exception as err:
            self._logger.debug("Database not available: [%s] %s", type(err), err)
            return False
        finally:
            if must_exit:
                cursor.__exit__(None, None, None) # type: ignore

    def get_url(self, *, hide_password: bool = False, table: str|tuple|type|DbObj|None = None) -> str:
        try:
            url = self._url
        except AttributeError:
            url = None

        if not url:
            if self._connection_is_external:
                self._url = self.build_connection_url()
            else:
                path = self.name.replace('\\', '/') if self.scheme == 'sqlite' and self.name else self.name
                self._url = build_url(scheme=self.scheme, hostname=self.host, port=self.port, username=self.user, password='__password__', path=path)
            url = self._url

        if hide_password:
            url = url.replace('__password__', '*****')
        else:
            url = url.replace('__password__', DelayedStr.ensure_value(self.password) or '')

        if table:
            if not self.name:
                url += '/.'
            table = self.parse_obj(table)
            url += '/' + (quote(table.schema) + '.' if table.schema else '') + quote(table.name)
        
        return url

    def build_connection_url(self) -> str:
        raise NotImplementedBy(self.__class__)

    #endregion


    #region Cursors

    def get_lastrowid(self, cursor: Cursor) -> int|None:
        """
        The rowid of the last inserted row. None if no inserted rowid.
        """
        return cursor.lastrowid
    
    def _register_notices_handler(self, cursor: Cursor, source: str|None) -> AbstractContextManager|None:
        """
        Register a notices handler for the cursor. Must be a context manager.
        """
        pass

    def _log_cursor_notices(self, cursor: Cursor, source: str|None):
        """
        Log notices produced during analysis of a cursor result set.
        The cursor must be analyzed as-is, no operation must be done on in (neither advancing the result set, nor opening a new cursor).
        
        Use this if notices cannot be handled through `_register_notices_handler`.
        """
        pass

    def _log_accumulated_notices(self, source: str|None):
        """
        Log notices produced after execution of a cursor.
        
        Use this if notices cannot be handled through `_register_notices_handler` or `_log_cursor_notices`.
        """
        pass
    
    #endregion

    
    #region Execute

    _procedure_caller = 'CALL'
    _procedure_params_parenthesis = True
    _function_requires_schema = False

    def execute(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False) -> int:
        with ResultManager(self, sql, params, limit=limit, offset=offset, source=source, warn_if_result=warn_if_result) as result:
            rowcount = result.rowcount
            return 0 if rowcount is None or rowcount <= 0 else rowcount

    def execute_result(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False) -> ResultManager:
        return ResultManager(self, sql, params, limit=limit, offset=offset, source=source, warn_if_result=warn_if_result)
    
    def execute_function(self, obj: str|tuple|DbObj, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False) -> int:
        with self.execute_function_result(obj, params, limit=limit, offset=offset, source=source, warn_if_result=warn_if_result) as result:
            rowcount = result.rowcount
            return 0 if rowcount is None or rowcount <= 0 else rowcount

    def execute_function_result(self, obj: str|tuple|DbObj, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False) -> ResultManager:
        obj = self.parse_obj(obj)
        sql, params = self.prepare_function_sql(obj, params)
        if not source:
            source = obj.unsafe
        return self.execute_result(sql, params, limit=limit, offset=offset, source=source, warn_if_result=warn_if_result)
    
    def execute_procedure(self, obj: str|tuple|DbObj, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False) -> int:
        with self.execute_procedure_result(obj, params, limit=limit, offset=offset, source=source, warn_if_result=warn_if_result) as result:
            rowcount = result.rowcount
            return 0 if rowcount is None or rowcount <= 0 else rowcount
    
    def execute_procedure_result(self, obj: str|tuple|DbObj, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False) -> ResultManager:
        obj = self.parse_obj(obj)
        sql, params = self.prepare_function_sql(obj, params, procedure=True)
        if not source:
            source = obj.unsafe
        return self.execute_result(sql, params, limit=limit, offset=offset, source=source, warn_if_result=warn_if_result)

    def execute_script(self, script: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False, encoding = 'utf-8') -> int:
        with self.execute_script_result(script, params, limit=limit, offset=offset, encoding=encoding, source=source, warn_if_result=warn_if_result) as result:
            rowcount = result.rowcount
            return 0 if rowcount is None or rowcount <= 0 else rowcount

    def execute_script_result(self, script: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False, encoding = 'utf-8') -> ResultManager:
        statement_list = self._split_script(script, encoding)
        statement_count = len(statement_list)
        if statement_count > 1:
            previous_result: ResultManager|None = None
            for index, sql in enumerate(statement_list):
                if previous_result is not None:
                    with previous_result:
                        pass
                
                statement_num = index + 1
                if self._logger.isEnabledFor(logging.DEBUG):
                    statement_start = re.sub(r"\s+", " ", sql).strip()[0:100] + "…"
                    self._logger.debug("Execute statement %d/%d: %s ...", statement_num, statement_count, statement_start)
                
                _source = (f'{source}, ' if source else '') + f'statement {statement_num}/{statement_count}'
                
                if warn_if_result == 'not-last':
                    _warn_if_result = True if statement_num < statement_count else 'not-last'
                else:
                    _warn_if_result = warn_if_result

                previous_result = self.execute_result(sql, params, limit=limit, offset=offset, source=_source, warn_if_result=_warn_if_result)
            
            if previous_result is None:
                raise ValueError("No sql to execute")
            return previous_result
        else:
            return self.execute_result(script, params, limit=limit, offset=offset, source=source, warn_if_result=warn_if_result)

    def execute_file(self, file: str|os.PathLike, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False, encoding = 'utf-8', **file_kwargs) -> int:
        sql = self.prepare_file_sql(file, encoding=encoding, **file_kwargs)
        if not source:
            source = os.path.basename(file)
        return self.execute_script(sql, params, limit=limit, offset=offset, source=source, warn_if_result=warn_if_result, encoding=encoding)

    def execute_file_result(self, file: str|os.PathLike, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False, encoding = 'utf-8', **file_kwargs) -> ResultManager:
        sql = self.prepare_file_sql(file, encoding=encoding, **file_kwargs)
        if not source:
            source = os.path.basename(file)
        return self.execute_script_result(sql, params, limit=limit, offset=offset, source=source, warn_if_result=warn_if_result, encoding=encoding)
    
    # ---------- Dicts ----------

    def iter_dicts(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> Generator[dict[str,Any], Any, None]:
        with ResultManager(self, sql, params, limit=limit, offset=offset) as result:
            headers = [column_description[0] for column_description in result.cursor.description]
            for row in result:
                yield {header: row[i] for i, header in enumerate(headers)}

    def get_paginated_dicts(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int, offset: int = 0) -> tuple[list[dict[str,Any]], int]:
        """
        Return (rows, total)
        """
        paginated_sql, total_sql = self.get_paginated_and_total_sql(sql, limit=limit, offset=offset)
        rows = self.get_dicts(paginated_sql, params)
        total: int = self.get_scalar(total_sql, params) # type: ignore
        return rows, total
    
    def get_dicts(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> list[dict[str,Any]]:
        return [result for result in self.iter_dicts(sql, params, limit=limit, offset=offset)]
    
    def get_dict(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> dict[str,Any]|None:
        iterator = self.iter_dicts(sql, params, limit=limit, offset=offset)
        return next(iterator, None)
    
    def single_dict(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> dict[str,Any]:
        iterator = self.iter_dicts(sql, params, limit=limit, offset=offset)
        
        try:
            result = next(iterator)
        except StopIteration:
            raise NotFound()
        
        try:
            next(iterator)
            raise SeveralFound()
        except StopIteration:
            return result
        
    # ---------- Tuples ----------
    
    def iter_rows(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> Generator[tuple, Any, None]:
        with ResultManager(self, sql, params, limit=limit, offset=offset) as result:
            for row in result:
                yield row

    def get_paginated_rows(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int, offset: int = 0) -> tuple[list[tuple], int]:
        """
        Return (rows, total)
        """
        paginated_sql, total_sql = self.get_paginated_and_total_sql(sql, limit=limit, offset=offset)
        rows = self.get_rows(paginated_sql, params)
        total: int = self.get_scalar(total_sql, params) # type: ignore
        return rows, total

    def get_rows(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> list[tuple]:
        return [result for result in self.iter_rows(sql, params, limit=limit, offset=offset)]
    
    def get_row(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> tuple|None:
        iterator = self.iter_rows(sql, params, limit=limit, offset=offset)
        return next(iterator, None)
                
    def single_row(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> tuple:
        iterator = self.iter_rows(sql, params, limit=limit, offset=offset)
        
        try:
            result = next(iterator)
        except StopIteration:
            raise NotFound()
        
        try:
            next(iterator)
            raise SeveralFound()
        except StopIteration:
            return result
        
    # ---------- Scalars ----------
    
    @overload
    def iter_scalars(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type[T], notnull: Literal[True]) -> Generator[T, Any, None]:
        ...
    
    @overload
    def iter_scalars(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type[T], notnull: Literal[False] = False) -> Generator[T|None, Any, None]:
        ...
    
    @overload
    def iter_scalars(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: None = None, notnull = False) -> Generator[Any|None, Any, None]:
        ...

    def iter_scalars(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type|None = None, notnull = False) -> Generator[Any|None, Any, None]:
        with ResultManager(self, sql, params, limit=limit, offset=offset) as result:
            for row in result:
                if len(row) > 1:
                    raise ValueError(f"Result rows have {len(row)} columns")
                if len(row) == 0:
                    raise ValueError(f"Result rows have no column")
                value = row[0]
                if type is not None:
                    value = convert(value, type)
                if notnull and value is None:
                    raise ValueError(f"Result scalar is null")
                yield value

    @overload
    def get_scalars(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type[T], notnull: Literal[True]) -> list[T]:
        ...
    
    @overload
    def get_scalars(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type[T], notnull: Literal[False] = False) -> list[T|None]:
        ...
    
    @overload
    def get_scalars(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: None = None, notnull = False) -> list[Any|None]:
        ...

    def get_scalars(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type|None = None, notnull = False) -> list[Any|None]:
        return [value for value in self.iter_scalars(sql, params, limit=limit, offset=offset, type=type, notnull=notnull)]
    
    @overload
    def get_scalar(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type[T], notnull: Literal[True]) -> T:
        ...
    
    @overload
    def get_scalar(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type[T], notnull: Literal[False] = False) -> T|None:
        ...
    
    @overload
    def get_scalar(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: None = None, notnull = False) -> Any|None:
        ...

    def get_scalar(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type|None = None, notnull = False) -> Any|None:
        iterator = self.iter_scalars(sql, params, limit=limit, offset=offset, type=type, notnull=notnull)
        return next(iterator, None)

    @overload
    def single_scalar(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type[T], notnull: Literal[True]) -> T:
        ...
    
    @overload
    def single_scalar(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type[T], notnull: Literal[False] = False) -> T|None:
        ...
    
    @overload
    def single_scalar(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: None = None, notnull = False) -> Any|None:
        ...

    def single_scalar(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, type: type|None = None, notnull = False) -> Any|None:
        iterator = self.iter_scalars(sql, params, limit=limit, offset=offset, type=type, notnull=notnull)
        
        try:
            result = next(iterator)
        except StopIteration:
            raise NotFound()
        
        try:
            next(iterator)
            raise SeveralFound()
        except StopIteration:
            return result
    
    #endregion


    #region Queries and types

    str_sql_type = 'text'
    varstr_sql_type_pattern = 'character varying(%(max_length)d)'
    list_sql_type = 'json' # Use 'visual' for easy-to-read-and-parse text values, and '%(type)s[]' for a typed postgresql array
    dict_sql_type = 'json' # Use 'visual' for easy-to-read-and-parse text values
    bool_sql_type = 'boolean'
    int_sql_type = 'bigint'
    uuid_sql_type = 'uuid'
    float_sql_type = 'double precision'
    decimal_sql_type = 'character varying(66)'
    vardecimal_sql_type_pattern: str|None = 'decimal(%(precision)d,%(scale)d)'
    datetime_sql_type = 'timestamp with time zone'
    date_sql_type = 'date'
    sql_type_catalog_by_id: dict[int, tuple[str,type|None]] = {}
    sql_type_catalog_by_name: dict[str,type|None] = {}

    _identifier_quotechar_begin = '"'
    _identifier_quotechar_end = '"'
    _only_positional_params = False
    _split_multi_statement_scripts = False
    _accept_aware_datetimes = False
    _start_transaction_sql = 'START TRANSACTION'
    
    _pos_placeholder = '%s'
    _name_placeholder = '%%(%s)s'
    _identity_sql = 'IDENTITY'

    @classmethod
    def get_python_type(cls, sql_type: str|int|type|Column|None) -> type|None:
        """
        Get the Python type from a SQL type expressed either as a string, or as an integer (oid in type catalog, for postgresql and mariadb)
        """
        if isinstance(sql_type, Column):
            column = sql_type
            if column._python_type:
                return column._python_type
            sql_type = column.type
        else:
            column = None

        if sql_type is None:
            return None
        elif isinstance(sql_type, type):
            return sql_type
        
        if isinstance(sql_type, int):
            if cls.sql_type_catalog_by_id is None:
                raise ValueError("Missing sql_type_catalog_by_id")
            if sql_type in cls.sql_type_catalog_by_id:
                python_type = cls.sql_type_catalog_by_id[sql_type][1]
            else:
                python_type = None
        elif not isinstance(sql_type, str):
            raise TypeError(f"sql_type: {type(sql_type)}")
        else:
            sql_type = sql_type.lower()
            if cls.sql_type_catalog_by_name is not None and sql_type in cls.sql_type_catalog_by_name:
                python_type = cls.sql_type_catalog_by_name[sql_type]
            else:            
                # Simple heuristic compatible with sqlite (see 3.1: Determination Of Column Affinity in https://www.sqlite.org/datatype3.html)
                if 'int' in sql_type:
                    python_type = int
                elif 'char' in sql_type or 'clob' in sql_type or 'text' in sql_type:
                    python_type = str
                elif 'real' in sql_type or 'floa' in sql_type or 'doub' in sql_type:
                    python_type = float
                else:
                    python_type = None
        
        if column:
            column._python_type = python_type
        return python_type

    @classmethod
    def get_sql_type(cls, python_type: str|int|type|Column|None, key: bool|float = False) -> str:
        """
        :param key: indicate whether the column is part of a key (primary or unique). If this is a float, indicate the ratio of the max size of a key to use (for multi column keys).
        """
        precision: int|None = None
        scale: int|None = None
        if isinstance(python_type, Column):
            column = python_type
            if column.type is None:
                python_type = str
            elif isinstance(column.type, type):
                python_type = column.type
                precision = column.precision
                scale = column.scale
            else:
                return column.type

        if isinstance(python_type, str):
            return python_type.lower()
        elif isinstance(python_type, int):
            if cls.sql_type_catalog_by_id is None:
                raise ValueError("Missing sql_type_catalog_by_id")
            if python_type in cls.sql_type_catalog_by_id:
                return cls.sql_type_catalog_by_id[python_type][0]
            else:
                raise ValueError(f"Unknown type name for type ip {python_type}")
        elif not isinstance(python_type, type):
            raise TypeError(f"python_type: {type(python_type)}")
        
        if not issubclass(python_type, str):
            if issubclass(python_type, bool):
                return cls.bool_sql_type
            elif issubclass(python_type, int):
                return cls.int_sql_type
            elif issubclass(python_type, UUID):
                return cls.uuid_sql_type
            elif issubclass(python_type, float):
                return cls.float_sql_type
            elif issubclass(python_type, Decimal):
                if cls.vardecimal_sql_type_pattern and precision is not None and scale is not None:
                    return cls.vardecimal_sql_type_pattern % {'precision': precision, 'scale': scale}
                else:
                    return cls.decimal_sql_type
            elif issubclass(python_type, datetime):
                return cls.datetime_sql_type
            elif issubclass(python_type, date):
                return cls.date_sql_type
            elif issubclass(python_type, Mapping):
                if cls.dict_sql_type == 'visual':
                    return cls.str_sql_type
                else:
                    return cls.dict_sql_type
            elif issubclass(python_type, (Sequence,Set)):
                if cls.list_sql_type == 'visual':
                    return cls.str_sql_type
                elif '%(type)s' in cls.list_sql_type:
                    element_type = get_element_type(python_type)
                    if element_type:
                        return cls.list_sql_type % {'type': cls.get_sql_type(element_type)}
                    else:
                        return 'array' # SQL standard - See also: https://www.postgresql.org/docs/current/arrays.html#ARRAYS-DECLARATION
                else:
                    return cls.list_sql_type
        
        # use str
        if key:
            # type for key limited to 255 characters (max length for a 1-bit length VARCHAR on MariaDB)
            ratio = 1.0 if key is True else key
            return cls.varstr_sql_type_pattern % {'max_length': int(ratio * 255)}
        elif precision is not None:
            return cls.varstr_sql_type_pattern % {'max_length': precision}
        else:
            return cls.str_sql_type

    def get_python_value(self, value):
        if isinstance(value, datetime):
            if not value.tzinfo and self._tz:
                value = make_aware(value, self._tz)
        return value

    def get_sql_value(self, value: Any) -> Any:
        """
        Prepare a value so that it can be accepted as input by the database engine.
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, (Enum,Flag)):
            return value.value
        elif isinstance(value, datetime):
            if value.tzinfo:
                if self._accept_aware_datetimes:
                    return value
                elif self._tz:
                    return make_naive(value, self._tz)
                else:
                    raise ValueError(f"Input datetime may not be aware ('tz' not defined for {self.__class__.__name__} object and the database does not accept aware datetimes)")
            else:
                if self._tz:
                    return value
                else:
                    raise ValueError(f"Input datetime may not be naive ('tz' not defined for {self.__class__.__name__} object)")
        elif isinstance(value, Mapping):
            if self.dict_sql_type == 'visual':
                return get_visual_dict_str(value)
            else:
                return get_json_str(value)
        elif isinstance(value, (Sequence,Set)):
            if self.list_sql_type == 'visual':
                return get_visual_list_str(value)
            elif self.list_sql_type == 'array' or '[' in self.list_sql_type:
                return value
            else:
                return get_json_str(value)
        else:
            return value

    def get_now_sql(self):
        if self._tz:
            if self.tz == 'local':
                return self._get_local_now_sql()
            elif self.tz == 'utc':
                return self._get_utc_now_sql()
            else:
                raise NotSupportedBy('zut library', 'now sql for timezone other than local or utc')
        else:
            return self._get_aware_now_sql()

    def _get_aware_now_sql(self) -> str:
        if not self._accept_aware_datetimes:
            raise NotSupportedBy(self.__class__, 'now sql without specifying if timezone is local or utc')
        return "CURRENT_TIMESTAMP" # ANSI/ISO SQL: include the time zone information (when possible... which is not the case for MySQL and SqlServer)

    def _get_local_now_sql(self) -> str:
        return "CURRENT_TIMESTAMP" # ANSI/ISO SQL: include the time zone information (when possible... which is not the case for MySQL and SqlServer)
    
    def _get_utc_now_sql(self) -> str:
        return "CURRENT_TIMESTAMP AT TIME ZONE 'UTC'" # Not standard

    @classmethod
    def escape_identifier(cls, value: str|type|Column):
        if isinstance(value, type):
            value = value._meta.db_table
        elif isinstance(value, Column):
            value = value.name
        if not isinstance(value, str):
            raise TypeError(f"Invalid identifier: {value} ({type(value)})")
        return f"{cls._identifier_quotechar_begin}{value.replace(cls._identifier_quotechar_end, cls._identifier_quotechar_end+cls._identifier_quotechar_end)}{cls._identifier_quotechar_end}"

    @classmethod
    def escape_literal(cls, value) -> str:
        if value is None:
            return "null"
        elif isinstance(value, datetime):
            raise ValueError("Cannot use datetimes directly with `escape_literal`. Use `get_sql_value` first to remove timezone ambiguity.")
        else:
            return f"'" + str(value).replace("'", "''") + "'"
        
    def prepare_sql(self, sql: str, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> tuple[str, Mapping[str,Any]|Sequence[Any]|None]:
        if limit is not None or offset is not None:
            sql, _ = self.get_paginated_and_total_sql(sql, limit=limit, offset=offset)
    
        if isinstance(params, Mapping):
            if self._only_positional_params:
                sql, params = self._to_positional_params(sql, params)
            else:
                params = {name: self.get_sql_value(value) for name, value in params.items()}
                return sql, params
        
        if params is not None:
            params = [self.get_sql_value(value) for value in params]
        return sql, params
    
    @classmethod
    def prepare_file_sql(cls, file: str|os.PathLike, *, encoding = 'utf-8', **file_kwargs) -> str:
        sql = files.read_text(file, encoding=encoding)
        if file_kwargs:
            sql = sql.format(**{key: '' if value is None else value for key, value in file_kwargs.items()})
        return sql
    
    @classmethod
    def prepare_function_sql(cls, obj: str|tuple|DbObj, params: Mapping[str,Any]|Sequence[Any]|None = None, *, procedure = False) -> tuple[str, Sequence[Any]|None]:
        obj = cls.parse_obj(obj)
        if procedure:
            caller = cls._procedure_caller
            params_parenthesis = cls._procedure_params_parenthesis
        else:
            caller = 'SELECT'
            params_parenthesis = True
        
        sql = f"{caller} {obj.full_escaped if cls._function_requires_schema else obj.escaped}"
        
        if params_parenthesis:
            sql += "("
        else:
            sql += " "
                
        if isinstance(params, Mapping):
            list_params = []
            first = True
            for value in params:
                if not value:
                    raise ValueError(f"Parameter cannot be empty")
                elif not re.match(r'^[\w\d0-9_]+$', value): # for safety
                    raise ValueError(f"Parameter contains invalid characters: {value}")
                
                if first:
                    first = False
                else:
                    sql += ','

                sql += f'{value}={cls._pos_placeholder}'
                list_params.append(value)
            params = list_params
        elif params:
            sql += ','.join([cls._pos_placeholder] * len(params))
    
        if params_parenthesis:
            sql += ")"
        else:
            sql = sql.rstrip()

        return sql, params
    
    def get_paginated_and_total_sql(self, sql: str, *, limit: int|None, offset: int|None) -> tuple[str,str]:        
        if limit is not None:
            if isinstance(limit, str) and re.match(r"^[0-9]+$", limit):
                limit = int(limit)
            elif not isinstance(limit, int):
                raise TypeError(f"Invalid type for limit: {type(limit).__name__} (expected int)")
            
        if offset is not None:
            if isinstance(offset, str) and re.match(r"^[0-9]+$", offset):
                offset = int(offset)
            elif not isinstance(offset, int):
                raise TypeError(f"Invalid type for offset: {type(limit).__name__} (expected int)")
        
        beforepart, selectpart, orderpart = self._parse_select_sql(sql)

        paginated_sql = beforepart
        total_sql = beforepart
        
        paginated_sql += self._paginate_splited_select_sql(selectpart, orderpart, limit=limit, offset=offset)
        total_sql += f"SELECT COUNT(*) FROM ({selectpart}) s"

        return paginated_sql, total_sql

    def _parse_select_sql(self, sql: str):
        import sqlparse  # not at the top because the enduser might not need this feature
        from sqlparse.exceptions import SQLParseError

        # Parse SQL to remove token before the SELECT keyword
        # example: WITH (CTE) tokens
        statements = sqlparse.parse(sql)
        if len(statements) != 1:
            raise SQLParseError(f"SQL contains {len(statements)} statements")

        # Get first DML keyword
        dml_keyword = None
        dml_keyword_index = -1
        order_by_index = None
        for i, token in enumerate(statements[0].tokens):
            if token.ttype == sqlparse.tokens.DML:
                if dml_keyword is None:
                    dml_keyword = str(token).upper()
                    dml_keyword_index = i
            elif token.ttype == sqlparse.tokens.Keyword:
                if order_by_index is None:
                    keyword = str(token).upper()
                    if keyword == "ORDER BY":
                        order_by_index = i

        # Check if the DML keyword is SELECT
        if not dml_keyword:
            raise SQLParseError(f"Not a SELECT sql (no DML keyword found)")
        if dml_keyword != 'SELECT':
            raise SQLParseError(f"Not a SELECT sql (first DML keyword is {dml_keyword})")

        # Get part before SELECT (example: WITH)
        if dml_keyword_index > 0:
            tokens = statements[0].tokens[:dml_keyword_index]
            beforepart = ''.join(str(token) for token in tokens)
        else:
            beforepart = ''
    
        # Determine actual SELECT sql
        if order_by_index is not None:
            tokens = statements[0].tokens[dml_keyword_index:order_by_index]
            selectpart = ''.join(str(token) for token in tokens)
            tokens = statements[0].tokens[order_by_index:]
            orderpart = ''.join(str(token) for token in tokens)
        else:
            tokens = statements[0].tokens[dml_keyword_index:]
            selectpart = ''.join(str(token) for token in tokens)
            orderpart = ''

        return beforepart, selectpart, orderpart
    
    def _split_script(self, script: str, encoding: str) -> list[str]:
        if not self._split_multi_statement_scripts or not ';' in script:
            return [script]
            
        import sqlparse  # not at the top because the enduser might not need this feature
        return sqlparse.split(script, encoding)
    
    def _to_positional_params(self, sql: str, params: Mapping[str, Any]) -> tuple[str, Sequence[Any]]:
        from sqlparams import SQLParams  # (not at the top because the enduser might not need this feature)

        formatter: SQLParams
        try:
            formatter = getattr(self.__class__, '_params_formatter')
        except AttributeError:
            formatter = SQLParams('named', 'qmark')
            setattr(self.__class__, '_params_formatter', formatter)
        return formatter.format(sql, params) # type: ignore

    def _paginate_splited_select_sql(self, selectpart: str, orderpart: str, *, limit: int|None, offset: int|None) -> str:
        #NOTE: overriden for sqlserver
        result = f"{selectpart} {orderpart}"
        if limit is not None:
            result += f" LIMIT {limit}"
        if offset is not None:
            result += f" OFFSET {offset}"
        return result
    
    @classmethod
    def get_sqlutils_path(cls) -> Path|None:
        try:
            return cls._sqlutils_path
        except AttributeError:
            pass

        cls._sqlutils_path = Path(__file__).resolve().parent.joinpath('sqlutils', f"{cls.scheme}.sql")
        if not cls._sqlutils_path.exists():
            cls._sqlutils_path = None
        return cls._sqlutils_path

    #endregion


    #region Columns

    _can_add_several_columns = False

    def get_headers(self, obj: str|tuple|type|DbObj|Cursor) -> list[str]:
        if isinstance(obj, (str,tuple,type,DbObj)):
            table = self.parse_obj(obj)
            with self.execute_result(f"SELECT * FROM {table.escaped} WHERE 1 = 0") as result:
                return self.get_headers(result.cursor)
        else:
            if not obj.description:
                raise ValueError("No results in last executed sql (no cursor description available)")
            return [column[0] for column in obj.description]
    
    def get_columns(self, obj: str|tuple|type|DbObj|Cursor) -> list[Column]:
        if isinstance(obj, (str,tuple,type,DbObj)):
            table = self.parse_obj(obj)            
            if table.model:            
                return self.get_django_columns(table.model)            
            else:
                return self._get_table_columns(table)
        else:
            if not obj.description:
                raise ValueError("No results in last executed sql (no cursor description available)")
            return [self._get_cursor_column(name, type_info, display_size, internal_size, precision, scale, nullable) for name, type_info, display_size, internal_size, precision, scale, nullable in obj.description]
    
    def _get_table_columns(self, table: DbObj) -> list[Column]:
        raise NotImplementedBy(self.__class__)

    def get_django_columns(self, model: type[Model]) -> list[Column]:
        from django.db import models
        from django.db.models.fields import AutoFieldMixin
        from zut.django.fields import get_django_field_python_type

        columns = []

        field: models.Field
        for field in model._meta.fields:
            column = Column(field.attname)

            _type = get_django_field_python_type(field)
            if _type:
                column.type = _type
                if isinstance(field, models.DecimalField):
                    column.precision = field.max_digits
                    column.scale = field.decimal_places
                elif isinstance(field, models.CharField):
                    column.precision = field.max_length

            column.not_null = not field.null

            if field.primary_key:
                column.primary_key = True
            if isinstance(field, AutoFieldMixin):
                column.identity = True

            columns.append(column)

        return columns

    @classmethod
    def _get_cursor_column(cls, name: str, type_info: type|int|str|None, display_size: int|None, internal_size: int|None, precision: int|None, scale: int|None, nullable: bool|int|None) -> Column:
        if isinstance(type_info, int):
            if cls.sql_type_catalog_by_id is None:
                raise ValueError("Missing sql_type_catalog_by_id")
            if type_info in cls.sql_type_catalog_by_id:
                type_info = cls.sql_type_catalog_by_id[type_info][0]
            else:
                raise ValueError(f"Unknown type name for type ip {type_info}")

        if isinstance(nullable, int):
            if nullable == 1:
                nullable = True
            elif nullable == 0:
                nullable = False
        
        python_type = cls.get_python_type(type_info)
        if python_type != Decimal:
            scale = None
        
        return Column(name, type=type_info, precision=precision, scale=scale, not_null=not nullable if isinstance(nullable, bool) else None)
    
    def add_column(self, table: str|tuple|type|DbObj, columns: str|Column|Sequence[str|Column], *, ignore_decimal = False, ignore_not_null = False, loglevel = logging.DEBUG):
        """
        Add column(s) to a table.

        NOTE: This method does not intend to manage all cases, but only those usefull for zut library internals.
        """
        table = self.parse_obj(table)
        if isinstance(columns, (str,Column)):
            columns = [columns]

        if len(columns) > 1 and not self._can_add_several_columns:
            for column in columns:
                self.add_column(table, [column], ignore_decimal=ignore_decimal, ignore_not_null=ignore_not_null, loglevel=loglevel)
            return

        sql = f"ALTER TABLE {table.escaped} ADD "
        for i, column in enumerate(columns):
            if isinstance(column, Column):
                if column.primary_key:
                    raise NotSupportedBy('zut library', f"add primary key column: {column.name}")
                if column.identity:
                    raise NotSupportedBy('zut library', f"add identity column: {column.name}")
            sql += (',' if i > 0 else '') + self._get_column_sql(column, ignore_decimal=ignore_decimal, ignore_not_null=ignore_not_null)

        self._logger.log(loglevel, "Add column%s %s to table %s", ('s' if len(columns) > 1 else '', ', '.join(str(column) for column in columns)), table)        
        self.execute(sql)
    
    def alter_column_default(self, table: str|tuple|type|DbObj, columns: Column|Sequence[Column]|dict[str,Any], *, loglevel = logging.DEBUG):
        table = self.parse_obj(table)

        if isinstance(columns, Column):
            columns = [columns]
        elif isinstance(columns, dict):
            columns = [Column(name, default=value) for name, value in columns.items()]

        columns_sql = ''
        columns_names: list[str] = []
        only_drop = True
        for column in columns:
            columns_sql = (", " if columns_sql else "") + f"ALTER COLUMN {self.escape_identifier(column.name)} "
            if column.default is None:
                columns_sql += "DROP DEFAULT"
            else:
                columns_sql += f"SET DEFAULT {self._get_escaped_default_sql(column.default)}"
                only_drop = False
            columns_names.append(f'"{column.name}"')

        if not columns_sql:
            return
    
        sql = f"ALTER TABLE {table.escaped} {columns_sql}"

        self._logger.log(loglevel, "%s default for column%s %s of table %s", 'Drop' if only_drop else 'Alter', 's' if len(columns_names) > 1 else '', ', '.join(columns_names), table)
        self.execute(sql)

    def drop_column_default(self, table: str|tuple|type|DbObj, columns: str|Column|Sequence[str|Column], *, loglevel = logging.DEBUG):
        if isinstance(columns, (str,Column)):
            columns = [columns]
        
        columns_dict = {}
        for column in columns:
            columns_dict[column.name if isinstance(column, Column) else column] = None

        return self.alter_column_default(table, columns_dict, loglevel=loglevel)
    
    def _get_column_sql(self, column: str|Column, *, foreign_key: ForeignKey|None = None, single_primary_key = False, ignore_decimal = False, ignore_not_null = False):
        """ Add primary key only if `column.primary_key` and `single_primary_key` are both true. """
        if not isinstance(column, Column):
            column = Column(column)

        if ignore_decimal and column.type in {float, Decimal}:
            sql_type = self.varstr_sql_type_pattern % 66
        else:
            sql_type = self.get_sql_type(column)
            if ignore_decimal and column.type is not None and self.get_python_type(sql_type) in {float, Decimal}:
                sql_type = self.varstr_sql_type_pattern % 66
        
        if column.primary_key or column.identity:
            not_null = True
        elif ignore_not_null:
            not_null = False
        else:
            not_null = column.not_null
        
        sql = f"{self.escape_identifier(column.name)} {sql_type} {'NOT NULL' if not_null else 'NULL'}"

        if column.default is not None:
            sql += f" DEFAULT {self._get_escaped_default_sql(column.default)}"

        if column.primary_key and single_primary_key:
            sql += f" PRIMARY KEY"

        if column.identity:
            sql += f" {self._identity_sql}"

        if foreign_key:
            sql += " " + self._get_foreign_key_constraint_sql(foreign_key, for_column=column.name)

        return sql
    
    def _get_escaped_default_sql(self, default: Any|None):
        if isinstance(default, str):
            if default.lower() in {'now', 'now()'}:
                return self.get_now_sql()
            elif default.startswith('sql:'):
                return default[len('sql:'):]
        
        return self.escape_literal(default)
    
    def _parse_default_from_db(self, column: Column):
        if isinstance(column.default, str):
            if column.default == '(getdate())' or column.default == 'statement_timestamp()' or column.default == 'now()':
                column.default = self._get_local_now_sql()
            elif column.default == '(getutcdate())':
                column.default = self._get_utc_now_sql()
            else:
                m = re.match(r"^\((.+)\)$", column.default) # sqlserver-specific
                if m:
                    column.default = m[1]
                    m = re.match(r"^\((.+)\)$", column.default) # type: ignore   # second level (e.g. for integer value)
                    if m:
                        column.default = m[1]
                m = re.match(r"^'(.+)'(?:::[a-z0-9 ]+)?$", column.default) # type: ignore   # note: `::type` is postgresql-specific
                if m:
                    column.default = re.sub(r"''", "'", m[1]) # remove quotes

        target_type = self.get_python_type(column)
        if target_type and column.default not in {self._get_utc_now_sql(), self._get_local_now_sql()}:
            column.default = convert(column.default, target_type)
    
    #endregion


    #region Constraints

    def get_unique_keys(self, table: str|tuple|type|DbObj) -> list[UniqueKey]:
        table = self.parse_obj(table)
            
        if table.model:
            return self._get_django_unique_keys(table.model)
        else:
            return self._get_table_unique_keys(table)

    def _get_django_unique_keys(self, model: type[Model]) -> list[UniqueKey]:
            from django.db import models

            field_orders: dict[str,int] = {}
            attnames_by_fieldname: dict[str,str] = {}

            primary_key: list[str]|None = None
            unique_keys: list[UniqueKey] = []

            for i, field in enumerate(model._meta.fields):
                field_orders[field.attname] = i
                attnames_by_fieldname[field.name] = field.attname
                
                if field.primary_key:
                    if not primary_key:
                        primary_key = [field.attname]
                    else:
                        primary_key.append(field.attname)
                elif field.unique:
                    unique_keys.append(UniqueKey((field.attname,)))

            if primary_key:
                unique_keys.insert(0, UniqueKey(tuple(primary_key)))

            for names in model._meta.unique_together:
                unique_keys.append(UniqueKey(tuple(attnames_by_fieldname[name] for name in names)))

            for constraint in model._meta.constraints:
                if isinstance(constraint, models.UniqueConstraint):
                    unique_keys.append(UniqueKey(tuple(attnames_by_fieldname[name] for name in constraint.fields)))

            unique_keys.sort(key=lambda unique_key: tuple(field_orders[attname] for attname in unique_key.columns))
            
            return unique_keys

    def _get_table_unique_keys(self, table: DbObj) -> list[UniqueKey]:
        raise NotImplementedBy(self.__class__)

    def get_foreign_keys(self, table: str|tuple|type|DbObj, *, columns: Iterable[str]|None = None, recurse = False):
        """
        Return the list of foreign keys defined for the given table.

        :param table: Source of the foreign key relations.
        :param columns: If set, restrict the foreign key searching to the given columns.
        :param recurse: If True, check recursively if the related primary keys are themselves part of foreign keys (on the related models).
        """
        table = self.parse_obj(table)
        if table.model:
            return self._get_django_foreign_keys(table.model, columns=columns, recurse=recurse)
        else:
            return self._get_table_foreign_keys(table, columns=columns, recurse=recurse)
    
    def _get_django_foreign_keys(self, model: type[Model], *, columns: Iterable[str]|None, recurse: bool) -> list[ForeignKey]:        
        fks: list[ForeignKey] = []
        from django.db import models
        
        for field in model._meta.get_fields():
            if not isinstance(field, models.ForeignKey):
                continue

            column = field.attname
            if columns is not None and column not in columns:
                continue

            related_table = self.parse_obj(field.related_model)
            related_column = field.related_model._meta.pk.attname
            fk = self._build_foreign_key(related_table, {column: related_column}, recurse=recurse)
            fks.append(fk)

        return fks

    def _get_table_foreign_keys(self, table: DbObj, *, columns: Iterable[str]|None, recurse: bool) -> list[ForeignKey]:        
        fks: list[ForeignKey] = []

        rows_by_constraint_name: dict[str,list[dict[str,Any]]] = {}
        for row in self._get_table_foreign_key_descriptions(table):
            rows = rows_by_constraint_name.get(row['constraint_name'])
            if rows is None:
                rows_by_constraint_name[row['constraint_name']] = [row]
            else:
                rows.append(row)

        for rows in rows_by_constraint_name.values():
            if columns is not None:
                if not any(row['column_name'] in columns for row in rows):
                    continue # skip this foreign key

            related_table = self.parse_obj((rows[0]['related_schema'], rows[0]['related_table']))
            fk = self._build_foreign_key(related_table, {row['column_name']: row['related_column_name'] for row in rows}, recurse=recurse)
            fks.append(fk)
            
        return fks
        
    def _get_table_foreign_key_descriptions(self, table: DbObj) -> list[dict[str,Any]]:
        raise NotImplementedBy(self.__class__)

    def _build_foreign_key(self, related_table: DbObj, columns: dict[str, str], *, recurse: bool) -> ForeignKey:
        if recurse:
            sub_fks_by_column = {}
            for sub_fk in self.get_foreign_keys(related_table, columns=columns.values(), recurse=True):
                for column in sub_fk.columns:
                    sub_fks_by_column[column] = sub_fk
            columns = {column: sub_fks_by_column.get(related_column, related_column) for column, related_column in columns.items()}
        return ForeignKey(related_table, columns)

    def get_reversed_foreign_keys(self, columns: Iterable[str], table: str|tuple|type|DbObj, *, recurse = False) -> list[ForeignKey]:
        table = self.parse_obj(table)

        reversed_fks = []
        for fk in self.get_foreign_keys(table):
            fk_columns = [column for column in columns if column.startswith(f'{fk.basename}_')]
            if not fk_columns:
                continue

            reversed_fk_columns = {}
            for column in fk_columns:
                suffix = column[len(f'{fk.basename}_'):] if column.startswith(f'{fk.basename}_') else column
                reversed_fk_columns[suffix] = suffix
            
            if recurse:
                sub_reversed_fks_by_column = {}
                for sub_reversed_fk in self.get_reversed_foreign_keys(reversed_fk_columns.values(), fk.related_table, recurse=True):
                    for column in sub_reversed_fk.columns:
                        sub_reversed_fks_by_column[column] = sub_reversed_fk
                reversed_fk_columns = {column: sub_reversed_fks_by_column.get(column, column) for column in reversed_fk_columns}

            reversed_fk = ForeignKey(fk.related_table, reversed_fk_columns, basename=fk.basename)
            reversed_fks.append(reversed_fk)

        return reversed_fks

    #endregion


    #region Tables

    _truncate_with_delete = False
    _can_cascade_truncate = False

    strict_types: bool
    """ For sqlite. """

    @classmethod
    def parse_obj(cls, input: str|tuple|type|DbObj) -> DbObj:
        return DbObj.parse(cls, input)
    
    def get_random_table_name(self, prefix: str|None = None, *, schema = None, temp: bool|None = None):
        if temp is None:
            if schema == 'temp' or schema == self._temp_schema:
                temp = True
            elif prefix and prefix.lower().startswith(('tmp', 'temp')):
                temp = True

        if schema is None:
            if temp:
                schema = self._temp_schema if self._temp_schema else 'temp'

        if prefix is None:
            prefix = 'tmp_' if temp else 'rnd_'
                
        while True:
            table = self.parse_obj((schema, f'{prefix}{token_hex(8)}'[:63]))
            if not self.table_exists(table):
                return table
    
    def table_exists(self, table: str|tuple|type|DbObj) -> bool:
        raise NotImplementedBy(self.__class__)

    def create_table(self, table: str|tuple|type|DbObj, columns: Iterable[str|Column]|Mapping[str,str|type|Column], *,
            if_not_exists = False,
            primary_key: str|bool = False,
            unique_keys: Iterable[str|Sequence[str]|UniqueKey]|None = None,
            foreign_keys: Sequence[ForeignKey]|dict[str, str]|None = None,
            ignore_decimal = False,
            ignore_not_null = False,
            merge_status_columns: bool|None = None,                    
            inserted_at_column: str|None = None,
            updated_at_column: str|None = None,
            changed_at_column: str|None = None,
            error_code_column : str|None = None,
            error_arg_column : str|None = None,
            absent_at_column: str|None = None,
            sql_attributes: str|Sequence[str]|None = None) -> list[Column]:
        """
        Create a table with the given columns.

        :param sql_attribute: Attributes to be appended at the end of the table. For example, `STRICT` (for SQLite) or `ENGINE=MEMORY` (for MySQL/MariaDB)
        """

        # Analyze arguments
        table = self.parse_obj(table)
        _unique_keys = [UniqueKey(unique_key) if not isinstance(unique_key, UniqueKey) else unique_key for unique_key in unique_keys] if unique_keys else []

        columns_mapping: dict[str,Column]
        if isinstance(columns, Mapping):
            columns_mapping = {}
            for name, column in columns.items():
                if isinstance(name, Column):
                    name = name.name
                if isinstance(column, Column):
                    column.name = name
                elif isinstance(column, (str,type)):
                    column = Column(name, type=column)
                else:
                    raise ValueError(f"Invalid mapping type for column {name}: {type(column).__name__}")
                columns_mapping[name] = column
        else:
            columns_mapping = {}
            for column in columns:
                if not isinstance(column, Column):
                    column = Column(column)
                columns_mapping[column.name] = column

        primary_key_columns = [column for column in columns_mapping.values() if column.primary_key]

        UniqueKeyColumnInfo = NamedTuple('UniqueKeyColumnInfo', [('max_key_length', int), ('is_single_key', bool)])

        unique_info_by_column: dict[str, UniqueKeyColumnInfo] = {}
        for unique_key in _unique_keys:
            key_length = len(unique_key.columns)
            is_single_key = key_length == 1
            for column in unique_key.columns:
                info = unique_info_by_column.get(column)
                if info is not None:
                    if key_length > info.max_key_length or is_single_key and not info.is_single_key:
                        unique_info_by_column[column] = UniqueKeyColumnInfo(key_length, is_single_key)
                else:
                    unique_info_by_column[column] = UniqueKeyColumnInfo(key_length, is_single_key)

        single_foreign_key_by_column: dict[str, ForeignKey] = {}
        remaining_foreign_keys: list[ForeignKey] = []
        if isinstance(foreign_keys, dict):
            foreign_keys = [ForeignKey(related_table, {column: 'id'}) for column, related_table in foreign_keys.items()]
        if foreign_keys:
            for foreign_key in foreign_keys:
                if len(foreign_key.columns) == 1:
                    column = list(foreign_key.columns.keys())[0]
                    if column in single_foreign_key_by_column:
                        previous_foreign_key = single_foreign_key_by_column.pop(column)
                        remaining_foreign_keys.append(previous_foreign_key)
                    else:
                        single_foreign_key_by_column[column] = foreign_key
                else:
                    remaining_foreign_keys.append(foreign_key)

        # Complete the list of columns
        all_columns = list(columns_mapping.values())

        if primary_key:
            if not primary_key_columns:
                # Create an autoincrement primary key if no id field is present
                if primary_key is True:
                    primary_key = 'id'
                if not primary_key in columns_mapping:
                    column = Column(primary_key, type=int, not_null=True, primary_key=True, identity=True)
                    primary_key_columns.append(column)
                    all_columns.insert(0, column)
            elif isinstance(primary_key, str):
                if not any(column.name == primary_key for column in primary_key_columns):
                    raise ValueError(f"Primary key does not contain column {primary_key}: {', '.join(column.name for column in primary_key_columns)}")

        # Prepare columns_sql
        columns_sql = ""

        if len(primary_key_columns) == 1:
            column = primary_key_columns[0]
            column.not_null = True
            column.type = self.get_sql_type(column, key=True)
            columns_sql += ("\n    ," if columns_sql else "") + self._get_column_sql(column, single_primary_key=True, foreign_key=single_foreign_key_by_column.get(column.name), ignore_decimal=ignore_decimal, ignore_not_null=ignore_not_null)
            columns_mapping.pop(column.name, None)

        for column in columns_mapping.values():
            unique_key_info = unique_info_by_column.get(column.name)
            key_ratio = False
            if unique_key_info is not None:
                key_ratio = 1.0 / unique_key_info.max_key_length
            elif column.name in primary_key_columns:
                key_ratio = 1.0            
            column.type = self.get_sql_type(column, key=key_ratio)
            columns_sql += ("\n    ," if columns_sql else "") + self._get_column_sql(column, foreign_key=single_foreign_key_by_column.get(column.name), ignore_decimal=ignore_decimal, ignore_not_null=ignore_not_null)

        if merge_status_columns is not False:
            additional_columns: list[Column] = []

            if merge_status_columns or inserted_at_column:
                if not inserted_at_column:
                    inserted_at_column = self.inserted_at_column
                if inserted_at_column:
                    additional_columns.append(Column(inserted_at_column, type=datetime, not_null=True, default='now'))

            if merge_status_columns or updated_at_column:
                if not updated_at_column:
                    updated_at_column = self.updated_at_column
                if updated_at_column:
                    additional_columns.append(Column(updated_at_column, type=datetime, not_null=True, default='now'))

            if merge_status_columns or changed_at_column:
                if not changed_at_column:
                    changed_at_column = self.changed_at_column
                if changed_at_column:
                    additional_columns.append(Column(changed_at_column, type=datetime, not_null=True, default='now'))

            if merge_status_columns or error_code_column:
                if not error_code_column:
                    error_code_column = self.error_code_column
                if error_code_column:
                    additional_columns.append(Column(error_code_column, type='smallint'))

            if merge_status_columns or error_arg_column:
                if not error_arg_column:
                    error_arg_column = self.error_arg_column
                if error_arg_column:
                    additional_columns.append(Column(error_arg_column, type=str))

            if merge_status_columns or absent_at_column:
                if not absent_at_column:
                    absent_at_column = self.absent_at_column
                if absent_at_column:
                    additional_columns.append(Column(absent_at_column, type=datetime, default='now'))

            for column in additional_columns:
                all_columns.append(column)
                columns_sql += ("\n    ," if columns_sql else "") + self._get_column_sql(column, foreign_key=single_foreign_key_by_column.get(column.name))

        # Prepare constraints_sql
        constraints_sql = ''

        if len(primary_key_columns) > 1:
            constraints_sql += ("\n    ," if constraints_sql else "") + f"PRIMARY KEY (" + ', '.join(self.escape_identifier(column) for column in primary_key_columns) + ")"

        for unique_key in _unique_keys:
            constraints_sql += ("\n    ," if constraints_sql else "") + "UNIQUE"
            if unique_key.nulls:
                if unique_key.nulls == 'not-distinct':
                    constraints_sql += " NULLS NOT DISTINCT"
                elif unique_key.nulls == 'distinct':
                    constraints_sql += " NULLS DISTINCT" # This is the default
                else:
                    raise ValueError(f"Invalid nulls value '{unique_key.nulls}' for {unique_key}")
            
            constraints_sql += " (" + ', '.join(self.escape_identifier(column) for column in unique_key.columns) + ")"

        for foreign_key in remaining_foreign_keys:
            constraints_sql += ("\n    ," if constraints_sql else "") + self._get_foreign_key_constraint_sql(foreign_key)

        # Finalize
        sql = "CREATE"
        if table.temp and self.scheme != 'sqlserver':
            sql += f" TEMPORARY TABLE {self.escape_identifier(table.name)}"
        else:
            sql += f" TABLE {table.escaped}"
        if if_not_exists:
            sql += " IF NOT EXISTS"
        sql += " ("
        sql += f"\n    {columns_sql}"
        if constraints_sql:
            sql += f"\n    ,{constraints_sql}"
        sql += "\n)"

        # Attributes
        if sql_attributes is None:
            if self.scheme == 'sqlite' and self.strict_types:
                sql_attributes = ["STRICT"]
            else:
                sql_attributes = []
        elif isinstance(sql_attributes, str):
            sql_attributes = [sql_attributes]

        for sql_attribute in sql_attributes:
            sql += f" {sql_attribute}"

        self._logger.debug("Create%s table %s%s\n%s", ' temp' if table.temp else '', table, " (if not exists)" if if_not_exists else "", sql)
        self.execute(sql)
        return all_columns

    def drop_table(self, table: str|tuple|type|DbObj, *, if_exists = False):
        table = self.parse_obj(table)
        
        sql = "DROP TABLE "
        if if_exists:
            sql += "IF EXISTS "
        sql += table.escaped

        self._logger.debug("Drop table %s%s", table, " (if exists)" if if_exists else "")
        self.execute(sql)
    
    def clear_table(self, table: str|tuple|type|DbObj, *, truncate: bool|Literal['cascade'] = False, if_exists = False, loglevel = logging.DEBUG):
        table = self.parse_obj(table)

        if if_exists:
            if not self.table_exists(table):
                return
        
        if not truncate or self._truncate_with_delete:
            sql = "DELETE FROM "
        else:
            sql = "TRUNCATE TABLE "
        
        sql += table.escaped

        if truncate == 'cascade':
            if not self._can_cascade_truncate:
                raise NotSupportedBy(self.__class__, "cascade truncate")
            sql += " CASCADE"
        
        self._logger.log(loglevel, "Clear table %s", table)
        self.execute(sql)

    def _get_foreign_key_constraint_sql(self, foreign_key: ForeignKey, *, for_column: str|None = None):
        if for_column is not None:            
            if len(foreign_key.columns) != 1 or not for_column in foreign_key.columns:
                raise ValueError(f"Invalid foreign key ({', '.join(foreign_key.columns.keys())}): not for column {for_column}")
            constraint_sql = ""
        else:
            constraint_sql = "FOREIGN KEY (" + ', '.join(self.escape_identifier(column) for column in foreign_key.columns.keys()) + ") "

        constraint_sql += f"REFERENCES {foreign_key.related_table.escaped} (" + ', '.join(self.escape_identifier('id' if isinstance(column, ForeignKey) else column) for column in foreign_key.columns.values()) + ")"
        return constraint_sql

    #endregion


    #region Schemas

    _default_schema: str|None
    _temp_schema: str|None
    
    def schema_exists(self, name: str) -> bool:        
        if self._default_schema is None:
            raise NotSupportedBy(self.__class__, 'schemas')
        raise NotImplementedBy(self.__class__)

    def create_schema(self, name: str, *, if_not_exists = False, loglevel = logging.DEBUG) -> None:
        if self._default_schema is None:
            raise NotSupportedBy(self.__class__, 'schemas')

        sql = "CREATE SCHEMA "
        if if_not_exists:
            sql += "IF NOT EXISTS "
        sql += f"{self.escape_identifier(name)}"
        
        self._logger.log(loglevel, "Create schema %s%s", name, " (if not exists)" if if_not_exists else "")
        self.execute(sql)

    def drop_schema(self, name: str, *, if_exists = False, loglevel = logging.DEBUG) -> None:
        if self._default_schema is None:
            raise NotSupportedBy(self.__class__, 'schemas')
        
        sql = "DROP SCHEMA "
        if if_exists:
            sql += "IF EXISTS "
        sql += f"{self.escape_identifier(name)}"
        
        self._logger.log(loglevel, "Drop schema %s%s", name, " (if exists)" if if_exists else "")
        self.execute(sql)
    
    #endregion


    #region Databases

    def get_database_name(self) -> str|None:
        """
        Return the name of the database currently associated with this connection.

        NOTE:
        - This can be distinct from this class instance attribute `name` a statement such as `USE` has been executed.
        - This can be None for mysql and mariadb.
        """
        raise NotImplementedBy(self.__class__)
    
    def use_database(self, name: str) -> None:
        sql = f"USE {self.escape_identifier(name)}"
        self.execute(sql)

    def database_exists(self, name: str) -> bool:
        raise NotImplementedBy(self.__class__)

    def create_database(self, name: str, *, if_not_exists = False, loglevel = logging.DEBUG) -> None:
        sql = f"CREATE DATABASE "
        if if_not_exists:
            sql += "IF NOT EXISTS "
        sql += self.escape_identifier(name)

        self._logger.log(loglevel, "Create database %s%s", name, " (if not exists)" if if_not_exists else "")
        self.execute(sql)

    def drop_database(self, name: str, *, if_exists = False, loglevel = logging.DEBUG) -> None:
        sql = f"DROP DATABASE "
        if if_exists:
            sql += "IF EXISTS "
        sql += self.escape_identifier(name)

        self._logger.log(loglevel, "Drop database %s%s", name, " (if exists)" if if_exists else "")
        self.execute(sql)

    #endregion


    #region Migrations

    def migrate(self, dir: str|os.PathLike, *, no_sqlutils = False, **file_kwargs):        
        last_name = self.get_last_migration_name()

        if last_name is None:
            if not no_sqlutils:
                sqlutils = self.get_sqlutils_path()
                if sqlutils:
                    self._logger.info("Deploy SQL utils ...")
                    self.execute_file(sqlutils)

            self._logger.info("Create migration table ...")
            self.execute(f"CREATE TABLE _migration(id {self.int_sql_type} NOT NULL PRIMARY KEY {self._identity_sql}, name {self.get_sql_type(str, key=True)} NOT NULL UNIQUE, deployed_at {self.datetime_sql_type} NOT NULL)")
            last_name = ''
        
        for path in sorted((dir if isinstance(dir, Path) else Path(dir)).glob('*.sql')):
            if path.stem == '' or path.stem.startswith('~') or path.stem.endswith('~'):
                continue # skip
            if path.stem > last_name:
                self._apply_migration(path, **file_kwargs)

        self.commit()

    def _apply_migration(self, path: Path, **file_kwargs):
        self._logger.info("Apply migration %s ...", path.stem)

        self.execute_file(path, **file_kwargs)

        _previous_tz = self._tz
        try:
            if self._accept_aware_datetimes or self._tz:
                deployed_at = self.get_sql_value(now_aware())
            else:
                self._tz = timezone.utc # Make the library temporary accept a naive timezone - Only for migration table purpose.
                deployed_at = self.get_sql_value(now_naive(self._tz))
            self.execute(f"INSERT INTO _migration (name, deployed_at) VALUES({self._pos_placeholder}, {self._pos_placeholder})", [path.stem, deployed_at])
        finally:
            self._tz = _previous_tz

    def get_last_migration_name(self) -> str|None:
        if not self.table_exists("_migration"):
            return None
        
        try:
            return self.get_scalar("SELECT name FROM _migration ORDER BY name DESC", limit=1)
        except NotFound:
            return ''

    #endregion


    #region Load and merge

    inserted_at_column: str|None = None
    updated_at_column: str|None = None
    changed_at_column: str|None = None
    error_code_column : str|None = None
    error_arg_column : str|None = None
    absent_at_column: str|None = None
    delete_on_absent: bool|int|None = None

    _merge_statement = False
    """ Indicate whether the MERGE standard command is available (see https://modern-sql.com/caniuse/merge) """
    
    def copy_csv(self, file: str|os.PathLike|IO[str], table: str|tuple|type|DbObj, columns: Iterable[str|Column]|None = None, *,
            delimiter: str|None = None,
            newline: str|None = None,
            encoding = 'utf-8') -> int:
        """
        Insert data from a CSV file directly to a table without performing any check or conversion.
        """

        raise NotImplementedBy(self.__class__)
    
    def load_csv(self, file: str|os.PathLike|IO[str], table: str|tuple|type|DbObj|None = None, columns: Iterable[str|Column|Literal['*']]|Mapping[str,str|type|Column|Literal['*']]|None = None, *,
            create_table_if_not_exists: bool|None = None,
            slugify_columns: Callable[[str],str]|bool = False,
            encoding='utf-8',
            # Merge options
            key: str|Sequence[str]|UniqueKey|None = None,
            inserted_at_column: bool|str|None = None,
            updated_at_column: bool|str|None = None,
            changed_at_column: bool|str|None = None,
            error_code_column : bool|str|None = None,
            error_arg_column : bool|str|None = None,
            absent_at_column: bool|str|None = None,
            delete_on_absent: bool|int|None = None) -> MergeResult:

        from zut.db.operations.load import LoadOperation

        op = LoadOperation(self, file, table, columns,
            create_table_if_not_exists = create_table_if_not_exists,
            slugify_columns = slugify_columns,
            encoding = encoding,
            # Merge options
            key = key,
            inserted_at_column = inserted_at_column,
            updated_at_column = updated_at_column,
            changed_at_column = changed_at_column,
            error_code_column = error_code_column,
            error_arg_column = error_arg_column,
            absent_at_column = absent_at_column,
            delete_on_absent = delete_on_absent)
        
        return op.run()

    def merge_tables(self, src_table: str|tuple|type|DbObj, dst_table: str|tuple|type|DbObj, columns: Iterable[str|Column|Literal['*']]|Mapping[str,str|type|Column|Literal['*']]|None = None, *,
            key: str|Sequence[str]|UniqueKey,
            inserted_at_column: bool|str|None = None,
            updated_at_column: bool|str|None = None,
            changed_at_column: bool|str|None = None,
            error_code_column : bool|str|None = None,
            error_arg_column : bool|str|None = None,
            absent_at_column: bool|str|None = None,
            delete_on_absent: bool|int|None = None
            ) -> MergeResult:
        
        from zut.db.operations.merge import MergeOperation

        op = MergeOperation(self, src_table, dst_table, columns,
            key = key,
            inserted_at_column = inserted_at_column,
            updated_at_column = updated_at_column,
            changed_at_column = changed_at_column,
            error_code_column = error_code_column,
            error_arg_column = error_arg_column,
            absent_at_column = absent_at_column,
            delete_on_absent = delete_on_absent)

        return op.run()

    def _get_convert_str_sql(self, column: Column, *, name: str|None = None, alias: str|None = None):
        if name is None:
            name = column.name
        identifier_sql = (alias if alias else '') + self.escape_identifier(name)

        python_type = self.get_python_type(column)
        if python_type != str:
            sql_type = self.get_sql_type(column)
            return f"CAST({identifier_sql} AS {sql_type})"
        else:
            return identifier_sql

    #endregion


#region Db param and results

class DbObj:
    """
    Identify a database object (table, view, procedure, etc). Mostly for internal usage. For external applications, advise is to use tuple (`schema`, `table`).
    """

    db: type[Db]
    """ Type of the database (used for escaping). """

    schema: str|None
    """ Schema of the object. """

    name: str
    """ Name of the object. """

    temp: bool
    """ Indicate whether the table is temporary. """ 

    model: type[Model]|None = None
    """ Django model associated to the table, if known. """

    def __init__(self, db: type[Db], schema: str|None, name: str, model: type[Model]|None = None):
        self.db = db
        self.schema = schema
        self.name = name
        self.model = model

        m = re.match(r'^(.+)\.([^\.]+)$', self.name)
        if m:
            if self.schema:
                self.name = m[2] # Schema given specifically overrides schema given within the name - Usage example: force temp schema.
            else:
                self.schema = m[1]
                self.name = m[2]

        if self.db._temp_schema == 'pg_temp' and self.schema is not None and self.schema.startswith('pg_temp_'): # pg
            self.schema = self.db._temp_schema
            self.temp = True
        elif self.schema == 'temp':
            self.temp = True
            if self.db._temp_schema == '#': # sqlserver
                self.schema = None
                self.name = f'#{self.name}'
            elif self.db._temp_schema:
                self.schema = self.db._temp_schema
            else:
                self.schema = None
        elif self.db._temp_schema == '#' and self.name.startswith('#'): # sqlserver
            self.temp = True
        elif self.schema and self.schema == self.db._temp_schema:
            self.temp = True
        else:
            self.temp = False

    def __str__(self):
        return self.escaped
    
    @cached_property
    def escaped(self) -> str:
        return f"{f'{self.db.escape_identifier(self.schema)}.' if self.schema else ''}{self.db.escape_identifier(self.name)}"
    
    @cached_property
    def full_escaped(self) -> str:
        """ Include the db default schema if none is given. """
        if self.schema:
            schema = self.schema
        else:
            schema = self.db._default_schema            
        return f"{f'{self.db.escape_identifier(schema)}.' if schema else ''}{self.db.escape_identifier(self.name)}"
    
    @cached_property
    def unsafe(self) -> str:
        return (f'{self.schema}.' if self.schema else '') + self.name
    
    @classmethod
    def parse(cls, db: type[Db]|Db, input: str|tuple|type|DbObj) -> DbObj:
        if not isinstance(db, type):
            db = type(db)

        if isinstance(input, DbObj):
            if input.db != db:
                return DbObj(db, input.schema, input.name, input.model)
            else:
                return input
        elif isinstance(input, tuple):
            return DbObj(db, input[0], input[1])
        elif isinstance(input, str):
            m = re.match(r'^(.+)\.([^\.]+)$', input)
            if m:
                return DbObj(db, m[1], m[2])
            else:
                return DbObj(db, None, input)
        else:
            meta = getattr(input, '_meta', None) # Django model
            if meta:
                if not isinstance(input, type):
                    input = input.__class__
                return DbObj(db, None, meta.db_table, input)
            else:
                raise TypeError(f'input: {type(input).__name__}')


class ResultManager:
    next_num = 1

    def __init__(self, db: Db, sql: str|None = None, params: Mapping[str,Any]|Sequence[Any]|None = None, *, limit: int|None = None, offset: int|None = None, source: str|None = None, warn_if_result: bool|int|Literal['not-last'] = False):
        self.db = db
        self.source = source

        self.sql = sql
        self.params = params
        self.limit = limit
        self.offset = offset

        self.num = self.__class__.next_num
        self.__class__.next_num += 1

        self._warn_if_result: bool|Literal['not-last']
        if isinstance(warn_if_result, int) and not isinstance(warn_if_result, bool):
            self._warn_max_rows = warn_if_result
            self._warn_if_result = True
        else:
            if warn_if_result == 'not-last':
                self._warn_if_result = warn_if_result
            else:
                self._warn_if_result = True if warn_if_result else False
            self._warn_max_rows = 10
        
        # Prepare cursor and execute sql (if any)
        self._notices_handler = None
        self._cursor = self._prepare_cursor_and_execute()
        self.db._unclosed_results.add(self)
        
        # Prepare result variables
        self._columns: list[Column]|None = None
        self._headers: list[str]|None = None
        self._row_iterator = None
        self._row_iteration_stopped = False
        self._iterated_rows: list[tuple] = []

        # Control usage as a context manager        
        self._is_entered = False

    def __enter__(self):
        self._is_entered = True
        return self
    
    def __exit__(self, exc_type = None, exc = None, exc_tb = None):
        self._finalize_cursor(on_exception = True if exc_type else False)

    @property
    def cursor(self) -> Cursor:
        if not self._is_entered:
            raise ValueError(f"{self.__class__.__name__} must be used as a context manager (enclosed in a `with` block)")
        return self._cursor
    
    def _prepare_cursor_and_execute(self) -> Cursor:
        cursor: Cursor = self.db.connection.cursor()

        self._notices_handler = self.db._register_notices_handler(cursor, self.source)
        if self._notices_handler:
            self._notices_handler.__enter__()
    
        if self.sql is not None:
            sql, params = self.db.prepare_sql(self.sql, self.params, limit=self.limit, offset=self.offset)
            if params is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, params)
                
        return cursor
    
    def _finalize_cursor(self, on_exception: bool):
        #
        # The parameter `on_exception` indicate that there was an exception in the `with` block, example:
        #
        #               with db.execute_result("SELECT 1") as result:
        #                   raise ValueError("I'm raising!")
        #
        # We still need to try-catch here because there might be other exceptions in the next result sets.
        # Particularly for SQL server/PyODBC where each PRINT or RAISERROR statement may be reported in distinct results sets,
        # with exceptions being reported in later result sets.
        #
        try:
            if self._notices_handler:
                self._notices_handler.__exit__(None, None, None)

            rows, headers, there_are_more = [], [], False
            nextset_method = getattr(self.cursor, 'nextset', None)
            while True: # traverse all result sets
                if not on_exception: # Do not display warnings after exception (that would induce mistake in the exception analyzis)
                    self.db._log_cursor_notices(self.cursor, self.source)

                if self._warn_if_result:
                    if rows:
                        self._log_resultset_warn_info(rows, headers, there_are_more)
                    rows, headers, there_are_more = self._get_resultset_warn_info(self.cursor)
    
                if not nextset_method or not nextset_method():
                    break

            if rows and self._warn_if_result != 'not-last':
                self._log_resultset_warn_info(rows, headers, there_are_more)
        except:
            on_exception = True
            raise
        finally:
            self.cursor.close()
            self.db._unclosed_results.remove(self)

        if not on_exception: # Do not display warnings after exception (that would induce mistake in the exception analyzis)
            self.db._log_accumulated_notices(self.source)
            
    def _get_resultset_warn_info(self, cursor: Cursor):
        headers = []
        rows = []
        there_are_more = False

        if cursor.description:
            for i, row in enumerate(iter(cursor)):
                if self._warn_max_rows is None or i < self._warn_max_rows:
                    rows.append(row)
                else:
                    there_are_more = True
                    break

            if rows:
                headers = [c[0] for c in cursor.description]
        
        return rows, headers, there_are_more
        
    def _log_resultset_warn_info(self, rows: list, headers: list[str], there_are_more: bool):
        warn_text = "Unexpected result set:\n"
        warn_text += tabulate(rows, headers)
        if there_are_more:
            warn_text += "\n…"
        if self.source:
            warn_text = f"[{self.source}] {warn_text}"
        self.db._logger.warning(warn_text)

    @property
    def headers(self):
        if self._headers is None:
            if self._columns is not None:
                self._headers = [column.name for column in self._columns]
            else:
                self._headers = self.db.get_headers(self.cursor)
        return self._headers
    
    @property
    def columns(self):
        if self._columns is None:
            self._columns = self.db.get_columns(self.cursor)
        return self._columns

    def __iter__(self):       
        return ResultIterator(self)
        
    def __bool__(self):
        try:
            next(iter(self))
            return True
        except StopIteration:
            return False

    def _next_row(self) -> tuple:
        if self._row_iterator is None:
            self._row_iterator = iter(self.cursor)
        
        if self._row_iteration_stopped:
            raise StopIteration()
    
        try:
            values = next(self._row_iterator)
        except StopIteration:
            self._input_rows_iterator_stopped = True
            raise

        return values

    def _format_row(self, row: tuple) -> tuple:
        transformed_row = None

        if self.db._tz:
            for i, value in enumerate(row):
                transformed_value = self.db.get_python_value(value)
                if transformed_value != value:
                    if transformed_row is None:
                        transformed_row = [value for value in row] if isinstance(row, tuple) else row
                    transformed_row[i] = transformed_value

        return tuple(transformed_row) if transformed_row is not None else row
    
    @property
    def length(self) -> int:
        """
        Return the number of rows in the result set.
        
        To get the number of rows modified by the last SQL statement, use `rowcount` instead. 
        """
        return len(self)
    
    def __len__(self):
        """
        Return the number of rows in the result set.
        
        To get the number of rows modified by the last SQL statement, use `rowcount` instead. 
        """
        return sum(1 for _ in iter(self))

    @property
    def rowcount(self) -> int|None:
        """
        The number of rows modified by the last SQL statement. Has the value of -1 or None if the number of rows is unknown or unavailable.

        To get the number of rows in the result set, use `length` instead.
        """
        return self.cursor.rowcount
    
    @property
    def lastrowid(self):
        """
        The rowid of the last inserted row. None if no inserted rowid.
        """
        return self.db.get_lastrowid(self.cursor)
        
    # ---------- Dicts ----------

    def iter_dicts(self) -> Generator[dict[str,Any],Any,None]:
        for row in iter(self):
            yield {column: row[i] for i, column in enumerate(self.headers)}
    
    def get_dicts(self):
        return [data for data in self.iter_dicts()]

    def get_dict(self):
        iterator = self.iter_dicts()
        return next(iterator, None)
    
    def single_dict(self):
        iterator = self.iter_dicts()
        try:
            result = next(iterator)
        except StopIteration:
            raise NotFound()
        
        try:
            next(iterator)
            raise SeveralFound()
        except StopIteration:
            return result
            
    # ---------- Tuples ----------
        
    def iter_rows(self) -> Generator[tuple,Any,None]:
        for row in iter(self):
            yield row
    
    def get_rows(self):
        return [row for row in self.iter_rows()]

    def get_row(self):
        iterator = iter(self)
        return next(iterator, None)

    def single_row(self):
        iterator = iter(self)
        try:
            result = next(iterator)
        except StopIteration:
            raise NotFound()
        
        try:
            next(iterator)
            raise SeveralFound()
        except StopIteration:
            return result
            
    # ---------- Rows ----------
        
    def iter_scalars(self) -> Generator[tuple,Any,None]:
        for row in iter(self):
            if len(row) > 1:
                raise ValueError(f"Result rows have {len(row)} columns")
            if len(row) == 0:
                raise ValueError(f"Result rows have no column")
            value = row[0]
            yield value
    
    def get_scalars(self):
        return [value for value in self.iter_scalars()]

    def get_scalar(self):
        iterator = self.iter_scalars()
        return next(iterator, None)

    def single_scalar(self):
        iterator = self.iter_scalars()

        try:
            result = next(iterator)
        except StopIteration:
            raise NotFound()
        
        try:
            next(iterator)
            raise SeveralFound()
        except StopIteration:
            return result
    
    # ---------- Tabulate ----------
    
    def tabulate(self):
        tabular_data = self.get_rows()
        headers = self.headers
        return tabulate(tabular_data, headers)
    
    def print_tabulate(self, *, file = sys.stdout, max_length: int|None = None):
        text = self.tabulate()
        more = False
        if max_length is not None and len(text) > max_length:
            text = text[0:max_length-1] + '…'
            more = True
        file.write(text)
        if more:
            file.write('…')
        file.write('\n')


class ResultIterator:
    def __init__(self, result: ResultManager):
        self.context = result
        self.next_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_index < len(self.context._iterated_rows):
            row = self.context._iterated_rows[self.next_index]
        else:
            row = self.context._next_row()
            row = self.context._format_row(row)
            self.context._iterated_rows.append(row)
        self.next_index += 1
        return row


@dataclass
class MergeResult:
    """
    Result of merge and load operations.

    If used as a context manager, when the destination table is a temporary table, the table is dropped when the context is exited.
    """
    _db: Db

    src: DbObj|str|os.PathLike|IO[str]
    """ Source table or CSV file. """

    dst_table: DbObj
    """ Destination table. """

    columns_mapping: dict[str,Column]
    """ Mapping of source columns (or headers of the CSV file) to columns of the destination table. """

    inserted_count: int = 0
    """ Number of rows inserted from the source to the destination. """

    updated_count: int|None = None
    """ Number of rows updated (with change or not) from the source to the destination. """

    changed_count: int|None = None
    """ Number of updated rows that have at least one modification. """

    error_count: int|None = None
    """ Number of rows of the source that could not be inserted or updated in the destination because of an error. """

    absent_count: int|None = None
    """ Number of rows of the destination table that are absent in the source. """

    @cached_property
    def src_table(self) -> DbObj:
        if not isinstance(self.src, DbObj):
            raise TypeError("Source is not a table")
        return self.src
    
    @cached_property
    def src_total(self):
        result = self.inserted_count
        if self.updated_count is not None:
            result += self.updated_count
        if self.error_count is not None:
            result += self.error_count
        return result
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type = None, exc = None, exc_tb = None):
        if self.dst_table.temp:
            self._db.drop_table(self.dst_table)


class UniqueKey:
    columns: Sequence[str]
    """ Unique column(s). """

    nulls: Literal['distinct','not-distinct']|None
    """ Indicate how are NULL values treated: as distinct entries (the default) or as not distinct (see https://www.postgresql.org/about/featurematrix/detail/392/). """

    def __init__(self, columns: str|Sequence[str], *, nulls: Literal['distinct','not-distinct']|None = None):
        if isinstance(columns, str):
            columns = (columns,)
        self.columns = columns
        self.nulls = nulls

    def __repr__(self) -> str:
        return f"UniqueKey({', '.join(self.columns)})"


@dataclass
class ForeignKey:
    related_table: DbObj
    """ Related table of the forein key. """

    columns: Mapping[str, str|ForeignKey]
    """ Association of the source columns (e.g. 'basename_id1' and 'basename_id2') to the matching primary key in the related table. """

    def __init__(self, related_table: str|tuple|type|DbObj, columns: Mapping[str, str|ForeignKey]|Sequence[str]|str, *, basename: str|None = None, db: Db|type[Db]|None = None):
        if not isinstance(related_table, DbObj):
            if db is None:
                raise ValueError(f"Parameter 'db' must be provided when table ('{related_table}') is not a DbObj instance")
            related_table = db.parse_obj(related_table)
        
        self.related_table = related_table

        if isinstance(columns, str):
            columns = {columns: columns}
        elif isinstance(columns, Sequence):
            columns = {column: column for column in columns}

        if basename is None:
            self._basename = self._build_basename_from_column_names(columns.keys())
            self.columns = columns
        else:
            self._basename = basename
            self.columns = {f'{basename}_{column}': related_column for column, related_column in columns.items()}

    @property
    def basename(self) -> str|None:
        """ Base name of the foreign Key. This is normally the name of the field(s) without the `_id` or `_pk` suffix. """
        return self._basename
    
    @cached_property
    def suffixes(self) -> dict[str, str|ForeignKey]:
        return {self._split_column_name_basename(column)[1]: related_column for column, related_column in self.columns.items()}
    
    def _split_column_name_basename(self, column: str) -> tuple[str, str]:
        if not self.basename:
            return '', column
        if not column.startswith(f'{self.basename}_'):
            raise ValueError(f"Basename '{self.basename}' not found in column '{column}'")
        keyname = column[len(f'{self.basename}_'):]
        if not keyname:
            raise ValueError(f"Column '{column}' does not have a keyname after basename '{self.basename}'")
        return self.basename, keyname
    
    @classmethod
    def _build_basename_from_column_names(cls, columns: Iterable[str]) -> str|None:
        combined_possible_basenames: list[str]|None = None

        for column in columns:
            parts = column.split('_')
            if len(parts) <= 1:
                return None # Has no id or pk part
            column_possible_basenames = ['_'.join(parts[:i+1]) for i in range(len(parts)-1)]
            if combined_possible_basenames is None:
                combined_possible_basenames = column_possible_basenames
            else:
                for possible_basename in list(combined_possible_basenames):
                    if not possible_basename in column_possible_basenames:
                        combined_possible_basenames.remove(possible_basename)
                        if not combined_possible_basenames:
                            return None # No common basename found in columns
                        
        if combined_possible_basenames is None:
            raise ValueError(f"Argument 'columns' cannot be empty")
        
        if len(combined_possible_basenames) > 1:
            combined_possible_basenames.sort(key=lambda n: -len(n))
        return combined_possible_basenames[0]

#endregion


#region Utils

def get_db(input) -> Db:
    if isinstance(input, Db):
        return input
        
    scheme = None
    args = []
    kwargs = {}

    try:
        from django.db.backends.base.base import BaseDatabaseWrapper
        from django.utils.connection import ConnectionProxy
        if isinstance(input, ConnectionProxy):
            from django.db import connections
            input = connections[input._alias]
        if isinstance(input, BaseDatabaseWrapper):
            scheme = input.vendor.lower()
            args.append(input)
    except ModuleNotFoundError:
        pass
    
    if isinstance(input, str):
        if '://' in input:
            input = urlparse(input)

    if isinstance(input, (str,os.PathLike)):
        _, ext = os.path.splitext(input)
        ext = ext.lower()
        if ext in {'.sqlite3', '.sqlite', '.db'}:
            scheme = 'sqlite'
            kwargs['name'] = input
        else:
            raise ValueError(f"Invalid file extension for sqlite")

    elif isinstance(input, ParseResult):
        scheme = input.scheme.lower()
        m = re.match(r'^/([^/]+)', input.path)
        if not m:
            raise ValueError(f"Invalid URL: missing database name")
        kwargs['name'] = m[1]
        kwargs['user'] = input.username
        kwargs['password'] = input.password
        kwargs['host'] = input.hostname
        kwargs['port'] = input.port
    
    elif isinstance(input, Mapping):
        for key, value in input.items():
            if not isinstance(key, str):
                raise ValueError(f"Invalid key type in input: {key}")
            key = key.lower()
            if key == 'engine': # See https://docs.djangoproject.com/en/5.2/ref/settings/#databases
                scheme = value.lower()
            elif key in {'name', 'user', 'password', 'host', 'port'}: # See https://docs.djangoproject.com/en/5.2/ref/settings/#databases
                kwargs[key] = value
            elif key in {'table', 'sql', 'params'}:
                kwargs[key] = value
   
    if not scheme:
        raise ValueError(f"No database scheme found for input: {input}")
    
    pos = scheme.rfind('.')
    if pos:
        scheme = scheme[pos+1:]
        
    if scheme in {'postgresql', 'pg', 'postgres'}:
        from zut.db.pg import PgDb
        return PgDb(*args, **kwargs)
    elif scheme in {'mysql'}:
        from zut.db.mysql import MysqlDb
        return MysqlDb(*args, **kwargs)
    elif scheme in {'mariadb', 'maria'}:
        from zut.db.mariadb import MariaDb
        return MariaDb(*args, **kwargs)
    elif scheme in {'sqlite', 'sqlite3', 'sqlite3'}:
        from zut.db.sqlite import SqliteDb
        return SqliteDb(*args, **kwargs)
    elif scheme in {'sqlserver', 'mssql'}:
        from zut.db.sqlserver import SqlServerDb
        return SqlServerDb(*args, **kwargs)
    else:
        raise ValueError(f"Unsupported database scheme: {scheme}")


def _get_available_name(prefix: str, existing_names: Iterable[str], suffix = '') -> str:
    i = 1
    while True:
        name = prefix + (str(i) if i > 1 else '') + suffix
        if not name in existing_names:
            return name
        i += 1

#endregion
