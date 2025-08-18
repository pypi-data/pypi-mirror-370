"""
Implementation of `zut.db` for the PostgreSQL database backend.
"""
from __future__ import annotations

import logging
import os
import re
from contextlib import contextmanager, nullcontext
from datetime import date, datetime, time
from decimal import Decimal
from random import randint
from typing import IO, Any, Iterable
from uuid import UUID

from psycopg import Connection, connect
from psycopg.errors import Diagnostic

from zut import Column, DelayedStr, get_logger, skip_utf8_bom
from zut.csv import examine_csv_file
from zut.db import Db, DbObj, UniqueKey
from zut.urls import build_url

_logger = get_logger(__name__)


class PgDb(Db[Connection]):
    """
    Database adapter for PostgreSQL (using `psycopg` (v3) driver).
    """

    #region Connections and transactions

    scheme = 'postgresql'
    default_port = 5432

    def create_connection(self, autocommit: bool | None = None):
        kwargs = {}
        if self.name is not None:
            kwargs['dbname'] = self.name
        if self.host is not None:
            kwargs['host'] = self.host
        if self.port is not None:
            kwargs['port'] = self.port
        if self.user is not None:
            kwargs['user'] = self.user

        password = DelayedStr.ensure_value(self.password)
        if password is not None:
            kwargs['password'] = password

        kwargs['autocommit'] = autocommit if autocommit is not None else (False if self.no_autocommit else True)

        return connect(**kwargs)
    
    def build_connection_url(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT session_user, inet_server_addr(), inet_server_port(), current_database()")
            user, host, port, dbname = next(iter(cursor))
        return build_url(scheme=self.scheme, username=user, hostname=host, port=port, path=dbname)
    
    #endregion


    #region Cursors
    
    @contextmanager
    def _register_notices_handler(self, cursor, source: str|None):
        handler = lambda diag: self._notice_handler(diag, source)
        try:
            cursor.connection.add_notice_handler(handler) # type: ignore
            yield
        finally:
            cursor.connection.remove_notice_handler(handler) # type: ignore


    def _notice_handler(self, diag: Diagnostic, source: str|None = None):
        """
        Handler required by psycopg 3 `connection.add_notice_handler()`.
        """
        # determine level
        level, message = parse_pg_message(diag.severity_nonlocalized, diag.message_primary)
        
        # determine source by parsing context
        if diag.context:
            m = re.match(r"^[\s\w/]+ (\w+)\(", diag.context, re.IGNORECASE)
            if m:
                # English example: "PL/pgSQL function test_callproc(text,integer,smallint) line 3 at RAISE"
                source = m[1] # we replace default messages source

        # write log
        if source:
            message = f"[{source}] {message}"
        self._logger.log(level, message)


    def get_lastrowid(self, cursor) -> int:
        cursor.execute("SELECT lastval()")
        return next(iter(cursor))[0]

    #endregion


    #region Queries and types

    list_sql_type = '%(type)s[]'
    dict_sql_type = 'jsonb'
    decimal_sql_type = 'numeric'

    _accept_aware_datetimes = True
    _identity_sql = 'GENERATED ALWAYS AS IDENTITY'

    _pos_placeholder = '%s'
    _name_placeholder = '%%(%s)s'

    sql_type_catalog_by_id = {
        16: ('bool', bool),
        17: ('bytea', bytes),
        18: ('char', str),
        19: ('name', str),
        20: ('int8', int),
        21: ('int2', int),
        23: ('int4', int),
        25: ('text', str),
        26: ('oid', int),
        114: ('json', None),
        650: ('cidr', None),
        700: ('float4', float),
        701: ('float8', float),
        869: ('inet', None),
        1042: ('bpchar', str),
        1043: ('varchar', str),
        1082: ('date', date),
        1083: ('time', time),
        1114: ('timestamp', datetime),
        1184: ('timestamptz', datetime),
        1186: ('interval', None),
        1266: ('timetz', time),
        1700: ('numeric', Decimal),
        2249: ('record', None),
        2950: ('uuid', UUID),
        3802: ('jsonb', None),
        3904: ('int4range', None),
        3906: ('numrange', None),
        3908: ('tsrange', None),
        3910: ('tstzrange', None),
        3912: ('daterange', None),
        3926: ('int8range', None),
        4451: ('int4multirange', None),
        4532: ('nummultirange', None),
        4533: ('tsmultirange', None),
        4534: ('tstzmultirange', None),
        4535: ('datemultirange', None),
        4536: ('int8multirange', None),
    }

    sql_type_catalog_by_name = {description[0]: description[1] for description in sql_type_catalog_by_id.values()}

    #endregion


    #region Columns

    def _get_table_columns(self, table) -> list[Column]:
        object_fullname = self.escape_literal(table.full_escaped)
        
        sql = f"""
        WITH primary_key AS (
            SELECT i.indkey
            FROM pg_index i
            WHERE i.indisprimary
            AND i.indrelid = {object_fullname}::regclass
        )
        SELECT
            attname AS name
            ,format_type(atttypid, atttypmod) AS "type"
            ,CASE
                WHEN atttypmod = -1 THEN null
                WHEN atttypid IN (1042, 1043) THEN atttypmod - 4 -- char, varchar
                WHEN atttypid IN (1560, 1562) THEN atttypmod -- bit, varbit
                WHEN atttypid IN (1083, 1114, 1184, 1266) THEN atttypmod -- time, timestamp, timestamptz, timetz
                WHEN atttypid = 1700 THEN -- numeric (decimal)
                    CASE
                        WHEN atttypmod = -1 THEN null
                        ELSE ((atttypmod - 4) >> 16) & 65535
                    END
            END AS "precision"
            ,CASE
                WHEN atttypmod = -1 THEN null
                WHEN atttypid = 1700 THEN -- numeric (decimal)
                    CASE 
                        WHEN atttypmod = -1 THEN null       
                        ELSE (atttypmod - 4) & 65535  
                    END
            END AS "scale"
            ,attnotnull AS not_null
            ,COALESCE(a.attnum = ANY((SELECT indkey FROM primary_key)::smallint[]), false) AS "primary_key"
            ,a.attidentity != '' AS "identity"
            ,pg_get_expr(d.adbin, d.adrelid) AS "default"
        FROM pg_attribute a
        LEFT OUTER JOIN pg_attrdef d ON (d.adrelid, d.adnum) = (a.attrelid, a.attnum)
        WHERE a.attnum > 0 AND NOT a.attisdropped AND a.attrelid = {object_fullname}::regclass
        ORDER BY attnum
        """

        columns = []
        for row in self.iter_dicts(sql):
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

    @classmethod
    def _get_cursor_column(cls, name: str, type_info: type|int|str|None, display_size: int|None, internal_size: int|None, precision: int|None, scale: int|None, nullable: bool|int|None) -> Column:
        if display_size is not None:
            precision = display_size
        return super()._get_cursor_column(name, type_info, display_size, internal_size, precision, scale, nullable)
    
    #endregion


    #region Constraints

    def _get_table_unique_keys(self, table: DbObj) -> list[UniqueKey]:
        object_fullname = self.escape_literal(table.full_escaped)

        sql = f"""
        SELECT
            i.indexrelid AS index_id
            ,a.attname AS "column_name"
            ,k.i AS column_order_in_index
            ,k.attnum AS column_order_in_table
        FROM pg_index i
        CROSS JOIN LATERAL unnest(i.indkey) WITH ORDINALITY AS k(attnum, i)
        INNER JOIN pg_attribute AS a ON a.attrelid = i.indrelid AND a.attnum = k.attnum
        WHERE i.indrelid = 'public.test_unique_keys'::regclass AND i.indisunique
        ORDER BY index_id, column_order_in_index
        """

        unique_keys: dict[str,list] = {}
        positions: dict[str,int] = {}

        for data in self.get_dicts(sql):
            if data['index_id'] in unique_keys:
                columns = unique_keys[data['index_id']]
            else:
                columns = []
                unique_keys[data['index_id']] = columns                
            columns.append(data['column_name'])
            positions[data['column_name']] = data['column_order_in_table']

        return [UniqueKey(tuple(columns)) for columns in sorted(unique_keys.values(), key=lambda u: tuple(positions[c] for c in u))]


    def _get_table_foreign_key_descriptions(self, table: DbObj) -> list[dict[str,Any]]:
        if table.temp:
            schema_spec = "LIKE 'pg_temp_%%'"
            params = [table.name]
        else:
            schema_spec = f"= {self._pos_placeholder}"
            params = [table.schema or self._default_schema, table.name]

        sql = f"""
        SELECT
            fk.CONSTRAINT_NAME AS constraint_name
            ,cu.COLUMN_NAME AS column_name
            ,r_uk.TABLE_SCHEMA AS related_schema
            ,r_uk.TABLE_NAME AS related_table
            ,r_cu.COLUMN_NAME AS related_column_name
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS fk
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE cu ON cu.CONSTRAINT_NAME = fk.CONSTRAINT_NAME AND cu.CONSTRAINT_SCHEMA = fk.CONSTRAINT_SCHEMA AND cu.CONSTRAINT_CATALOG = fk.CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.COLUMNS c ON c.COLUMN_NAME = cu.COLUMN_NAME AND c.TABLE_NAME = fk.TABLE_NAME AND c.TABLE_SCHEMA = fk.TABLE_SCHEMA AND c.TABLE_CATALOG = fk.CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc ON rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME AND cu.CONSTRAINT_SCHEMA = fk.CONSTRAINT_SCHEMA AND cu.CONSTRAINT_CATALOG = fk.CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS r_uk ON r_uk.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'UNIQUE') AND r_uk.CONSTRAINT_NAME = rc.UNIQUE_CONSTRAINT_NAME AND r_uk.CONSTRAINT_SCHEMA = rc.UNIQUE_CONSTRAINT_SCHEMA AND r_uk.CONSTRAINT_CATALOG = rc.UNIQUE_CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE r_cu ON r_cu.TABLE_NAME = r_uk.TABLE_NAME AND r_cu.CONSTRAINT_NAME = r_uk.CONSTRAINT_NAME AND r_cu.CONSTRAINT_SCHEMA = r_uk.CONSTRAINT_SCHEMA AND r_cu.CONSTRAINT_CATALOG = r_uk.CONSTRAINT_CATALOG AND r_cu.ORDINAL_POSITION = cu.POSITION_IN_UNIQUE_CONSTRAINT
        WHERE fk.CONSTRAINT_TYPE = 'FOREIGN KEY' AND fk.TABLE_SCHEMA {schema_spec} AND fk.TABLE_NAME = {self._pos_placeholder}
        ORDER BY c.ORDINAL_POSITION
        """
        return self.get_dicts(sql, params)

    #endregion


    #region Tables

    _can_cascade_truncate = True

    def table_exists(self, table: str|tuple|type|DbObj) -> bool:
        table = self.parse_obj(table)

        if table.temp:
            result = self.get_row("SELECT 1 FROM pg_tables WHERE schemaname LIKE 'pg_temp_%%' AND tablename = %s", [table.name])
        else:
            result = self.get_row("SELECT 1 FROM pg_tables WHERE schemaname = %s AND tablename = %s", [table.schema or self._default_schema, table.name])
        return True if result else False

    #endregion


    #region Schemas

    _default_schema = 'public'
    _temp_schema = 'pg_temp'

    def schema_exists(self, name: str) -> bool:
        return True if self.get_row("SELECT 1 FROM pg_namespace WHERE nspname = %s", [name]) else False

    #endregion


    #region Databases

    def get_database_name(self) -> str:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            return next(iter(cursor))[0]
        
    def database_exists(self, name: str) -> bool:
        sql = "SELECT EXISTS (SELECT FROM pg_database WHERE datname = %s)"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, [name])
            return next(iter(cursor))[0]

    def create_database(self, name: str, *, if_not_exists = False, loglevel = logging.DEBUG) -> None:
        if if_not_exists:
            if self.database_exists(name):
                return
        super().create_database(name, loglevel=loglevel)

    #endregion


    #region Load and merge
    
    copy_csv_chunk_size = 65536
    
    _merge_statement = True
        
    def copy_csv(self, file: str|os.PathLike|IO[str], table: str|tuple|type|DbObj, columns: Iterable[str|Column]|None = None, *,
            delimiter: str|None = None,
            newline: str|None = None, # (`newline` not necessary for PostgreSQL)
            encoding = 'utf-8') -> int:
        
        table = self.parse_obj(table)

        if columns is None or delimiter is None:
            examined = examine_csv_file(file, encoding=encoding)
            if columns is None:
                columns = examined.headers
            if delimiter is None:
                delimiter = examined.delimiter
                                
        escaped_double_quote = self.escape_literal('"')
        sql = f"COPY {table.escaped} ("
        for i, column in enumerate(columns):
            sql += (", " if i > 0 else "") + self.escape_identifier(column)
        sql += ")"            
        sql += f" FROM STDIN (FORMAT csv, ENCODING {self.escape_literal('utf-8' if encoding == 'utf-8-sig' else encoding)}, DELIMITER {self.escape_literal(delimiter)}, QUOTE {escaped_double_quote}, ESCAPE {escaped_double_quote}, HEADER match)"
        
        self._logger.debug("Load %s to %s …", file, table)
        with open(file, "rb") if isinstance(file, (str,os.PathLike)) else nullcontext(file) as fp:
            skip_utf8_bom(fp)

            with self.connection.cursor() as cursor:
                with cursor.copy(sql) as copy: # type: ignore
                    while True:
                        data = fp.read(self.copy_csv_chunk_size)
                        if not data:
                            break
                        copy.write(data)
                rowcount = cursor.rowcount

        self._logger.debug("%d rows loaded to %s", rowcount, table)
        return rowcount

    #endregion


