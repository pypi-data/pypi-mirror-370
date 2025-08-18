from __future__ import annotations

import logging
import os
from typing import IO, TYPE_CHECKING, Callable, Iterable, Mapping, Sequence

from zut import Column
from zut.csv import ExaminedCsvFile, examine_csv_file
from zut.db import Db, DbObj, ForeignKey, MergeResult, UniqueKey, _get_available_name
from zut.db.operations.merge import MergeOperation
from zut.polyfills import cached_property
from zut.slugs import slugify

if TYPE_CHECKING:
    from typing import Literal


class LoadOperation:
    # ----- Load parameters -----

    src_file: str|os.PathLike|IO[str]
    """ Source data.  """ 

    dst_table: DbObj
    """ Destination table. If not set, the destination table will be a newly created temporary table. """

    columns_mapping: dict[str,Column]
    """ Headers in the source CSV file, associated to columns in the destination table (name, and the SQL type that will be used in case of creation of the destination table, or for conversion of values). """

    create_table: bool
    """ Indicate whether the destionation table must be created. """

    int_table: DbObj|None
    """ The intermediate temporary table to use to insert the data before loading in the actual destination table. This is mandatory if `key` is given, or if the destination columns have at least one foreign key. This can also be usefull to address performance issues with indexes. """

    encoding: str
    """ Encoding of the CSV file. """

    # ----- Merge parameters -----

    key: str|Sequence[str]|UniqueKey|None
    """ Reconciliate key: column(s) used to reconciliate existing records. Use `None` to disable merge (will only insert). """

    inserted_at_column: bool|str|None
    updated_at_column: bool|str|None
    changed_at_column: bool|str|None
    absent_at_column: bool|str|None
    error_code_column : bool|str|None
    error_arg_column : bool|str|None
    delete_on_absent: bool|int|None

    # ----- Attributes determined during operation initialization -----

    src_table: DbObj
    """ The temporary table that will contain only text nullable data. """

    dst_columns: dict[str,Column]
    """ Columns of the destination table that are part of the mapping. """

    foreign_keys: list[ForeignKey]
    """ Foreign keys of the destination table within the loaded columns. """
    
    delimiter: str
    """ CSV delimiter character. """
    
    newline: str
    """ CSV newline character. """

    at_least_one_file_header_discarded: bool
    """ If True, at least one header of the source CSV file is discarded. """

    # -------------------------------

    def __init__(self, db: Db, file: str|os.PathLike|IO[str], table: str|tuple|type|DbObj|None = None, columns: Iterable[str|Column|Literal['*']]|Mapping[str,str|type|Column|Literal['*']]|None = None, *,
            create_table_if_not_exists: bool|None = None,
            slugify_columns: Callable[[str],str]|bool = False,
            encoding = 'utf-8',
            # Merge options
            key: str|Sequence[str]|UniqueKey|None = None,
            inserted_at_column: bool|str|None = None,
            updated_at_column: bool|str|None = None,
            changed_at_column: bool|str|None = None,
            error_code_column : bool|str|None = None,
            error_arg_column : bool|str|None = None,
            absent_at_column: bool|str|None = None,
            delete_on_absent: bool|int|None = None):
        
        self._db = db
        self._logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__qualname__}')

        # Merge options
        self.key = key
        self.inserted_at_column = inserted_at_column
        self.updated_at_column = updated_at_column
        self.changed_at_column = changed_at_column
        self.error_code_column = error_code_column
        self.error_arg_column = error_arg_column
        self.absent_at_column = absent_at_column
        self.delete_on_absent = delete_on_absent

        # Input
        self.src_file = file
        self.encoding = encoding
        examined_src = examine_csv_file(self.src_file, encoding=encoding)
        self.delimiter = examined_src.delimiter
        self.newline = examined_src.newline

        # Table
        if table is None:
            self.dst_table = self._db.get_random_table_name('tmp_load_', temp=True)
            if not (create_table_if_not_exists is None or create_table_if_not_exists is True):
                raise ValueError(f"Invalid create_table_if_not_exists={create_table_if_not_exists} with a newly created temp table")
            self.create_table = True
        else:
            self.dst_table = self._db.parse_obj(table)

            if create_table_if_not_exists is None:
                create_table_if_not_exists = False

            if self._db.table_exists(table):
                self.create_table = False
            else:
                if not create_table_if_not_exists:
                    raise ValueError(f"Destination table {self.dst_table.unsafe} does not exist")
                else:
                    self.create_table = True

        # Columns
        if self.create_table:
            self.columns_mapping, self.at_least_one_file_header_discarded = self._get_columns_mapping(columns, slugify_columns, examined_src, all_dst_columns=None)
            self.dst_columns = self.columns_mapping

        else:            
            all_dst_columns = {column.name: column for column in self._db.get_columns(self.dst_table)}
            self.columns_mapping, self.at_least_one_file_header_discarded = self._get_columns_mapping(columns, slugify_columns, examined_src, all_dst_columns=all_dst_columns)
            mapped_dst_names = set(column.name for column in self.columns_mapping.values())
            self.dst_columns = {name: column for name, column in all_dst_columns.items() if name in mapped_dst_names}


        # Forein keys
        self.foreign_keys = [] if self.create_table else self._db.get_reversed_foreign_keys(self.dst_mapping_names, self.dst_table)

        # Intermediate table?
        self.src_table = self._db.get_random_table_name('tmp_src_', temp=True)


    def _get_columns_mapping(self, input: Iterable[str|Column|Literal['*']]|Mapping[str,str|type|Column|Literal['*']]|None, slugify_columns: Callable[[str],str]|bool, examined_src: ExaminedCsvFile, *, all_dst_columns: dict[str,Column]|None):
        if slugify_columns is True:
            slugify_columns = slugify

        # Transform input into a mapping, resolve asterisks, and indicate whether at least one file header is discarded
        columns_mapping: dict[str, Column]
        at_least_one_file_header_discarded: bool

        if not input:
            if not examined_src.headers:
                raise ValueError("No headers found in source file")
            columns_mapping = {column: Column(slugify_columns(column) if slugify_columns else column) for column in examined_src.headers}
            at_least_one_file_header_discarded = False
        
        else:
            input_mapping: Mapping[str,Column|Literal['*']]
            if isinstance(input, Mapping):
                input_mapping = input # type: ignore
            else:
                input_mapping = {}
                for column in input:
                    header_name = column.name if isinstance(column, Column) else column
                    column_name = slugify_columns(header_name) if slugify_columns else header_name

                    if column == '*':
                        pass # keep it
                    elif isinstance(column, type):
                        column = Column(column_name, type=column)
                    elif not isinstance(column, Column):
                        column = Column(column_name)

                    input_mapping[header_name] = column

            mapping_tuples: list[tuple[str, Column]] = []
            asterisk_pos = None
            found_src_headers = set()
            missing_src_headers = []
            for pos, (header_name, column) in enumerate(input_mapping.items()):
                if column == '*':
                    if asterisk_pos is not None:
                        raise ValueError("Parameter 'columns' cannot have several '*'")
                    asterisk_pos = pos
                else:
                    if not examined_src.headers:
                        raise ValueError("No headers found in source file")
                    if header_name in examined_src.headers:
                        found_src_headers.add(header_name)
                    else:
                        missing_src_headers.append(header_name)

                    mapping_tuples.append((header_name, column))

            if missing_src_headers:
                raise ValueError(f"Header not found in source CSV file: {', '.join(missing_src_headers)}")
        
            columns_mapping = {}
            discarded = None
            for pos, (header_name, column) in enumerate(mapping_tuples):
                if pos == asterisk_pos:
                    discarded = False
                    if not examined_src.headers:
                        raise ValueError("No headers found in source file")
                    for column in examined_src.headers:
                        if not column in found_src_headers:
                            columns_mapping[column] = Column(column)
                else:
                    columns_mapping[header_name] = column

            if discarded is None:
                if not examined_src.headers:
                    raise ValueError("No headers found in source file")
                discarded = any(src_name for src_name in examined_src.headers if src_name not in columns_mapping)
            at_least_one_file_header_discarded = discarded

        # Check existency of the column in destination table and complete the mapping with the params of the column in the destination table
        if all_dst_columns is not None:
            for header, column in columns_mapping.items():
                dst_column = all_dst_columns.get(column.name)
                if not dst_column:
                    raise ValueError(f"Column '{column.name}' (mapped to CSV header '{header}') is not part of the destination table")
                if dst_column.identity:
                    raise ValueError(f"Column '{column.name}' (mapped to CSV header '{header}') cannot be used because this is an identity (auto-generated) column")
                
                # (complete the column information)
                if not column.type or (isinstance(column.type, type) and isinstance(dst_column, str)):
                    column.type = dst_column.type
                    column.precision = dst_column.precision
                    column.scale = dst_column.scale

                if column.not_null is None:
                    column.not_null = dst_column.not_null

                if column.primary_key is None:
                    column.primary_key = dst_column.primary_key

                if column.default is None:
                    column.default = dst_column.default

        return columns_mapping, at_least_one_file_header_discarded


    @cached_property
    def src_mapping_names(self) -> list[str]:
        return list(self.columns_mapping.keys())


    @cached_property
    def dst_mapping_names(self) -> list[str]:
        return list(column.name for column in self.columns_mapping.values())


    def run(self) -> MergeResult:
        # Create destination table if necessary
        if self.create_table:
            self._db.create_table(self.dst_table, self.dst_columns.values(), primary_key=True, merge_status_columns=True if self.key and not self.dst_table.temp else False)

        # Create temporary source table
        src_pk_name = _get_available_name('_pk', self.columns_mapping.keys())
        src_pk_column = Column(src_pk_name, type=int, not_null=True, primary_key=True, identity=True)
        src_columns = self._db.create_table(self.src_table, [src_pk_column] + [Column(dst_column.name) for dst_column in self.columns_mapping.values()])

        try:
            # Populate src_table from src_file
            self._db.copy_csv(self.src_file, self.src_table, self.src_mapping_names, delimiter=self.delimiter, newline=self.newline, encoding=self.encoding)

            # Merge src_table in dst_table
            merge_op = MergeOperation(self._db, self.src_table, self.dst_table, self.columns_mapping.values(),
                key = self.key,
                inserted_at_column = self.inserted_at_column,
                updated_at_column = self.updated_at_column,
                changed_at_column = self.changed_at_column,
                error_code_column = self.error_code_column,
                error_arg_column = self.error_arg_column,
                absent_at_column = self.absent_at_column,
                delete_on_absent = self.delete_on_absent)
            
            # (set optimization shortcuts)
            merge_op.src_columns = {column.name: column for column in src_columns}
            merge_op.dst_columns = self.dst_columns
            merge_op.foreign_keys = self.foreign_keys
            
            # (run and set result)
            result = merge_op.run()
            result.src = self.src_file
            result.columns_mapping = self.columns_mapping
            return result

        finally:
            self._db.drop_table(self.src_table)
