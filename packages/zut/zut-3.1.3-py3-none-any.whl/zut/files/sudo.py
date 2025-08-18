"""
Implementation of `zut.files` to access files via sudo.
"""
from __future__ import annotations

import os
from getpass import getuser

from zut.files import BaseAdapter, FileAdapter, BaseOpenTempContext
from zut.process import RunProcessError, run_process


class SudoOpenContext(BaseOpenTempContext[str]):
    def before_open_temp(self):
        if self.is_reading:
            run_process(['cp', self.path, self.temp_path], check=True, sudo=True)
            run_process(['chown', getuser(), self.temp_path], check=True, sudo=True)

    def after_close_temp(self):
        if self.is_writing:
            run_process(['cp', self.temp_path, self.path], check=True, sudo=True)


class SudoAdapter(BaseAdapter[str]):
    open_context_cls = SudoOpenContext

    @classmethod
    def normalize_path(cls, path: str|os.PathLike) -> str:
        if not isinstance(path, str):
            path = str(path)
        if path.startswith('sudo:'):
            path = path[5:]
        return path
    
    @classmethod
    def open(cls, path: str|os.PathLike, mode: str = 'r', buffering: int = -1, encoding: str|None = None, errors: str|None = None, newline: str|None = None):
        path = cls.normalize_path(path)
        if os.access(path, os.R_OK if 'r' in mode else os.W_OK):
            return open(path, mode, buffering, encoding, errors, newline)
        return SudoOpenContext(path, mode, buffering, encoding, errors, newline)

    @classmethod
    def exists(cls, path: str|os.PathLike):
        path = cls.normalize_path(path)
        if cls._dir_access_to_parent(path):
            return FileAdapter.exists(path)
        
        escaped_path = str(path).replace('"', '\\"')
        cp = run_process(['sh', '-c', f'[ -e "{escaped_path}" ] && echo 1 || echo 0'], check=True, capture_output=True, strip='rstrip-newline', sudo=True)
        if cp.stdout == '1':
            return True
        elif cp.stdout == '0':
            return False
        else:
            raise ValueError(f"Invalid result: {cp.stdout}")

    @classmethod
    def _remove(cls, path: str|os.PathLike, *, tree_ok: bool = False):
        path = cls.normalize_path(path)
        if not cls.exists(path):
            raise FileNotFoundError(f"No such file or directory: '{path}'")
        
        try:
            args = ['rm']
            if tree_ok:
                args += ['-r']
            run_process([*args, path], check=True, capture_output=True, sudo=True)
        except RunProcessError as err:
            if err.returncode != 1 or tree_ok:
                raise err from None
            
            # Might be a directory
            try:
                run_process(['rmdir', path], check=True, capture_output=True, sudo=True)
            except RunProcessError as err:
                raise err from None               

    @classmethod
    def _makedirs(cls, path: str|os.PathLike):
        path = cls.normalize_path(path)
        if cls._dir_access_to_parent(path):
            return FileAdapter._makedirs(path)

        if cls.exists(path):
            raise FileExistsError(f"File exists: '{path}'")
        
        run_process(['mkdir', '-p', path], check=True, capture_output=True, strip='rstrip-newline', sudo=True)

    @classmethod
    def _dir_access_to_parent(cls, path: str):
        parent = os.path.dirname(path) or '.'
        return os.access(parent, os.X_OK)
