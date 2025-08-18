from __future__ import annotations

import os
import sys
from contextlib import nullcontext
from typing import IO, TYPE_CHECKING, Any, Mapping

from zut import Column

if TYPE_CHECKING:
    from typing import Iterable, Literal, Sequence

try:
    from tabulate import tabulate  # type: ignore

except ModuleNotFoundError:
    def tabulate(tabular_data: Iterable[Iterable|Mapping], headers: Sequence[str]|Literal['keys']|None = None):
        if headers:
            if headers == 'keys':
                first_row = next(iter(tabular_data), None)
                if not isinstance(first_row, Mapping):
                    raise ValueError(f"First row must be a dict, got {type(first_row).__name__}")
                headers = [key for key in first_row]
            result = '\t'.join(str(header) for header in headers)
            result += '\n' + '\t'.join('-' * len(header) for header in headers)
        else:
            result = ''

        for row in tabular_data:
            if isinstance(row, Mapping):
                if not headers:
                    raise ValueError("Cannot use dict rows without headers. Specify headers='keys' to use keys of the first dict as headers.")
                row = {header: row.get(header) for header in headers}
            result += ('\n' if result else '') + '\t'.join(str(value) for value in row)

        return result


def dump_tabulate(data: Any, headers: Sequence[str|Column]|dict[str,Any]|None = None, *, file: str|os.PathLike|IO[str] = sys.stdout):
    if headers is None or headers == 'keys':
        _headers = 'keys'
    else:
        _headers = [str(header) if not isinstance(header, str) else header for header in headers]

    if _headers != 'keys':
        data = [[elem.get(key, None) for key in _headers] if isinstance(elem, dict) else elem for elem in data]
    
    text = tabulate(data, _headers)
    with open(file, 'w', encoding='utf-8') if isinstance(file, (str,os.PathLike)) else nullcontext(file) as file:
        file.write(text) # type: ignore
        file.write('\n') # type: ignore


__all__ = ('tabulate', 'dump_tabulate')
