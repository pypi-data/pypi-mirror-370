"""
Implementation of `zut.db` for the MySQL database backend.
"""
from __future__ import annotations

import logging
import os
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from tempfile import NamedTemporaryFile
from typing import IO, Any, Iterable, Sequence

from MySQLdb import OperationalError, connect
from MySQLdb.connections import Connection

from zut import Column, DelayedStr
from zut.csv import examine_csv_file
from zut.db import Db, DbObj, MergeResult, UniqueKey
from zut.urls import build_url


class MysqlDb(Db[Connection]):
    #region Connections and transactions
    
    scheme = 'mysql'
    default_port = 3306

    def create_connection(self, autocommit: bool|None = None):
        kwargs = {}
        if self.name is not None:
            kwargs['database'] = self.name
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
            cursor.execute("SELECT user(), @@hostname, @@port, database()")
            user, host, port, dbname = next(iter(cursor))
            m = re.match(r'^(.+)@([^@]+)$', user)
            if m:
                user = m[1]
        return build_url(scheme=self.scheme, username=user, hostname=host, port=port, path=dbname)
    
    #endregion


    #region Cursors

    def _log_accumulated_notices(self, source):
        offset = getattr(self, '_cursor_notices_offset', 0)

        with self.connection.cursor() as cursor:
            cursor.execute(f"SHOW WARNINGS LIMIT {offset},18446744073709551615", [])
            offset += 1
            self._cursor_notices_offset = offset

            issue_count = 0
            for row in cursor:
                level, message = parse_mysql_message(row)

                if source:
                    message = f"[{source}] {message}"

                if level >= logging.WARNING:
                    issue_count += 1

                self._logger.log(level, message)

            if issue_count:
                raise ValueError(f"The SQL execution raised {issue_count} issue{'s' if issue_count > 1 else ''} (see logs above)")

    #endregion


    #region Queries and types

    str_sql_type= 'longtext'
    varstr_sql_type_pattern = 'varchar(%(max_length)d)'
    float_sql_type = 'double'
    decimal_sql_type = 'varchar(66)'
    datetime_sql_type = 'datetime(6)'

    _identifier_quotechar_begin = '`'
    _identifier_quotechar_end = '`'

    _pos_placeholder = '%s'
    _name_placeholder = '%%(%s)s'
    _identity_sql = 'AUTO_INCREMENT'
    
    def _get_local_now_sql(self) -> str:
        return "CURRENT_TIMESTAMP(6)"
    
    def _get_utc_now_sql(self) -> str:
        return "UTC_TIMESTAMP(6)"

    sql_type_catalog_by_id = { # (see: MySQLdb.constants.FIELD_TYPE)
        0: ('decimal', Decimal),
        1: ('tiny', int),
        2: ('short', int),
        3: ('long', int),
        4: ('float', float),
        5: ('double', float),
        6: ('null', None),
        7: ('timestamp', None),
        8: ('longlong', int), # bigint
        9: ('int24', None),
        10: ('date', date),
        11: ('time', time),
        12: ('datetime', datetime),
        13: ('year', None),
        14: ('newdate', None),
        15: ('varchar', str),
        16: ('bit', None),
        246: ('newdecimal', Decimal),
        247: ('interval', None),
        248: ('set', None),
        249: ('tiny_blob', None),
        250: ('medium_blob', None),
        251: ('long_blob', None),
        252: ('blob', None),
        253: ('var_string', str),
        254: ('string', str),
        255: ('geometry', None),
    }

    sql_type_catalog_by_name = {description[0]: description[1] for description in sql_type_catalog_by_id.values()}

    #endregion


    #region Columns

    def _get_table_columns(self, table) -> list[Column]:
        columns = []

        for row in self.iter_dicts(f"SHOW COLUMNS FROM {table.escaped}"):
            column = Column(
                name = row['Field'],
                type = row['Type'].lower(),
                not_null = row['Null'] == 'NO',
                primary_key = row['Key'] == 'PRI',
                identity = 'auto' in row['Extra'],
                default = row['Default'])
            
            self._parse_default_from_db(column)
            columns.append(column)

        return columns
    
    #endregion

    
    #region Constraints

    def _get_table_unique_keys(self, table: DbObj) -> list[UniqueKey]:
        unique_keys: dict[str,list] = {}

        for data in sorted(self.get_dicts(f"SHOW INDEX FROM {table.escaped} WHERE Non_unique = 0"), key=lambda d: (d['Key_name'], d['Seq_in_index'])):
            if data['Key_name'] in unique_keys:
                columns = unique_keys[data['Key_name']]
            else:
                columns = []
                unique_keys[data['Key_name']] = columns                
            columns.append(data['Column_name'])
            
        positions: dict[str,int] = {}
        for i, row in enumerate(self.iter_dicts(f"SHOW COLUMNS FROM {table.escaped}")):
            positions[row['Field']] = i

        return [UniqueKey(tuple(columns)) for columns in sorted(unique_keys.values(), key=lambda u: tuple(positions[c] for c in u))]

    def _get_table_foreign_key_descriptions(self, table: DbObj) -> list[dict[str,Any]]:
        # Due to a performance issue observed in MySQL (but not in MariaDB), join to r_uk and r_cu has to be made outside the DB.
        sql = f"""
        SELECT
            fk.CONSTRAINT_NAME AS constraint_name
            ,cu.COLUMN_NAME AS column_name
            ,rc.REFERENCED_TABLE_NAME AS related_table
            ,rc.UNIQUE_CONSTRAINT_NAME AS related_constraint_name
            ,cu.ORDINAL_POSITION AS ordinal_position
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS fk
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE cu ON cu.CONSTRAINT_NAME = fk.CONSTRAINT_NAME AND cu.CONSTRAINT_SCHEMA = fk.CONSTRAINT_SCHEMA AND cu.CONSTRAINT_CATALOG = fk.CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.COLUMNS c ON c.COLUMN_NAME = cu.COLUMN_NAME AND c.TABLE_NAME = fk.TABLE_NAME AND c.TABLE_SCHEMA = fk.TABLE_SCHEMA AND c.TABLE_CATALOG = fk.CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc ON rc.TABLE_NAME = fk.TABLE_NAME AND rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME AND cu.CONSTRAINT_SCHEMA = fk.CONSTRAINT_SCHEMA AND cu.CONSTRAINT_CATALOG = fk.CONSTRAINT_CATALOG
        WHERE fk.CONSTRAINT_TYPE = 'FOREIGN KEY' AND fk.TABLE_SCHEMA = DATABASE() AND fk.TABLE_NAME = {self._pos_placeholder}
        ORDER BY c.ORDINAL_POSITION
        """
        rows = self.get_dicts(sql, [table.name])
        if not rows:
            return []

        @dataclass        
        class Asso:
            constraint_name: str
            column: str
            related_column: str|None = None

        assos_by_constraint: dict[tuple[str, str], dict[int, Asso]] = {}
        for row in rows:
            constraint = (row['related_table'], row['related_constraint_name'])
            assos = assos_by_constraint.get(constraint)
            if assos:
                assos[row['ordinal_position']] = Asso(row['constraint_name'], row['column_name'])
            else:
                assos_by_constraint[constraint] = {row['ordinal_position']: Asso(row['constraint_name'], row['column_name'])}

        sql = f"""
        SELECT
            r_uk.TABLE_NAME AS related_table
            ,r_uk.CONSTRAINT_NAME AS related_constraint_name
            ,r_cu.COLUMN_NAME AS related_column_name
            ,r_cu.ORDINAL_POSITION AS ordinal_position
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS r_uk
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE r_cu ON r_cu.TABLE_NAME = r_uk.TABLE_NAME AND r_cu.CONSTRAINT_NAME = r_uk.CONSTRAINT_NAME AND r_cu.CONSTRAINT_SCHEMA = r_uk.CONSTRAINT_SCHEMA AND r_cu.CONSTRAINT_CATALOG = r_uk.CONSTRAINT_CATALOG
        WHERE r_uk.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'UNIQUE') AND r_uk.TABLE_SCHEMA = DATABASE() AND (
        """
        params = []
        for i, (related_table, related_constraint_name) in enumerate(assos_by_constraint.keys()):
            if i > 0:
                sql += " OR "
            sql += f"(r_uk.TABLE_NAME = {self._pos_placeholder} AND r_uk.CONSTRAINT_NAME = {self._pos_placeholder})"
            params += [related_table, related_constraint_name]
        sql += ")"

        for row in self.get_dicts(sql, params):
            assos = assos_by_constraint[(row['related_table'], row['related_constraint_name'])]
            assos[row['ordinal_position']].related_column = row['related_column_name']

        merged_rows: list[dict[str,Any]] = []
        for (related_table, related_constraint_name), assos in assos_by_constraint.items():
            for position, asso in assos.items():
                if not asso.related_column:
                    raise ValueError(f"Related column not found for column '{asso.column}' (position {position} in constraint {related_constraint_name} of table {related_table})")
                merged_rows.append({
                    'constraint_name': asso.constraint_name,
                    'column_name': asso.column,
                    'related_schema': None,
                    'related_table': related_table,
                    'related_column_name': asso.related_column,
                })

        return merged_rows

    #endregion


    #region Tables

    def table_exists(self, table: str|tuple|type|DbObj) -> bool:
        table = self.parse_obj(table)

        if table.schema and table.schema != 'temp':
            raise ValueError(f"Invalid schema: {table.schema}")
        
        return True if self.get_row("SELECT 1 FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'performance_schema') AND table_name = %s", [table.name]) else False

    #endregion


    #region Schemas

    _default_schema = None
    _temp_schema = None

    #endregion


    #region Databases

    def get_database_name(self) -> str|None:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT database()")
            return next(iter(cursor))[0]

    def database_exists(self, name: str) -> bool:
        sql = "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, [name])
            try:
                return next(iter(cursor))[0] == 1
            except StopIteration:
                return False

    #endregion


    #region Load and merge
    
    def copy_csv(self, file: str|os.PathLike|IO[str], table: str|tuple|type|DbObj, columns: Iterable[str|Column]|None = None, *,
            delimiter: str|None = None,
            newline: str|None = None,
            encoding = 'utf-8') -> int:

        table = self.parse_obj(table)

        if columns is None or delimiter is None or newline is None:
            examined = examine_csv_file(file, encoding=encoding)
            if columns is None:
                columns = examined.headers
            if delimiter is None:
                delimiter = examined.delimiter
            if newline is None:
                newline = examined.newline
        
        temp = None
        
        if not isinstance(file, (str,os.PathLike)):
            with NamedTemporaryFile('w', encoding=encoding, delete=False, prefix=f'tmp_load_{self.scheme}_', suffix='.csv') as temp:
                shutil.copyfileobj(file, temp.file)
            file = temp.name
        
        try:
            sql = f"LOAD DATA LOCAL INFILE %s INTO TABLE {table.escaped}"
            sql += f"\nFIELDS TERMINATED BY {self.escape_literal(delimiter)} OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"'"
            sql += f"\nLINES TERMINATED BY {self.escape_literal(newline)}"
            sql += f"\nIGNORE 1 LINES ("
            params = [file]

            vars_sql = ""
            for i, column in enumerate(columns):
                if vars_sql:
                    sql += ", "
                    vars_sql += ", "
                sql += f"@c{i}"
                vars_sql += f"{self.escape_identifier(column)} = NULLIF(@c{i}, '')"

            sql += f") SET {vars_sql}"

            try:
                self._logger.debug("Load %s to %s …", file, table)
                rowcount = self.execute(sql, params)
            except OperationalError as err:
                if len(err.args) >= 1 and err.args[0] == 3948: # Loading local data is disabled                
                    self._logger.debug("Enable loading local data (fix error 3948)", file, table)
                    self.execute("SET GLOBAL local_infile=1")
                    return self.copy_csv(file, table, columns, delimiter=delimiter, newline=newline, encoding=encoding)
                
                raise err from None
            
            self._logger.debug("%d rows loaded to %s", rowcount, table)
            return rowcount
        
        finally:
            if temp:
                os.remove(temp.name)

    def _get_convert_str_sql(self, column: Column, *, name: str|None = None, alias: str|None = None):
        if name is None:
            name = column.name
        identifier_sql = (alias if alias else '') + self.escape_identifier(name)

        # TODO: review which types should be CAST
        # python_type = self.get_python_type(column)
        # if python_type != str:
        #     sql_type = self.get_sql_type(column)
        #     return f"CAST({identifier_sql} AS {sql_type})"
        # else:
        return identifier_sql

    #endregion


def parse_mysql_message(row: tuple) -> tuple[int, str]:
    if row[0] == 'Warning':
        level = logging.WARNING
    elif row[0] == 'Error':
        level = logging.ERROR
    elif row[0] == 'Note':
        level = logging.INFO
    else:
        level = logging.WARNING
        
    message = row[2]
    return level, message
