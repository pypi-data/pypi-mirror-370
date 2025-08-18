from __future__ import annotations

import inspect
import logging
import os
import re
from pathlib import Path

from zut import skip_utf8_bom

from django.conf import settings
from django.db.migrations import RunSQL
from django.db.migrations.operations.base import Operation

_logger = logging.getLogger(__name__)


def get_sql_migration_operations(path: str|os.PathLike|None = None, vars: dict|None = None) -> list[Operation]:
    def get_ordered_files(directory: str|os.PathLike, *, ext: str|None = None, recursive: bool = False) -> list[Path]:
        if not isinstance(directory, Path):
            directory = Path(directory)

        if ext and not ext.startswith('.'):
            ext = f'.{ext}'

        def generate(directory: Path):
            for path in sorted(directory.iterdir(), key=lambda entry: (0 if entry.is_dir() else 1, entry.name)):
                if path.is_dir():
                    if recursive:
                        yield from generate(path)
                elif not ext or path.name.lower().endswith(ext):
                    yield path

        return [ path for path in generate(directory) ]

    def get_sql_and_reverse_sql(file: str|os.PathLike):
        sql = None
        reverse_sql = None

        with open(file, 'r', encoding='utf-8') as fp:
            skip_utf8_bom(fp)

            while True:
                line = fp.readline()
                if not line:
                    break
                if vars:
                    for name, value in vars.items():
                        line = line.replace("{"+name+"}", value)

                if reverse_sql is None:
                    # search !reverse mark
                    stripped_line = line = line.strip()
                    if stripped_line.startswith('--') and stripped_line.lstrip(' -\t').startswith('!reverse'):
                        reverse_sql = line
                    else:
                        sql = (sql + '\n' if sql else '') + line
                else:
                    reverse_sql += '\n' + line

        return sql, reverse_sql

    if path is None:
        calling_module = inspect.getmodule(inspect.stack()[1][0])
        if not calling_module:
            raise ValueError("Cannot find calling module")
        if not calling_module.__file__:
            raise ValueError("Calling module has not __file__: %s" % (calling_module,))
        calling_file = Path(calling_module.__file__)
        path = calling_file.parent.joinpath(calling_file.stem).with_suffix('.sql')
        if not path.exists():
            path = calling_file.parent.joinpath(calling_file.stem).with_suffix('')
    elif not isinstance(path, Path):
        path = Path(path)

    if path.is_file():
        sql, reverse_sql = get_sql_and_reverse_sql(path)
        return [RunSQL(sql, reverse_sql)]
    elif path.is_dir():
        operations = []

        for path in get_ordered_files(path, ext='.sql', recursive=True):
            sql, reverse_sql = get_sql_and_reverse_sql(path)
            operations.append(RunSQL(sql, reverse_sql))

        return operations
    else:
        raise ValueError(f"Migration path not found: {path}")


def check_migration_sql_file_names():
    def check_file(path: Path):
        _logger.debug("Check migration SQL file name: %s", path)

        m = re.match(r'^[0-9]+\-(.+)$', path.stem)
        if m:
            expected_name = m[1]
        else:
            expected_name = path.stem

        with open(path, 'r', encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                if re.match(r'^--\s*check_migration_sql_file_names:skip', line, re.IGNORECASE):
                    return
                if line == '' or line.startswith('--'):
                    continue
                if re.match(r'^DROP\s+', line, re.IGNORECASE):
                    continue
                m = re.match(r'^CREATE\s+(?:OR\s+REPLACE\s+)?(?P<type>VIEW|FUNCTION|PROCEDURE|TABLE|EXTENSION)\s+"?(?P<name>[^;"\s\(\)]+)"?', line, re.IGNORECASE)
                if m:
                    type = m['type'].strip().upper()
                    name = m['name'].strip()
                    m = re.match(r'^\s*IF\s*NOT\s*EXISTS\s*(.+)$', name)
                    if m:
                        name = m[1].strip()
                    
                    if name != expected_name:
                        _logger.warning(f"Invalid {type} name \"{name}\" in SQL migration file {path} (expected \"{expected_name}\")")
                    return
                else:
                    _logger.warning(f"Unexpected line \"{line}\" in SQL migration file {path}")
                    return

    path: Path
    for path in settings.BASE_DIR.glob('**/migrations/**/*.sql'):
        if re.match(r'^[0-9]{4}_', path.name) or any(not re.match(r'^[a-zA-Z0-9_]+$', part) for part in path.relative_to(settings.BASE_DIR).with_suffix('').parts):
            continue
        check_file(path)
