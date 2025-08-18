"""
Graph utilities.
"""
from __future__ import annotations

from typing import Iterable, Mapping, TypeVar

T = TypeVar('T')

def topological_sort(source: Mapping[T,None|T|Iterable[T]]) -> list[T]:
    """
    Perform a topological sort.

    - `source`: dictionnary associating keys to list of dependencies
    - returns a list of keys, sorted with dependencies first
    """
    #See: https://stackoverflow.com/a/11564323
    pending = [(key, set() if deps is None else (set([deps]) if isinstance(deps, type(key)) else set(deps))) for key, deps in source.items()] # copy deps so we can modify set in-place  # type: ignore
    emitted = []
    result = []

    while pending:
        next_pending = []
        next_emitted = []

        for entry in pending:
            key, deps = entry
            deps.difference_update(emitted) # remove deps we emitted last pass
            if deps: # still has deps? recheck during next pass
                next_pending.append(entry) 
            else: # no more deps? time to emit
                result.append(key)
                emitted.append(key) # <-- not required, but helps preserve original ordering
                next_emitted.append(key) # remember what we emitted for difference_update() in next pass

        if not next_emitted: # all entries have unmet deps, one of two things is wrong...
            raise ValueError("Cyclic or missing dependency detected: %r" % (next_pending,))
        
        pending = next_pending
        emitted = next_emitted

    return result
