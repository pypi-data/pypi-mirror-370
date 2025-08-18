"""
Write and read using JSON format.
"""
from __future__ import annotations

import json
import os
import sys
from contextlib import AbstractContextManager, contextmanager
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, Flag
from tempfile import NamedTemporaryFile
from typing import IO, Any
from uuid import UUID

from zut import skip_utf8_bom
from zut.polyfills import ZipPath


#region Write JSON

class ExtendedJSONEncoder(json.JSONEncoder):
    """
    Adapted from: django.core.serializers.json.DjangoJSONEncoder
    
    Usage example: json.dumps(data, indent=4, cls=ExtendedJSONEncoder)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def default(self, o):
        if isinstance(o, datetime):
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            if o.tzinfo is not None:
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:12]
            return f'T{r}'
        elif isinstance(o, timedelta):
            from zut.convert import get_duration_str
            return get_duration_str(o)
        elif isinstance(o, (Decimal, UUID)):
            return str(o)
        else:
            try:
                from django.utils.functional import \
                    Promise  # type: ignore (optional dependency)
                if isinstance(o, Promise):
                    return str(o)
            except ModuleNotFoundError:
                pass

            if isinstance(o, (Enum,Flag)):
                return o.value
            elif isinstance(o, bytes):
                return str(o)
            else:
                return super().default(o)


class JsonWriter:
    default_indent: int|None = 2
    default_encoder: type[json.JSONEncoder] = ExtendedJSONEncoder


def dump_json(data: Any, file: str|os.PathLike|IO[str], *, indent: int|None = None, sort_keys = False, ensure_ascii = False, cls: type[json.JSONEncoder]|None = None, encoding = 'utf-8', archivate: bool|str|os.PathLike|ZipPath|None = None):
    if indent is None:
        indent = JsonWriter.default_indent
    if cls is None:
        cls = JsonWriter.default_encoder

    _file_manager: AbstractContextManager[IO[str]]|None
    _file: IO[str]
    if isinstance(file, (str, os.PathLike)):
        from zut import files
        if archivate:
            files.archivate(file, archivate, missing_ok=True)
        _file_manager = files.open(file, 'w', encoding=encoding, mkdir=True)
        _file = _file_manager.__enter__()
    else:
        _file_manager = None # managed externally
        _file = file

    try:
        json.dump(data, _file, ensure_ascii=ensure_ascii, indent=indent, sort_keys=sort_keys, cls=cls)
        if _file == sys.stdout or _file == sys.stderr:
            _file.write('\n')
    finally:
        if _file_manager:
            _file_manager.__exit__(None, None, None)


@contextmanager
def dump_json_temp(data: Any, *, encoding = 'utf-8', indent: int|None = None, sort_keys = False, ensure_ascii = False, cls: type[json.JSONEncoder]|None = None):
    temp = None
    try:
        with NamedTemporaryFile('w', encoding=encoding, suffix='.json', delete=False) as temp:
            dump_json(data, temp.file, ensure_ascii=ensure_ascii, indent=indent, sort_keys=sort_keys, cls=cls)
 
        yield temp.name
    finally:
        if temp is not None:
            os.unlink(temp.name)

#endregion


#region Read JSON

class ExtendedJSONDecoder(json.JSONDecoder):
    def __init__(self, *, object_hook = None, **options):
        super().__init__(object_hook=object_hook or self._object_hook, **options)

    def _object_hook(self, data: dict):
        for key, value in data.items():
            if isinstance(value, str):
                from zut.convert import recognize_datetime
                value = recognize_datetime(value)
                if isinstance(value, datetime):
                    data[key] = value
        
        return data


class JsonLoader:
    default_decoder: type[json.JSONDecoder] = ExtendedJSONDecoder


def load_json(file: str|os.PathLike|IO[str], *, encoding = 'utf-8', cls: type[json.JSONDecoder]|None = None) -> Any:
    if cls is None:
        cls = JsonLoader.default_decoder
    
    _file_manager: AbstractContextManager[IO[str]]|None
    _file: IO[str]
    if isinstance(file, (str, os.PathLike)):
        from zut import files
        _file_manager = files.open(file, 'r', encoding=encoding)
        _file = _file_manager.__enter__()
    else:
        _file_manager = None # managed externally
        _file = file

    try:
        skip_utf8_bom(_file)
        return json.load(_file, cls=cls)
    finally:
        if _file_manager:
            _file_manager.__exit__(None, None, None)

#endregion
