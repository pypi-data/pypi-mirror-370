"""
Implementation of `zut.db` for the Sql Server database backend.
"""
from __future__ import annotations

import logging
import re
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Iterable
from uuid import UUID

from pyodbc import Connection, connect, drivers

from zut import Column, DelayedStr
from zut.db import Cursor, Db, DbObj, UniqueKey
from zut.urls import build_url


class SqlServerDb(Db[Connection]): # type: ignore
    """
    Database adapter for Microsoft SQL Server (using `pyodbc` driver).
    """

    #region Connections and transactions
    
    scheme = 'sqlserver'
    default_port = 1433

    def create_connection(self, autocommit: bool | None = None):
        def escape(s: str):
            if ';' in s or '{' in s or '}' in s or '=' in s:
                return "{" + s.replace('}', '}}') + "}"
            else:
                return s

        # Use "ODBC Driver XX for SQL Server" if available ("SQL Server" seems not to work with LocalDB, and takes several seconds to establish connection on my standard Windows machine with SQL Server Developer).
        driver = "SQL Server"
        for a_driver in sorted(drivers(), reverse=True):
            if re.match(r'^ODBC Driver \d+ for SQL Server$', a_driver):
                driver = a_driver
                break        
        connection_string = 'Driver={%s}' % escape(driver)
                
        server = self.host or '(local)'
        if self.port:
            server += f',{self.port}'
        connection_string += ';Server=%s' % escape(server)

        if self.name:
            connection_string += ';Database=%s' % escape(self.name)

        if self.user:
            connection_string += ';UID=%s' % escape(self.user)
            if self.password:
                password = DelayedStr.ensure_value(self.password)
                if password:
                    connection_string += ';PWD=%s' % escape(password)
        else:
            connection_string += ';Trusted_Connection=yes'
            
        connection_string += ';Encrypt=%s' % ('yes' if self.encrypt else 'no',)

        if autocommit is None:
            autocommit = (False if self.no_autocommit else True)
        return connect(connection_string, autocommit=autocommit)
    
    def build_connection_url(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT @@SERVERNAME, local_tcp_port, SUSER_NAME(), DB_NAME() FROM sys.dm_exec_connections WHERE session_id = @@spid")
            host, port, user, dbname = next(iter(cursor))
        return build_url(scheme=self.scheme, username=user, hostname=host, port=port, path=dbname)

    #endregion


    #region Cursors

    def _log_cursor_notices(self, cursor: Cursor, source: str|None):
        messages: Iterable[tuple[str,str]]|None = cursor.messages # type: ignore
        if not messages:
            return
                            
        for nature, message in messages:
            level, message = parse_sqlserver_message(nature, message)
            if source:
                message = f"[{source}] {message}"
            self._logger.log(level, message)

    def get_lastrowid(self, cursor):
        cursor.execute("SELECT @@IDENTITY")
        return next(iter(cursor))[0]
    
    #endregion


    #region Queries and types

    varstr_sql_type_pattern = 'varchar(%(max_length)d)'
    bool_sql_type = 'bit'
    uuid_sql_type = 'uniqueidentifier'
    decimal_sql_type = 'varchar(66)'
    datetime_sql_type = 'datetime'

    _only_positional_params = True
    _start_transaction_sql = 'BEGIN TRANSACTION'
    _split_multi_statement_scripts = True # NOTE: multi "SELECT" works without splitting, but multi "CREATE FUNCTION" does not

    _pos_placeholder = '?'
    _name_placeholder = ':%s'
    _identity_sql = 'IDENTITY'
    
    def _get_local_now_sql(self) -> str:
        return "CURRENT_TIMESTAMP"
    
    def _get_utc_now_sql(self) -> str:
        return "GETUTCDATE()"

    def _paginate_splited_select_sql(self, selectpart: str, orderpart: str, *, limit: int|None, offset: int|None) -> str:
        if orderpart:
            result = f"{selectpart} {orderpart} OFFSET {offset or 0} ROWS"
            if limit is not None:
                result += f" FETCH NEXT {limit} ROWS ONLY"
            return result
        elif limit is not None:
            if offset is not None:
                raise ValueError("an ORDER BY clause is required for OFFSET")
            return f"SELECT TOP {limit} * FROM ({selectpart}) s"
        else:
            return selectpart

    sql_type_catalog_by_name = {
        'bigint': int,
        'binary': bytes,
        'bit': bool,
        'char': str,
        'date': date,
        'datetime': datetime,
        'datetime2': datetime,
        'datetimeoffset': None,
        'decimal': Decimal,
        'float': float,
        'geography': None,
        'geometry': None,
        'hierarchyid': None,
        'image': None,
        'int': int,
        'money': Decimal,
        'nchar': str,
        'ntext': str,
        'numeric': Decimal,
        'nvarchar': str,
        'real': float,
        'smalldatetime': datetime,
        'smallint': int,
        'smallmoney': Decimal,
        'sql_variant': None,
        'sysname': str,
        'text': str,
        'time': time,
        'timestamp': None,
        'tinyint': int,
        'uniqueidentifier': UUID,
        'varbinary': bytes,
        'varchar': str,
        'xml': str,
    }

    #endregion


    #region Execute

    _procedure_caller = 'EXEC'
    _procedure_params_parenthesis = False
    _function_requires_schema = True

    #endregion


    #region Columns
    
    _can_add_several_columns = True

    @classmethod
    def _get_cursor_column(cls, name: str, type_info: type|int|str|None, display_size: int|None, internal_size: int|None, precision: int|None, scale: int|None, nullable: bool|int|None) -> Column:
        if type_info == Decimal:
            pass # keep precision and scale
        elif type_info == str:
            if precision is not None:
                if precision >= 1073741823:  # ntext: 1073741823, text: 2147483647
                    precision = None
                elif precision == 0: # varchar(max), nvarchar(max)
                    precision = None
            scale = None
        elif type_info == datetime or type_info == time:
            precision = scale
            scale = None
        elif type_info in {int, float}:
            precision = None
            scale = None
        else:
            if type_info == bytearray:
                type_info = None
            precision = None
            scale = None
        return super()._get_cursor_column(name, type_info, display_size, internal_size, precision, scale, nullable)

    def _get_table_columns(self, table) -> list[Column]:
        if table.name.startswith('#'):
            object_fullname = self.escape_literal(f'tempdb..{self.escape_identifier(table.name)}')
            sys_schema = 'tempdb.sys'
        else:
            object_fullname = self.escape_literal(table.full_escaped)
            sys_schema = 'sys'
        
        sql = f"""
        WITH primary_key AS (
            SELECT ic.column_id
            FROM {sys_schema}.indexes i
            INNER JOIN {sys_schema}.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
            WHERE i.is_primary_key = 1
            AND i.object_id = OBJECT_ID({object_fullname})
        )
        SELECT
            c.column_id AS [ordinal]
            ,c.name
            ,t.name AS "type"
            --ROADMAP ,CASE WHEN c.collation_name IS NOT NULL THEN concat(' COLLATE ', c.collation_name) ELSE '' END AS sql_type_suffix
            ,CASE
                WHEN t.name IN ('char', 'varchar', 'binary', 'varbinary') THEN c.[max_length]
                WHEN t.name IN ('nchar', 'nvarchar') THEN c.[max_length] / 2
                WHEN t.name = 'datetime2' THEN c.[scale]
                WHEN t.name IN ('numeric', 'decimal') THEN c.[precision]
            END AS [precision]
            ,CASE
                    WHEN t.name IN ('numeric', 'decimal') THEN c.[scale]
            END AS [scale]
            ,CASE WHEN c.is_nullable = 0 THEN 1 ELSE 0 END AS not_null
	        ,CASE WHEN c.column_id IN (SELECT column_id FROM primary_key) THEN 1 ELSE 0 END AS [primary_key]
            ,c.is_identity AS [identity]
            ,OBJECT_DEFINITION(c.default_object_id) AS [default]
        FROM {sys_schema}.columns c
        LEFT OUTER JOIN {sys_schema}.types t ON t.user_type_id = c.system_type_id
        WHERE c.object_id = OBJECT_ID({object_fullname})
        ORDER BY [ordinal]
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

    #endregion


    #region Constraints

    def _get_table_unique_keys(self, table: DbObj) -> list[UniqueKey]:
        if table.name.startswith('#'):
            object_fullname = self.escape_literal(f'tempdb..{self.escape_identifier(table.name)}')
            sys_schema = 'tempdb.sys'
        else:
            object_fullname = self.escape_literal(table.full_escaped)
            sys_schema = 'sys'
        
        sql = f"""
        SELECT
            i.index_id
            ,c.name AS column_name
            ,ic.key_ordinal AS column_order_in_index
            ,ic.column_id AS column_order_in_table
        FROM {sys_schema}.indexes i
        INNER JOIN {sys_schema}.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
        INNER JOIN {sys_schema}.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id  
        WHERE i.object_id = OBJECT_ID({object_fullname}) AND i.is_unique = 1
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
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE r_cu ON r_cu.TABLE_NAME = r_uk.TABLE_NAME AND r_cu.CONSTRAINT_NAME = r_uk.CONSTRAINT_NAME AND r_cu.CONSTRAINT_SCHEMA = r_uk.CONSTRAINT_SCHEMA AND r_cu.CONSTRAINT_CATALOG = r_uk.CONSTRAINT_CATALOG AND r_cu.ORDINAL_POSITION = cu.ORDINAL_POSITION
        WHERE fk.CONSTRAINT_TYPE = 'FOREIGN KEY' AND fk.TABLE_SCHEMA = {self._pos_placeholder} AND fk.TABLE_NAME = {self._pos_placeholder}
        ORDER BY c.ORDINAL_POSITION
        """
        return self.get_dicts(sql, [table.schema or self._default_schema, table.name])
    
    #endregion


    #region Tables

    _truncate_with_delete = True

    strict_types = True

    def table_exists(self, table: str|tuple|type|DbObj) -> bool:
        table = self.parse_obj(table)

        if table.temp:
            object_fullname = self.escape_literal(f'tempdb..{self.escape_identifier(table.name)}')
            result = self.get_row(f"SELECT 1 FROM tempdb.sys.tables WHERE object_id = OBJECT_ID({object_fullname})")
        else:
            result = self.get_row(f"SELECT 1 FROM information_schema.tables WHERE table_schema = ? AND table_name = ?", [table.schema or self._default_schema, table.name])
        
        return True if result else False
       
    #endregion


    #region Schemas

    _default_schema = 'dbo'
    _temp_schema = '#'

    def schema_exists(self, name: str) -> bool:
        return True if self.get_row("SELECT 1 FROM information_schema.schemata WHERE schema_name = ?", [name]) else False

    def create_schema(self, name: str, *, if_not_exists = False, loglevel = logging.DEBUG):
        if if_not_exists:
            if self.schema_exists(name):
                return
        super().create_schema(name, loglevel=loglevel)

    #endregion

    
    #region Databases

    def get_database_name(self) -> str:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT db_name()")
            return next(iter(cursor))[0]

    def database_exists(self, name: str) -> bool:
        sql = "SELECT 1 FROM master.sys.databases WHERE name = ?"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, [name])
            try:
                return next(iter(cursor))[0] == 1            
            except StopIteration:
                return False

    def create_database(self, name: str, *, if_not_exists = False, loglevel = logging.DEBUG) -> None:
        if if_not_exists:
            if self.database_exists(name):
                return
        super().create_database(name, loglevel=loglevel)

    #endregion


    #region Load and merge

    _merge_statement = True

    #ROADMAP

    #endregion


def parse_sqlserver_message(nature: str, message: str) -> tuple[int, str]:
    m = re.match(r"^\[Microsoft\]\[[\w\d ]+\]\[SQL Server\](.+)$", message)
    if m:
        message = m[1]

    if nature == '[01000] (0)':
        nature = 'PRINT'
    elif nature == '[01000] (50000)':
        nature = 'RAISERROR'
    elif nature == '[01003] (8153)': # Avertissement : la valeur NULL est éliminée par un agrégat ou par une autre opération SET
        return logging.INFO, message
    
    m = re.match(r'^\[?(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s?[\]\:](?P<message>.+)$', message, re.DOTALL|re.IGNORECASE)
    if m:
        return getattr(logging, m['level']), m['message'].lstrip()
    
    if nature == 'PRINT':
        return logging.INFO, message
    else:
        return logging.WARNING, message
