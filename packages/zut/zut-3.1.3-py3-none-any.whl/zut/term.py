"""
Write temporary text on the console.
"""
from __future__ import annotations

import os
import sys
from time import time_ns


_transient_to_erase: dict[bool, list[int]] = {False: [], True: []}
_last_transient:  dict[bool, float|None] = {False: None, True: None}

def write_transient(text: str, *, stdout = False, newline=False, delay: float|int|None = None):
    """
    Write text to the terminal, keeping track of what was written, so that it can be erased later.

    Text lines are stripped to terminal column length.
    """    
    t = time_ns()
    if delay is not None:
        t0 = _last_transient[stdout]
        if t0 is not None and (t - t0) / 1E9 < delay:
            return

    file = sys.stdout if stdout else sys.stderr
    if not sys.stderr.isatty(): # Ignore if we're not on a terminal
        return
    
    erase_transient(stdout=stdout)
    columns, _ = os.get_terminal_size()

    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.rstrip()
        
        nb_chars = len(line)
        if nb_chars > columns:
            line = line[:columns-1] + '…'
            nb_chars = columns

        _transient_to_erase[stdout].insert(0, nb_chars)

        file.write(line)
        if newline or i < len(lines) - 1:
            file.write('\n')

    if newline:
        _transient_to_erase[stdout].insert(0, 0)
    
    file.flush()
    _last_transient[stdout] = t


def erase_transient(*, stdout = False):
    """
    Erase text written using :func:`write_transient`.

    Text lines are stripped to terminal column length.
    """
    if not _transient_to_erase[stdout]:
        return
    
    file = sys.stdout if stdout else sys.stderr
    for i, nb_chars in enumerate(_transient_to_erase[stdout]):
        if i == 0:
            file.write('\r') # move to beginning of line
        else:
            file.write('\033[F') # move to beginning of previous line
        file.write(' ' * nb_chars)
    file.write('\r')

    _transient_to_erase[stdout].clear()
    _last_transient[stdout] = None
