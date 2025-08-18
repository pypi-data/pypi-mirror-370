from __future__ import annotations

from functools import cached_property
import logging
from typing import TYPE_CHECKING, Callable, Iterable, Mapping, Sequence

from zut import Column, NotImplementedBy
from zut.db import Db, DbObj, MergeResult, ForeignKey, UniqueKey
from zut.slugs import slugify

if TYPE_CHECKING:
    from typing import Literal


class MergeOperation:
    # ----- Merge parameters -----
    # (see also properties defined later)

    src_table: DbObj
    """ Source table """

    dst_table: DbObj
    """ Destination table """
    
    key: UniqueKey|None
    """ Reconciliate key: column(s) used to reconciliate existing records. """

    def __init__(self, db: Db, src_table: str|tuple|type|DbObj, dst_table: str|tuple|type|DbObj, columns: Iterable[str|Column|Literal['*']]|Mapping[str,str|type|Column|Literal['*']]|None = None, *,
            key: str|Sequence[str]|UniqueKey|None,
            slugify_columns: Callable[[str],str]|bool = False,
            inserted_at_column: bool|str|None = None,
            updated_at_column: bool|str|None = None,
            changed_at_column: bool|str|None = None,
            error_code_column : bool|str|None = None,
            error_arg_column : bool|str|None = None,
            absent_at_column: bool|str|None = None,
            delete_on_absent: bool|int|None = None):
        
        self._db = db
        self._logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__qualname__}')

        self.src_table = self._db.parse_obj(src_table)
        self.dst_table = self._db.parse_obj(dst_table)

        if key is not None:
            if not isinstance(key, UniqueKey):
                key = UniqueKey(key)
        self.key = key

        self.delete_on_absent = delete_on_absent

        # Will be prepared later (to give a change to LoadOperation to provide optimization shortcuts)
        self._columns = columns
        self._slugify_columns = slugify_columns

        self._columns_mapping = None
        self._src_columns = None
        self._src_pk = None
        self._dst_columns = None
        self._foreign_keys = None

        self._inserted_at_column_input = inserted_at_column
        self._updated_at_column_input = updated_at_column
        self._changed_at_column_input = changed_at_column
        self._absent_at_column_input = absent_at_column


    @property
    def columns_mapping(self) -> dict[str, Column]:
        """
        Association of source columns with destination columns.
        
        Requires `src_columns`.
        Must be completed and validated with `_finalize_columns_mapping()` (which requires `dst_columns`).
        """
        if self._columns_mapping is None:
            if self._slugify_columns is True:
                self._slugify_columns = slugify

            if not self._columns:
                self._columns_mapping = {column.name: column for column in self.src_columns.values() if not column.identity}
            
            else:
                input_mapping: Mapping[str,Column|Literal['*']]
                if isinstance(self._columns, Mapping):
                    input_mapping = self._columns # type: ignore
                else:
                    input_mapping = {}
                    for dst_column in self._columns:
                        src_name = dst_column.name if isinstance(dst_column, Column) else dst_column
                        dst_name = self._slugify_columns(src_name) if self._slugify_columns else src_name

                        if dst_column == '*':
                            pass # keep it
                        elif isinstance(dst_column, type):
                            dst_column = Column(dst_name, type=dst_column)
                        else:
                            dst_column = Column(dst_name)

                        input_mapping[src_name] = dst_column

                mapping_tuples: list[tuple[str, Column]] = []
                asterisk_pos = None
                found_src_column_names = set()
                missing_src_columns = []
                for pos, (src_name, dst_column) in enumerate(input_mapping.items()):
                    if dst_column == '*':
                        if asterisk_pos is not None:
                            raise ValueError("Parameter 'columns' cannot have several '*'")
                        asterisk_pos = pos
                    else:           
                        if src_name in self.src_columns:
                            found_src_column_names.add(src_name)
                        else:
                            missing_src_columns.append(src_name)
                        mapping_tuples.append((src_name, dst_column))

                if missing_src_columns:
                    raise ValueError(f"Columns not found in source table: {', '.join(missing_src_columns)}")
            
                self._columns_mapping = {}
                for pos, (src_name, dst_column) in enumerate(mapping_tuples):
                    if pos == asterisk_pos:
                        for dst_column in self.src_columns:
                            if not dst_column in found_src_column_names:
                                self._columns_mapping[dst_column] = Column(dst_column)
                    else:
                        self._columns_mapping[src_name] = dst_column

        return self._columns_mapping


    def _finalize_columns_mapping(self):
        for src_name, dst_column in self.columns_mapping.items():
            if not (actual_dst_column := self.dst_columns.get(dst_column.name)):
                raise ValueError(f"Column not found in destination table: {dst_column}")
        
            if actual_dst_column.identity:
                raise ValueError(f"Destination column '{actual_dst_column.name}' (mapped to source column '{src_name}') cannot be used because this is an identity (auto-generated) column")
            
            # (complete the column information)
            if not dst_column.type or (isinstance(dst_column.type, type) and isinstance(actual_dst_column, str)):
                dst_column.type = actual_dst_column.type
                dst_column.precision = actual_dst_column.precision
                dst_column.scale = actual_dst_column.scale

            if dst_column.not_null is None:
                dst_column.not_null = actual_dst_column.not_null

            if dst_column.primary_key is None:
                dst_column.primary_key = actual_dst_column.primary_key

            if dst_column.default is None:
                dst_column.default = actual_dst_column.default
    

    def _get_merge_status_column(self, status: Literal['inserted', 'updated', 'changed', 'absent']) -> str|None:
        input_value = getattr(self, f'_{status}_at_column_input')
        if input_value is False:
            return None
        if isinstance(input_value, str):
            return input_value
        
        default_value = getattr(self._db, f'{status}_at_column')
        if input_value is True:
            return default_value
        if input_value is not None:
            raise TypeError(f'{status}_at_column: {type(input_value).__name__}')
        return default_value if default_value in self.dst_columns else None
    

    @property
    def src_columns(self) -> dict[str,Column]:
        """ All columns of the source table (even if they are not part of the merge). """
        if self._src_columns is None:
            self._src_columns = {column.name: column for column in self._db.get_columns(self.src_table)}
        return self._src_columns
    
    @src_columns.setter
    def src_columns(self, value):
        self._src_columns = value


    @property
    def dst_columns(self) -> dict[str,Column]:
        """ All columns of the destination table (even if they are not part of the merge). """
        if self._dst_columns is None:
            self._dst_columns = {column.name: column for column in self._db.get_columns(self.dst_table)}
        return self._dst_columns
    
    @dst_columns.setter
    def dst_columns(self, value):
        self._dst_columns = value


    @property
    def foreign_keys(self) -> list[ForeignKey]:
        """ Foreign keys within the merged columns. """
        if self._foreign_keys is None:
            self._foreign_keys = self._db.get_reversed_foreign_keys(self.src_column_names, self.dst_table)
        return self._foreign_keys
    
    @foreign_keys.setter
    def foreign_keys(self, value):
        self._foreign_keys = value


    @cached_property
    def src_column_names(self) -> list[str]:
        return list(self.columns_mapping.keys())


    @cached_property
    def dst_column_names(self) -> list[str]:
        return list(column.name for column in self.columns_mapping.values())


    @cached_property
    def src_column_names_by_dst_column_name(self) -> dict[str, str]:
        return {dst_column.name: src_name for src_name, dst_column in self.columns_mapping.items()}


    @cached_property
    def src_pk(self) -> list[Column]:
        result = [column for column in self.src_columns.values() if column.primary_key]
        if not result:
            raise ValueError("Source table does not have a primary key")
        return result

    @cached_property
    def src_columns_escaped(self) -> str:
        return ', '.join(self._db.escape_identifier(column) for column in self.src_columns.values())

    @cached_property
    def src_pk_escaped(self) -> str:
        return ', '.join(self._db.escape_identifier(column) for column in self.src_pk)


    def run(self) -> MergeResult:
        check_table = None
        try:
            self._finalize_columns_mapping()
            check_table = self._check()
            
            self.inserted_at_column = self._get_merge_status_column('inserted')
            self.updated_at_column = self._get_merge_status_column('updated')
            self.changed_at_column = self._get_merge_status_column('changed')
            self.absent_at_column = self._get_merge_status_column('absent')

            if self.key:
                key_mapping = {self.src_column_names_by_dst_column_name[dst_name]: dst_name for dst_name in self.key.columns}
                if self._db._merge_statement:
                    return self._merge_with_standard_statement(key_mapping)
                else:
                    return self._merge_with_alternative_statements(key_mapping)
            else:
                return self._copy()

        finally:
            if check_table:
                self._db.drop_table(check_table)


    def _check(self) -> DbObj|None:
        if not self.foreign_keys: #TODO: also check for conversions
            return None
        
        columns = [pk.replace(name=f'src_pk{i+1}') for i, pk in enumerate(self.src_pk)]
        check_pk_escaped = ', '.join(self._db.escape_identifier(column) for column in columns)
        columns += [Column('error_code', type=int), Column('error_arg', type=int)]
        for i, fk in enumerate(self.foreign_keys):
            column = Column(f'fk{i+1}_id', type=int)  #TODO: récupérer les infos sur la clé de la FK, y compris le type
            columns.append(column)

        check_table = self._db.get_random_table_name('tmp_check_', temp=True)
        self._db.create_table(check_table, columns)

        sql = f"INSERT INTO {check_table.escaped} ({check_pk_escaped})"
        sql += f"\nSELECT {self.src_pk_escaped} FROM {self.src_table.escaped}"
        self._db.execute(sql)

        for i, fk in enumerate(self.foreign_keys):
            self._logger.debug("Check fk%d: %s", i, fk.basename)
            #TODO/ROADMAP: Do it, recursively if required [prévoir une fonction spécifiquement pour cela vu la complexité potentielle

        return check_table
    

    def _merge_with_standard_statement(self, key_mapping: dict[str, str]) -> MergeResult:
        """ Use MERGE standard SQL statement. """

        sql = f"MERGE INTO {self.dst_table.escaped} dst"
        sql += f"\nUSING SELECT {', '.join(self._get_select_sql(src_name, dst_column) for src_name, dst_column in self.columns_mapping.items())}"
        sql += f"\nFROM {self.src_table.escaped} src"

        # Reconciliation with the key
        sql += f"\nON " + ' AND '.join(f"dst.{self._db.escape_identifier(src_name)} = src.{self._db.escape_identifier(dst_name)}" for src_name, dst_name in key_mapping.items())
        
        # Insert
        sql += f"\nWHEN NOT MATCHED THEN INSERT ("
        sql += ', '.join(self._db.escape_identifier(dst_column) for dst_column in self.columns_mapping.values())
        if self.inserted_at_column:
            sql += ', ' + self._db.escape_identifier(self.inserted_at_column)
        sql += ") VALUES ("
        sql += ', '.join(f"src.{self._db.escape_identifier(src_name)}" for src_name in self.columns_mapping.keys())
        if self.inserted_at_column:
            sql += ', ' + self._db.get_now_sql()
        sql += ")"

        # (prepare for changed or updated)
        update_sql = ''
        for src_name, dst_column in self.columns_mapping.items():
            update_sql += (', ' if update_sql else '') + f"{self._db.escape_identifier(dst_column)} = src.{self._db.escape_identifier(src_name)}"

        # Changed
        if self.changed_at_column:
            nochange_condition_sql = ''
            for src_name, dst_column in self.columns_mapping.items():
                dst = f"dst.{self._db.escape_identifier(dst_column)}"
                src = f"src.{self._db.escape_identifier(src_name)}"
                column_sql = f"{dst} = {src}"
                if not dst_column.not_null:
                    column_sql = f"({column_sql} OR ({dst} IS NULL AND {src} IS NULL))"
                nochange_condition_sql += (' AND ' if nochange_condition_sql else '') + column_sql

            sql += f"\nWHEN MATCHED AND NOT ({nochange_condition_sql}) THEN UPDATE SET {update_sql}"
            sql += f", {self._db.escape_identifier(self.changed_at_column)} = {self._db.get_now_sql()}"

        # Updated
        if not self.changed_at_column or self.updated_at_column:
            sql += f"\nWHEN MATCHED THEN UPDATE SET {update_sql}"
            if self.updated_at_column:
                sql += f", {self._db.escape_identifier(self.updated_at_column)} = {self._db.get_now_sql()}"

        # Absent
        if self.delete_on_absent:
            sql += f"\nWHEN NOT MATCHED BY SOURCE THEN DELETE"        
        elif self.absent_at_column:
            sql += f"\nWHEN NOT MATCHED BY SOURCE THEN UPDATE SET {self._db.escape_identifier(self.absent_at_column)} = {self._db.get_now_sql()}"

        self._logger.debug("Merge %s into %s", self.src_table.unsafe, self.dst_table.unsafe)
        rowcount = self._db.execute(sql)
        #TODO: get results
        return MergeResult(self._db, self.src_table, self.dst_table, self.columns_mapping, rowcount)
        

    def _merge_with_alternative_statements(self, key_mapping: dict[str, str]) -> MergeResult:
        raise NotImplementedBy(self.__class__, "merge with alternative to standard MERGE statement")


    def _copy(self) -> MergeResult:
        #TODO: add merge status columns?

        sql = f"INSERT INTO {self.dst_table.escaped} (" + ", ".join(self._db.escape_identifier(dst_column) for dst_column in self.columns_mapping.values()) + ")"
        sql += f"\nSELECT {', '.join(self._get_select_sql(src_name, dst_column) for src_name, dst_column in self.columns_mapping.items())}"
        sql += f"\nFROM {self.src_table.escaped} src"

        self._logger.debug("Copy %s into %s", self.src_table.unsafe, self.dst_table.unsafe)
        rowcount = self._db.execute(sql)
        return MergeResult(self._db, self.src_table, self.dst_table, self.columns_mapping, rowcount)
    

    def _get_select_sql(self, src_name: str, dst_column: Column):
        # TODO: conversions + foreign key translations
        return self._db._get_convert_str_sql(dst_column, name=src_name)
