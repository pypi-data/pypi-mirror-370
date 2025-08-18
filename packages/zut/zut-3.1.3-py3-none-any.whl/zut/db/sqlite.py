"""
Implementation of `zut.db` for the SQLite database backend.
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from sqlite3 import Connection, connect
from typing import TYPE_CHECKING, Any

from zut import Column, NotSupportedBy
from zut.db import Db, DbObj, UniqueKey
from zut.urls import build_url

if TYPE_CHECKING:
    from typing import Literal

class SqliteDb(Db[Connection]):
    """
    Database adapter for SQLite 3 (using the driver included in Python 3).
    """

    #region Connections and transactions

    scheme = 'sqlite'
    create_if_not_exists = False

    def __init__(self,
                 connection_or_path: Connection|str|os.PathLike|None = None, *,
                 no_autocommit: bool|str|None = None,
                 tz: Literal['local','utc']|None = None,
                 migrations_dir: str|os.PathLike|None = None,
                 create_if_not_exists: bool|None = None,
                 **kwargs):
        
        if create_if_not_exists is None:
            create_if_not_exists = self.__class__.create_if_not_exists
        
        if isinstance(connection_or_path, (str,os.PathLike)):
            if kwargs.get('name'):
                raise ValueError(f"Sqlite path cannot be provided both as first positional argument ('{connection_or_path}') and as keyword argument 'name' ('{kwargs.get('name')}')")
            connection = None
            path = connection_or_path if isinstance(connection_or_path, str) else str(connection_or_path)
            kwargs['name'] = path
        else:
            connection = connection_or_path

        if not create_if_not_exists:
            path = kwargs.get('name')
            if path:
                if not os.path.exists(path):
                    raise ValueError(f"Sqlite database not found at {path}") # Mandatory check (otherwise it would be automatically created by Python's sqlite3 module)
        
        super().__init__(connection,
                         no_autocommit=no_autocommit,
                         tz=tz,
                         migrations_dir=migrations_dir,
                         **kwargs)
        

    def create_connection(self, autocommit: bool|None = None):
        if not self.name:
            raise ValueError(f"Missing name (the path to the database) argument ({self.__class__.__name__})")
        
        dir_path = os.path.dirname(self.name)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

        if autocommit is None:
            autocommit = (False if self.no_autocommit else True)

        if sys.version_info < (3, 12): # Sqlite connect()'s autocommit parameter introduced in Python 3.12
            return connect(self.name, isolation_level=None if autocommit else 'DEFERRED')
        else:
            return connect(self.name, autocommit=autocommit)
    
    @property
    def autocommit(self):
        if sys.version_info < (3, 12): # Sqlite connect()'s autocommit parameter introduced in Python 3.12
            return False if self.no_autocommit else True
        else:
            return super().autocommit

    @property
    def in_transaction(self) -> bool:
        return self.connection.in_transaction # type: ignore

    def check_port(self) -> bool:
        if not self.name:
            return False
        return os.path.exists(self.name)
    
    def build_connection_url(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT file, name FROM pragma_database_list WHERE name = 'main'")
        file, _ = next(iter(cursor))
        return build_url(scheme=self.scheme, path=file.replace('\\', '/'))

    #endregion


    #region Queries and types

    list_sql_type = 'text'
    dict_sql_type = 'text'
    bool_sql_type = 'integer'
    int_sql_type = 'integer'
    uuid_sql_type = 'text'
    float_sql_type = 'real'
    decimal_sql_type = 'text'
    vardecimal_sql_type_pattern = None
    datetime_sql_type = 'real'
    date_sql_type = 'text'

    _split_multi_statement_scripts = True
    _start_transaction_sql = 'BEGIN TRANSACTION'

    _pos_placeholder = '?'
    _name_placeholder = ':%s'
    _identity_sql = 'AUTOINCREMENT'

    def get_sql_value(self, value: Any):
        value = super().get_sql_value(value)
        if isinstance(value, (IPv4Address,IPv6Address)):
            return value.compressed
        elif isinstance(value, Decimal):
            from zut.convert import get_number_str
            return float(value) if self.decimal_sql_type in {'real', 'float', 'double', 'decimal'} else get_number_str(value)
        elif isinstance(value, datetime):
            #NOTE: The datetime value has been converted to a naive value in the expected timezone (in `super().get_sql_value(value)`)
            if self.datetime_sql_type in {'real', 'float', 'double', 'decimal'}:
                return value.timestamp()
            elif 'int' in self.datetime_sql_type:
                return int(value.timestamp())
            elif self.datetime_sql_type.endswith('(19)'):
                return value.replace(microsecond=0).isoformat().replace('T', ' ')
            else:
                text = value.isoformat().replace('T', ' ')
                if not '.' in text:
                    return text + '.000'
                else:
                    return text[:-3]
        else:
            return value

    def _get_local_now_sql(self):
        if self.datetime_sql_type in {'real', 'float', 'double', 'decimal'}:
            return "unixepoch(datetime('subsec', 'localtime'), 'subsec')"
        elif 'int' in self.datetime_sql_type:
            return "unixepoch(datetime('subsec', 'localtime'))"
        elif self.datetime_sql_type.endswith('(19)'):
            return "datetime('now', 'localtime')"
        else:
            return "datetime('subsec', 'localtime')"
    
    def _get_utc_now_sql(self):
        if self.datetime_sql_type in {'real', 'float', 'double', 'decimal'}:
            return "unixepoch('subsec')"
        elif 'int' in self.datetime_sql_type:
            return "unixepoch()"
        elif self.datetime_sql_type.endswith('(19)'):
            return "datetime()"
        else:
            return "datetime('subsec')"

    #endregion


    #region Columns

    def _get_table_columns(self, table) -> list[Column]:
        sql = f"""
        SELECT
            c.cid AS "ordinal"
            ,c.name
            ,lower(c."type") AS "type"
            ,null AS "precision"
            ,null AS "scale"
            ,CASE WHEN c."notnull" = 1 THEN 1 ELSE 0 END AS not_null
            ,c.pk AS primary_key	
            ,CASE WHEN lower(c."type") = 'integer' AND c.pk = 1 AND lower(t."sql") LIKE '%autoincrement%' THEN 1 ELSE 0 END AS "identity"
            ,c.dflt_value AS "default"
        FROM {'temp' if table.schema == 'temp' else 'main'}.pragma_table_info(?) c
        LEFT OUTER JOIN sqlite{'_temp' if table.schema == 'temp' else ''}_master t ON t.name = ?
        ORDER BY c.cid
        """

        columns = []
        for row in self.iter_dicts(sql, [table.name, table.name]):
            column = Column(
                name = row['name'],
                type = row['type'],
                precision = row['precision'],
                scale = row['scale'],
                not_null = row['not_null'] == 1,
                primary_key = row['primary_key'] == 1,
                identity = row['identity'] == 1,
                default = row['default'])
            
            self._parse_default_from_db(column)
            columns.append(column)

        return columns
    
    #endregion


    #region Constraints

    def _get_table_unique_keys(self, table: DbObj) -> list[UniqueKey]:
        unique_keys: list[list[str]] = []
        positions: dict[str,int] = {}

        for key_name in self.get_scalars(f'SELECT name FROM {"temp" if table.schema == "temp" else "main"}.pragma_index_list(?) WHERE "unique" = 1', [table.name]):
            unique_key = []
            
            for name, cid in self.get_rows(f'SELECT name, cid FROM {"temp" if table.schema == "temp" else "main"}.pragma_index_info(?) ORDER BY seqno', [key_name]):
                unique_key.append(name)
                positions[name] = cid
            
            unique_keys.append(unique_key)

        return [UniqueKey(tuple(columns)) for columns in sorted(unique_keys, key=lambda u: tuple(positions[c] for c in u))]

    def _get_table_foreign_key_descriptions(self, table: DbObj) -> list[dict[str,Any]]:
        if table.temp:
            schema = "'temp'"
            pragma = "temp.pragma"
        else:
            schema = "null"
            pragma = "main.pragma"

        sql = f"""
        SELECT
            fk.id AS constraint_name
            ,"from" AS column_name
            ,{schema} AS related_schema
            ,"table" AS related_table
            ,"to" AS related_column_name
        FROM {pragma}_foreign_key_list({self._pos_placeholder}) fk
        INNER JOIN {pragma}_table_info({self._pos_placeholder}) c ON c."name" = fk."from"
        ORDER BY c.cid
        """
        return self.get_dicts(sql, [table.name, table.name])

    #endregion


    #region Tables

    def table_exists(self, table: str|tuple|type|DbObj) -> bool:
        table = self.parse_obj(table)
        
        if table.schema == 'temp':
            sql = "SELECT 1 FROM sqlite_temp_master WHERE type = 'table' AND name = ?"
        elif not table.schema or table.schema == 'main':
            sql = "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?"
        else:
            raise NotSupportedBy(self.__class__, f'schema "{table.schema}"')
        
        return True if self.get_row(sql, [table.name]) else False

    #endregion


    #region Schemas

    _default_schema = None
    _temp_schema = 'temp'

    #endregion


    #region Database

    def get_database_name(self) -> str|None:
        if self.name is None:
            return None
        stem, _ = os.path.splitext(os.path.basename(self.name))
        return stem
    
    def use_database(self, name: str) -> None:
        raise NotSupportedBy(self.__class__)

    def database_exists(self, name: str) -> bool:
        return name == self.get_database_name()
    
    def create_database(self, name: str, *, if_not_exists = False, loglevel = logging.DEBUG) -> None:
        raise NotSupportedBy(self.__class__)

    def drop_database(self, name: str, *, if_exists = False, loglevel = logging.DEBUG) -> None:
        raise NotSupportedBy(self.__class__)

    #endregion


    #region Load and merge

    #ROADMAP

    #endregion