def parse_pg_message(severity: str|None, message: str|None) -> tuple[int, str]:
    if message:
        m = re.match(r'^\[?(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)[\]\:](?P<message>.+)$', message, re.DOTALL)
        if m:
            return getattr(logging, m['level']), m['message'].lstrip()
    else:
        message = '?'

    if severity is not None:
        if severity.startswith('DEBUG'): # not sent to client (by default)
            return logging.DEBUG, message
        elif severity == 'LOG': # not sent to client (by default), written on server log (LOG > ERROR for log_min_messages)
            return logging.DEBUG, message
        elif severity == 'NOTICE': # sent to client (by default) [=client_min_messages]
            return logging.DEBUG, message
        elif severity == 'INFO': # always sent to client
            return logging.INFO, message
        elif severity == 'WARNING': # sent to client (by default) [=log_min_messages]
            return logging.WARNING, message
        elif severity in ['ERROR', 'FATAL']: # sent to client
            return logging.ERROR, message
        elif severity in 'PANIC': # sent to client
            return logging.CRITICAL, message
    
    return logging.WARNING, message


def enforce_pg_seq_offset(connection: Connection|PgDb|None = None, app_label: str|None = None, *, min_offset: int|None = None, max_offset: int|None = None):
    """
    Ensure the given model (or all models if none is given) have sequence starting with a minimal value.
    This leaves space for custom, programmatically defined values.

    Unless `min_offset` and `max_offset` are specified, the minimal value is randomly chosen between 65537 (after
    max uint16 value) and 262144 (max uint18 value).

    Compatible with postgresql only.
    """
    _connection: Connection
    if connection is None:
        from django.db import connection as _connection  # type: ignore
    elif isinstance(connection, Db):
        _connection = connection.connection
    else:
        _connection = connection

    if min_offset is None and max_offset is None:
        min_offset = 65537
        max_offset = 262144
    elif max_offset is None:
        max_offset = min_offset
    elif min_offset is None:
        min_offset = min(65537, max_offset)

    sql = f"""
SELECT
    s.schema_name
    ,s.table_name
    ,s.column_names
    ,s.sequence_name
    ,q.seqstart AS sequence_start
FROM (
    -- List all PKs with their associated sequence name (or NULL if this is not a serial or identity column)
    SELECT
        n.nspname AS schema_name
        ,c.relnamespace AS schema_oid
        ,c.relname AS table_name
        ,array_agg(a.attname) AS column_names
        ,substring(pg_get_serial_sequence(n.nspname || '.' || c.relname, a.attname), length(n.nspname || '.') + 1) AS sequence_name
    FROM pg_index i
    INNER JOIN pg_class c ON c.oid = i.indrelid
    INNER JOIN pg_namespace n ON n.oid = c.relnamespace
    INNER JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = any(i.indkey)
    WHERE i.indisprimary
    GROUP BY
        n.nspname
        ,c.relnamespace
        ,c.relname
        ,substring(pg_get_serial_sequence(n.nspname || '.' || c.relname, a.attname), length(n.nspname || '.') + 1)
) s
LEFT OUTER JOIN pg_class c ON c.relnamespace = s.schema_oid AND c.relname = s.sequence_name
LEFT OUTER JOIN pg_sequence q ON q.seqrelid = c.oid
WHERE s.schema_name = 'public' AND s.table_name {"LIKE %s" if app_label else "IS NOT NULL"} AND q.seqstart = 1
ORDER BY schema_name, table_name, column_names
"""
    params = [f'{app_label}_%'] if app_label else None

    seqs = []
    with _connection.cursor() as cursor:
        cursor.execute(sql, params)
        for row in cursor:
            seqs.append({'schema': row[0], 'table': row[1], 'column': row[2][0], 'name': row[3]})

    with _connection.cursor() as cursor:
        for seq in seqs:
            sql = f"SELECT MAX({PgDb.escape_identifier(seq['column'])}) FROM {PgDb.escape_identifier(seq['schema'])}.{PgDb.escape_identifier(seq['table'])}"
            cursor.execute(sql) # type: ignore
            row = cursor.fetchone()
            max_id = row[0] or 0 if row else 0
            
            start_value = max(max_id + 1, randint(min_offset, max_offset)) # type: ignore
            _logger.debug("Set start value of %s to %s", seq['name'], start_value)
            sql = f"ALTER SEQUENCE {PgDb.escape_identifier(seq['name'])} START WITH {start_value} RESTART WITH {start_value}"
            cursor.execute(sql) # type: ignore
