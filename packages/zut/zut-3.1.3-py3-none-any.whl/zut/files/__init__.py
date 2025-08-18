"""
A standardized interface to access different kinds of "files": entries in ZIP archives, samba shares, S3 objects, access via sudo.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from contextlib import AbstractContextManager
from datetime import datetime
from io import (BufferedRandom, BufferedReader, BufferedWriter, FileIO, IOBase,
                TextIOWrapper)
from tempfile import mktemp
from typing import (IO, TYPE_CHECKING, Callable, Generic,
                    Sequence, TypeVar, overload)
from urllib.parse import urlparse

if TYPE_CHECKING:
    from typing import Literal
    from _typeshed import (OpenBinaryMode, OpenBinaryModeReading, OpenBinaryModeUpdating, OpenBinaryModeWriting, OpenTextMode)

from zut import (Secret, SudoNotAvailable, NotImplementedBy, get_logger, is_secret_defined,
                 is_sudo_available)
from zut.tz import make_aware, make_naive
from zut.polyfills import ZipPath

_logger = get_logger(__name__)


#region High-level utilities

def archivate(path: str|os.PathLike, archive_dir: bool|str|os.PathLike|ZipPath|None = None, *, missing_ok: bool = False, keep: bool = False) -> str|None:
    """
    Archivate `path` to `archive_dir` directory (or zip entry), ensuring unique archive name.

    :param archive_dir: By default (if None), use the same directory as the origin path. If relative (e.g. 'archive'), it is relative to the directory of the original path.
    :param missing_ok: If True, do not throw an exception if the original file does not exist.
    :param keep: If True, the original file is not removed after archiving.
    """
    if archive_dir is False:
        # Disabled
        return None
    
    if not exists(path):
        if missing_ok:
            return
        raise FileNotFoundError(f'Path does not exist: {path}')

    if archive_dir is None or archive_dir is True:
        archive_dir = dirname(path) or '.'

    if not isinstance(archive_dir, ZipPath):
        if not isabs(archive_dir):
            archive_dir = join(dirname(path), archive_dir)
        if not exists(archive_dir):
            makedirs(archive_dir)

    modified_at = get_modified_at(path)
    stem, suffix = os.path.splitext(basename(path))
    prefix = stem + f"_{modified_at.strftime('%Y%m%d')}"
    i = 1
    while True:
        archive = join(archive_dir, prefix + (f"-{modified_at.strftime('%H%M%S')}" if i > 1 else '') + suffix)
        if not exists(archive):
            break
        i += 1

    _logger.debug(f"Archivate %s to %s", path, archive)
    copy2(path, archive)
    if not keep:
        remove(path)
    return archive

#endregion


#region High-level read-write functions

def read_bytes(path: str|os.PathLike, *, mkdir: bool = False, sudo: bool = False) -> bytes:
    """
    Open the file in bytes mode, read it, and close the file.
    """
    with open(path, 'rb', mkdir=mkdir, sudo=sudo) as fp:
        return fp.read()


def read_text(path: str|os.PathLike, *, encoding: str|None = None, errors: str|None = None, newline: str|None = None, mkdir: bool = False, sudo: bool = False) -> str:
    """
    Open the file in text mode, read it, and close the file.
    """
    with open(path, 'r', encoding=encoding, errors=errors, newline=newline, mkdir=mkdir, sudo=sudo) as fp:
        return fp.read()


def write_bytes(path: str|os.PathLike, data, *, mkdir: bool = False, sudo: bool = False) -> None:
    """
    Open the file in bytes mode, write to it, and close the file.
    """
    with open(path, 'wb', mkdir=mkdir, sudo=sudo) as fp:
        fp.write(data)


def write_text(path: str|os.PathLike, data: str, *, encoding: str|None = None, errors: str|None = None, newline: str|None = None, mkdir: bool = False, sudo: bool = False) -> None:
    """
    Open the file in text mode, write to it, and close the file.
    """
    with open(path, 'w', encoding=encoding, errors=errors, newline=newline, mkdir=mkdir, sudo=sudo) as fp:
            fp.write(data)

#endregion


#region Path utilities

def isabs(path: str|os.PathLike|ZipPath) -> bool:
    if isinstance(path, ZipPath):
        return os.path.isabs(path.root.filename or '')
    else:
        return os.path.isabs(path)

def isdir(path: str|os.PathLike|ZipPath) -> bool:
    if isinstance(path, ZipPath):
        return path.is_dir()
    else:
        return os.path.isdir(path)

def dirname(path: str|os.PathLike|ZipPath) -> str:
    if isinstance(path, ZipPath):
        if not path.root.filename:
            raise ValueError("Zip path root must have a file name")
        if path.at == '' or path.at == '/':
            return os.path.dirname(path.root.filename)
        else:
            at_dir = os.path.dirname(path.at)
            if at_dir == '' or at_dir == '/':
                at_dir = '/(ziproot)'
            elif not at_dir.startswith('/'):
                at_dir = '/' + at_dir
            return path.root.filename + at_dir
    else:
        return os.path.dirname(path)

def basename(path: str|os.PathLike|ZipPath) -> str:
    if isinstance(path, ZipPath):
        at_name = os.path.basename(path.at)
        if at_name:
            return at_name
        else:
            return '(ziproot)'
    else:
        return os.path.basename(path)

def split(path: str|os.PathLike|ZipPath) -> list[str]:
    """
    A path split function that do not depend on the platform, is compatible with URLs, SMB shares and zipPath directory entries:
    - Keep leading slash(es): may be Linux root or SMB share
    - Keep trailing slash(es): may indicate a directory (necessary in `ZipPath.at` to designate a directory)
    - Keep URL separator `://`
    """
    if not isinstance(path, str):
        path = str(path)
    
    # URL protocol (or Windows Drive)
    protocol: str
    innerpath: str
    m = re.match(r'^([a-z0-9]+\:)(.+)$', path, re.IGNORECASE)
    if m:
        protocol = m[1]
        innerpath = m[2]
    else:
        protocol = ''
        innerpath = path
    
    # Prefix
    if innerpath.startswith(('//', '\\\\')):
        prefix = innerpath[0:2]
        innerpath = innerpath[2:]
    elif innerpath.startswith(('/', '\\')):
        prefix = innerpath[0:1]
        innerpath = innerpath[1:]
    else:
        prefix = ''

    # Suffix
    if innerpath.endswith(('/', '\\')):
        suffix = innerpath[-1]
        innerpath = innerpath[:-1]
    else:
        suffix = ''

    # Slit path
    parts: list[str] = []
    for part in re.sub(r'[/\\]+', '/', innerpath).split('/'):
        part = part.strip('/')
        if part != '':
            parts.append(part)

    if protocol or prefix:
        try:
            first_part = parts.pop(0)
        except IndexError:
            first_part = ''
        if prefix:
            first_part = f'{prefix}{first_part}'
        if protocol:
            first_part = f'{protocol}{first_part}'
        parts.insert(0, first_part)

    if suffix:
        try:
            last_part = parts.pop(-1)
        except IndexError:
            last_part = ''
        last_part = f'{last_part}{suffix}'
        parts.append(last_part)

    return parts

def join(base: str|os.PathLike|ZipPath|Sequence[str], *names: str|os.PathLike, sep: str|None = None, expanduser = False, mkparent = False, **kwargs) -> str:
    """
    A path join function that do not depend on the platform, is compatible with URLs, SMB shares and zipPath directory entries.
    """
    def handle_part(part):
        if not part:
            return None
        if not isinstance(part, str):
            part = str(part)
        if expanduser:
            part = os.path.expanduser(part)
        if kwargs:
            part = part.format(**kwargs)
        # Remove additional trailing separators
        if len(part) > 0 and (part[-1] == '/' or part[-1] == '\\'):
            sep = part[-1]
            part = part.rstrip('/\\') + sep
        return part

    if not isinstance(base, str):
        if isinstance(base, (os.PathLike,ZipPath)):
            base = str(base)
        else:
            parts: list[str] = []
            for part in base:
                part = handle_part(part)
                if not part:
                    continue
                parts.append(part)

            if sep is None:
                sep = '\\' if any('\\' in part for part in parts) or any('\\' in str(name) for name in names) else '/'
            base = sep.join(part for part in parts)

    if sep is None:
        sep = '\\' if '\\' in base or any('\\' in str(name) for name in names) else '/'

    path = base
    for name in names:
        name = handle_part(name)
        if not name:
            continue
        if name[0] == '/' or name[0] == '\\' or re.match(r'^([a-z0-9]+\:)(.+)$', name, re.IGNORECASE): # is rooted or contains a protocol (or drive letter)
            path = name
        else:
            path += (sep if path and not path.endswith(('/', '\\')) else '') + name

    if mkparent:
        parent = dirname(path)
        makedirs(parent, exist_ok=True)

    return path

#endregion


#region Open function

_open = open

@overload
def open(path: str|os.PathLike|ZipPath, mode: OpenTextMode = 'r', buffering: int = -1, encoding: str|None = None, errors: str|None = None, newline: str|None = None, *, mkdir: bool = False, sudo: bool = False) -> TextIOWrapper:
    ...

@overload
def open(path: str|os.PathLike|ZipPath, mode: OpenBinaryMode, buffering: Literal[0], encoding: None = None, errors: None = None, newline: None = None, *, mkdir: bool = False, sudo: bool = False) -> FileIO:
    ...

@overload
def open(path: str|os.PathLike|ZipPath, mode: OpenBinaryModeReading, buffering: Literal[-1, 1] = -1, encoding: None = None, errors: None = None, newline: None = None, *, mkdir: bool = False, sudo: bool = False) -> BufferedReader:
    ...

@overload
def open(path: str|os.PathLike|ZipPath, mode: OpenBinaryModeWriting, buffering: Literal[-1, 1] = -1, encoding: None = None, errors: None = None, newline: None = None, *, mkdir: bool = False, sudo: bool = False) -> BufferedWriter:
    ...

@overload
def open(path: str|os.PathLike|ZipPath, mode: OpenBinaryModeUpdating, buffering: Literal[-1, 1] = -1, encoding: None = None, errors: None = None, newline: None = None, *, mkdir: bool = False, sudo: bool = False) -> BufferedRandom:
    ...

def open(path: str|os.PathLike|ZipPath, mode: OpenTextMode|OpenBinaryMode = 'r', buffering: int = -1, encoding: str|None = None, errors: str|None = None, newline: str|None = None, *, mkdir: bool = False, sudo: bool = False) -> AbstractContextManager[IO]:
    if sudo:
        if not isinstance(path, str):
            path = str(path)
        if not path.startswith('sudo:'):
            path = f'sudo:{path}'
    adapter = get_adapter(path)

    if mkdir:
        dir_path = dirname(path)
        if dir_path:
            adapter.makedirs(dir_path, exist_ok=True)

    _path: str|os.PathLike = path # type: ignore (ZipPath not documented)
    return adapter.open(_path, mode, buffering, encoding, errors, newline)

#endregion


#region Copy functions

def copy(src: str|os.PathLike|ZipPath, dst: str|os.PathLike|ZipPath, follow_symlinks=True) -> str:
    """
    Copy file data and file data and file's permission mode (which on Windows is only the read-only flag).
    Other metadata like file's creation and modification times, are not preserved.

    The destination may be a directory (in this case, the file will be copied into `dst` directory using
    the base filename from `src`).

    If `follow_symlinks` is `False`, `dst` will be created as a symbolic link if `src` is a symbolic link.
    If `follow_symlinks` is `True`, `dst` will be a copy of the file `src` refers to.
    """
    src_cls = get_adapter(src)
    dst_cls = get_adapter(dst)
    use_cls = dst_cls if dst_cls != FileAdapter else src_cls
    _src: str|os.PathLike = src # type: ignore (ZipPath not documented)
    _dst: str|os.PathLike = dst # type: ignore (ZipPath not documented)
    return use_cls.copy(_src, _dst, follow_symlinks=follow_symlinks)


def copy2(src: str|os.PathLike|ZipPath, dst: str|os.PathLike|ZipPath, follow_symlinks=True) -> str:
    """
    Identical to `copy()` except that `copy2()` also attempts to preserve the file metadata.

    `copy2()` uses `copystat()` to copy the file metadata. Please see `copystat()` for more information about how and what
    metadata it copies to the `dst` file.

    If `follow_symlinks` is `False`, `dst` will be created as a symbolic link if `src` is a symbolic link.
    If `follow_symlinks` is `True`, `dst` will be a copy of the file `src` refers to.
    """
    src_cls = get_adapter(src)
    dst_cls = get_adapter(dst)
    use_cls = dst_cls if dst_cls != FileAdapter else src_cls
    _src: str|os.PathLike = src # type: ignore (ZipPath not documented)
    _dst: str|os.PathLike = dst # type: ignore (ZipPath not documented)
    return use_cls.copy2(_src, _dst, follow_symlinks=follow_symlinks)


def copyfile(src: str|os.PathLike|ZipPath, dst: str|os.PathLike|ZipPath, follow_symlinks=True) -> str:
    """
    Copy the contents (no metadata) in the most efficient way possible.

    If `follow_symlinks` is `False`, `dst` will be created as a symbolic link if `src` is a symbolic link.
    If `follow_symlinks` is `True`, `dst` will be a copy of the file `src` refers to.
    """
    src_cls = get_adapter(src)
    dst_cls = get_adapter(dst)
    use_cls = dst_cls if dst_cls != FileAdapter else src_cls
    _src: str|os.PathLike = src # type: ignore (ZipPath not documented)
    _dst: str|os.PathLike = dst # type: ignore (ZipPath not documented)
    return use_cls.copyfile(_src, _dst, follow_symlinks=follow_symlinks)


def copystat(src: str|os.PathLike|ZipPath, dst: str|os.PathLike|ZipPath, follow_symlinks=True) -> None:
    """
    Copy the read-only attribute, last access time, and last modification time from `src` to `dst`.
    The file contents, owner, and group are unaffected.

    If `follow_symlinks` is `False` and `src` and `dst` both refer to symbolic links, the attributes will be read and written
    on the symbolic links themselves (rather than the files the symbolic links refer to).
    """
    src_cls = get_adapter(src)
    dst_cls = get_adapter(dst)
    use_cls = dst_cls if dst_cls != FileAdapter else src_cls
    _src: str|os.PathLike = src # type: ignore (ZipPath not documented)
    _dst: str|os.PathLike = dst # type: ignore (ZipPath not documented)
    use_cls.copystat(_src, _dst, follow_symlinks=follow_symlinks)


def copymode(src: str|os.PathLike|ZipPath, dst: str|os.PathLike|ZipPath, follow_symlinks=True) -> None:
    """
    Copy the permission bits from `src` to `dst`.
    The file contents, owner, and group are unaffected.
    
    Due to the limitations of Windows, this function only sets/unsets `dst` FILE_ATTRIBUTE_READ_ONLY flag based on what `src` attribute is set to.

    If `follow_symlinks` is `False` and `src` and `dst` both refer to symbolic links, the attributes will be read and written
    on the symbolic links themselves (rather than the files the symbolic links refer to).
    """
    src_cls = get_adapter(src)
    dst_cls = get_adapter(dst)
    use_cls = dst_cls if dst_cls != FileAdapter else src_cls
    _src: str|os.PathLike = src # type: ignore (ZipPath not documented)
    _dst: str|os.PathLike = dst # type: ignore (ZipPath not documented)
    use_cls.copymode(_src, _dst, follow_symlinks=follow_symlinks)


def copytree(src: str|os.PathLike|ZipPath, dst: str|os.PathLike|ZipPath, symlinks: bool = False, ignore: Callable[[str, list[str]],list[str]]|None = None, ignore_dangling_symlinks: bool = False, dirs_exist_ok: bool = False) -> str:
    """
    Recursively copy a directory tree rooted at `src` to a directory named `dst` and return the destination directory.

    Permissions and times of directories are copied with `copystat()`, individual files are copied using `copy2()`.

    If `symlinks` is true, symbolic links in the source tree result in symbolic links in the destination tree;
    if it is false, the contents of the files pointed to by symbolic links are copied. If the file pointed by the symlink doesn't
    exist, an exception will be added. You can set `ignore_dangling_symlinks` to true if you want to silence this exception.
    Notice that this has no effect on platforms that don't support `os.symlink`.

    If `dirs_exist_ok` is false (the default) and `dst` already exists, an error is raised. If `dirs_exist_ok` is true, the copying
    operation will continue if it encounters existing directories, and files within the `dst` tree will be overwritten by corresponding files from the
    `src` tree.

    If `ignore` is given, it must be a callable of the form `ignore(src, names) -> ignored_names`.
    It will be called recursively and will receive as its arguments the directory being visited (`src`) and a list of its content (`names`).
    It must return a subset of the items of `names` that must be ignored in the copy process.
    """
    src_cls = get_adapter(src)
    dst_cls = get_adapter(dst)
    use_cls = dst_cls if dst_cls != FileAdapter else src_cls
    _src: str|os.PathLike = src # type: ignore (ZipPath not documented)
    _dst: str|os.PathLike = dst # type: ignore (ZipPath not documented)
    return use_cls.copytree(_src, _dst, symlinks=symlinks, ignore=ignore, ignore_dangling_symlinks=ignore_dangling_symlinks, dirs_exist_ok=dirs_exist_ok)

#endregion


#region Other public functions

def exists(path: str|os.PathLike|ZipPath):
    _path: str|os.PathLike = path # type: ignore (ZipPath not documented)
    return get_adapter(path).exists(_path)

def remove(path: str|os.PathLike|ZipPath, *, missing_ok: bool = False, tree_ok: bool = False):
    _path: str|os.PathLike = path # type: ignore (ZipPath not documented)
    return get_adapter(path).remove(_path, missing_ok=missing_ok, tree_ok=tree_ok)

def makedirs(path: str|os.PathLike|ZipPath, *, exist_ok: bool = False):
    _path: str|os.PathLike = path # type: ignore (ZipPath not documented)
    return get_adapter(path).makedirs(_path, exist_ok=exist_ok)

def stat(path: str|os.PathLike|ZipPath) -> BaseStat:
    _path: str|os.PathLike = path # type: ignore (ZipPath not documented)
    return get_adapter(path).stat(_path)

def get_modified_at(path: str|os.PathLike|ZipPath) -> datetime:
    _path: str|os.PathLike = path # type: ignore (ZipPath not documented)
    return get_adapter(path).stat(_path).modified_at

def set_modified_at(path: str|os.PathLike|ZipPath, value: datetime):
    _path: str|os.PathLike = path # type: ignore (ZipPath not documented)
    get_adapter(path).stat(_path).modified_at = value

#endregion


#region Base and File adapters

T_NormalizedPath = TypeVar('T_NormalizedPath')

class BaseOpenTempContext(Generic[T_NormalizedPath]):
    def __init__(self, path: T_NormalizedPath, mode: str = 'r', buffering: int = -1, encoding: str|None = None, errors: str|None = None, newline: str|None = None):
        """
        :param path: Must have been normalized (as a string) before instanciation of this class.
        """
        self.path = path
        self.mode = mode
        self.open_kwargs = {'mode': mode, 'buffering': buffering, 'encoding': encoding, 'errors': errors, 'newline': newline}
        self.temp_path = mktemp()
        self.temp_fp: IO|None = None

    def __enter__(self) -> IO:
        self.before_open_temp()
        self.temp_fp = open(self.temp_path, **self.open_kwargs)
        return self.temp_fp # type: ignore
    
    def __exit__(self, exc_type = None, exc = None, exc_tb = None):
        if self.temp_fp:
            self.temp_fp.close()
        self.after_close_temp()
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)

    @property
    def is_reading(self):
        return 'r' in self.mode

    @property
    def is_writing(self):
        return not self.is_reading

    def before_open_temp(self):
        pass

    def after_close_temp(self):
        pass


class BaseStat(Generic[T_NormalizedPath]):
    def __init__(self, path: T_NormalizedPath):
        self._path = path

    @property
    def size(self) -> int:
        """ Size of the file expressed in bytes. """
        raise NotImplementedBy(self.__class__)
    
    @property
    def accessed_at(self) -> datetime:
        """ Date of last access (aware if possible). """
        raise NotImplementedBy(self.__class__)
    
    @property
    def created_at(self) -> datetime:
        """ Date of creation (aware if possible). """
        raise NotImplementedBy(self.__class__)
    
    @property
    def modified_at(self) -> datetime:
        """ Date of last modification (aware if possible). """
        raise NotImplementedBy(self.__class__)
    
    @modified_at.setter
    def modified_at(self, value: datetime) -> None:
        """ Update date of last modification. """
        raise NotImplementedBy(self.__class__)


class BaseAdapter(Generic[T_NormalizedPath]):
    open_context_cls: type[BaseOpenTempContext[T_NormalizedPath]]|None = None
    stat_cls: type[BaseStat[T_NormalizedPath]]|None = None
    
    @classmethod
    def open(cls, path: str|os.PathLike, mode: str = 'r', buffering: int = -1, encoding: str|None = None, errors: str|None = None, newline: str|None = None) -> AbstractContextManager[IO]:
        if cls.open_context_cls:
            return cls.open_context_cls(cls.normalize_path(path), mode, buffering, encoding, errors, newline)
        else:
            raise NotImplementedBy(cls)

    @classmethod
    def normalize_path(cls, path: str|os.PathLike) -> T_NormalizedPath:
        if not isinstance(path, str):
            path = str(path)
        return path # type: ignore

    #region Exists, remove, makedirs

    @classmethod
    def exists(cls, path: str|os.PathLike):
        raise NotImplementedBy(cls)
    
    @classmethod
    def remove(cls, path: str|os.PathLike, *, missing_ok: bool = False, tree_ok: bool = False):
        try:
            cls._remove(path, tree_ok=tree_ok)
        except FileNotFoundError as err:
            if not missing_ok:
                raise err from None
    
    @classmethod
    def _remove(cls, path: str|os.PathLike, *, tree_ok: bool = False):
        """ Must raise FileNotFoundError if not found. """
        raise NotImplementedBy(cls)

    @classmethod
    def makedirs(cls, path: str|os.PathLike, *, exist_ok: bool = False):
        try:
            cls._makedirs(path)
        except FileExistsError as err:
            if not exist_ok:
                raise err from None
    
    @classmethod
    def _makedirs(cls, path: str|os.PathLike):
        """ Must raise FileExistsError if exists """
        raise NotImplementedBy(cls)
    
    #endregion


    #region Stat/time
    
    @classmethod
    def stat(cls, path: str|os.PathLike) -> BaseStat:
        if cls.stat_cls is None:        
            raise NotImplementedBy(cls)
        return cls.stat_cls(cls.normalize_path(path))
    
    #endregion


    #region Copy

    @classmethod
    def copy(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> str:
        """
        Copy file data and file data and file's permission mode (which on Windows is only the read-only flag).
        Other metadata like file's creation and modification times, are not preserved.

        The destination may be a directory (in this case, the file will be copied into `dst` directory using
        the base filename from `src`).

        If `follow_symlinks` is `False`, `dst` will be created as a symbolic link if `src` is a symbolic link.
        If `follow_symlinks` is `True`, `dst` will be a copy of the file `src` refers to.
        """
        if isdir(dst):
            dst = join(dst, basename(src))

        cls.copyfile(src, dst, follow_symlinks=follow_symlinks)
        cls.copymode(src, dst, follow_symlinks=follow_symlinks)

        if not isinstance(dst, str):
            dst = str(dst)
        return dst

    @classmethod
    def copy2(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> str:
        """
        Identical to `copy()` except that `copy2()` also attempts to preserve the file metadata.

        `copy2()` uses `copystat()` to copy the file metadata. Please see `copystat()` for more information about how and what
        metadata it copies to the `dst` file.

        If `follow_symlinks` is `False`, `dst` will be created as a symbolic link if `src` is a symbolic link.
        If `follow_symlinks` is `True`, `dst` will be a copy of the file `src` refers to.
        """
        if isdir(dst):
            dst = join(dst, basename(src))

        cls.copyfile(src, dst, follow_symlinks=follow_symlinks)
        cls.copystat(src, dst, follow_symlinks=follow_symlinks)
        
        if not isinstance(dst, str):
            dst = str(dst)
        return dst

    @classmethod
    def copyfile(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> str:
        """
        Copy the contents (no metadata) in the most efficient way possible.

        If `follow_symlinks` is `False`, `dst` will be created as a symbolic link if `src` is a symbolic link.
        If `follow_symlinks` is `True`, `dst` will be a copy of the file `src` refers to.
        """
        raise NotImplementedBy(cls)

    @classmethod
    def copystat(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> None:
        """
        Copy the read-only attribute, last access time, and last modification time from `src` to `dst`.
        The file contents, owner, and group are unaffected.

        If `follow_symlinks` is `False` and `src` and `dst` both refer to symbolic links, the attributes will be read and written
        on the symbolic links themselves (rather than the files the symbolic links refer to).
        """
        raise NotImplementedBy(cls)

    @classmethod
    def copymode(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> None:
        """
        Copy the permission bits from `src` to `dst`.
        The file contents, owner, and group are unaffected.
        
        Due to the limitations of Windows, this function only sets/unsets `dst` FILE_ATTRIBUTE_READ_ONLY flag based on what `src` attribute is set to.

        If `follow_symlinks` is `False` and `src` and `dst` both refer to symbolic links, the attributes will be read and written
        on the symbolic links themselves (rather than the files the symbolic links refer to).
        """
        raise NotImplementedBy(cls)

    @classmethod
    def copytree(cls, src: str|os.PathLike, dst: str|os.PathLike, symlinks: bool = False, ignore: Callable[[str, list[str]],list[str]]|None = None, ignore_dangling_symlinks: bool = False, dirs_exist_ok: bool = False) -> str:
        """
        Recursively copy a directory tree rooted at `src` to a directory named `dst` and return the destination directory.

        Permissions and times of directories are copied with `copystat()`, individual files are copied using `copy2()`.

        If `symlinks` is true, symbolic links in the source tree result in symbolic links in the destination tree;
        if it is false, the contents of the files pointed to by symbolic links are copied. If the file pointed by the symlink doesn't
        exist, an exception will be added. You can set `ignore_dangling_symlinks` to true if you want to silence this exception.
        Notice that this has no effect on platforms that don't support `os.symlink`.

        If `dirs_exist_ok` is false (the default) and `dst` already exists, an error is raised. If `dirs_exist_ok` is true, the copying
        operation will continue if it encounters existing directories, and files within the `dst` tree will be overwritten by corresponding files from the
        `src` tree.

        If `ignore` is given, it must be a callable of the form `ignore(src, names) -> ignored_names`.
        It will be called recursively and will receive as its arguments the directory being visited (`src`) and a list of its content (`names`).
        It must return a subset of the items of `names` that must be ignored in the copy process.
        """
        raise NotImplementedBy(cls)

    #endregion


class FileStat(BaseStat[str]):
    def __init__(self, path: str):
        super().__init__(path)
        raw = os.stat(self._path)
        self._size = raw.st_size
        self._atime = raw.st_atime
        self._mtime = raw.st_mtime
        self._ctime = raw.st_ctime
        self._accessed_at = None
        self._created_at = None
        self._modified_at = None

    @property
    def size(self) -> int:
        return self._size
    
    @property
    def accessed_at(self) -> datetime:
        if self._accessed_at is None:
            self._accessed_at = make_aware(datetime.fromtimestamp(self._atime), 'local')
        return self._accessed_at
    
    @property
    def created_at(self) -> datetime:
        if self._created_at is None:
            self._created_at = make_aware(datetime.fromtimestamp(self._ctime), 'local')
        return self._created_at
    
    @property
    def modified_at(self) -> datetime:
        if self._modified_at is None:
            self._modified_at = make_aware(datetime.fromtimestamp(self._mtime), 'local')
        return self._modified_at
    
    @modified_at.setter
    def modified_at(self, value: datetime):
        if value.tzinfo:
            value = make_naive(value, 'local')
        self._modified_at = value
        self._mtime = value.timestamp()
        os.utime(self._path, (self._atime, self._mtime))


class FileAdapter(BaseAdapter):
    stat_cls = FileStat

    @classmethod
    def open(cls, path: str|os.PathLike, mode: str = 'r', buffering: int = -1, encoding: str|None = None, errors: str|None = None, newline: str|None = None) -> AbstractContextManager[IO]:
        return _open(path, mode, buffering, encoding, errors, newline)

    #region Exists, remove, makedirs

    @classmethod
    def exists(cls, path: str|os.PathLike):
        return os.path.exists(path)
    
    @classmethod
    def _remove(cls, path: str|os.PathLike, *, tree_ok: bool = False):
        """ Must raise FileNotFoundError if not found. """
        try:
            os.remove(path)
            return
        except Exception as err:
            is_a_directory_error_cls = PermissionError if sys.platform == 'win32' else IsADirectoryError
            if not isinstance(err, is_a_directory_error_cls):
                raise err from None
            
            try:
                if tree_ok:
                    shutil.rmtree(path)
                else:
                    os.rmdir(path)
            except Exception as err:
                raise err from None

    @classmethod
    def _makedirs(cls, path: str|os.PathLike):
        """ Must raise FileExistsError if exists """
        os.makedirs(path)
    
    #endregion

    #region Copy

    @classmethod
    def copyfile(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> str:
        if not isinstance(dst, str):
            dst = str(dst)
        return shutil.copyfile(src, dst, follow_symlinks=follow_symlinks)

    @classmethod
    def copystat(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> None:
        return shutil.copystat(src, dst, follow_symlinks=follow_symlinks)

    @classmethod
    def copymode(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> None:
        return shutil.copymode(src, dst, follow_symlinks=follow_symlinks)

    @classmethod
    def copytree(cls, src: str|os.PathLike, dst: str|os.PathLike, symlinks: bool = False, ignore: Callable[[str, list[str]],list[str]]|None = None, ignore_dangling_symlinks: bool = False, dirs_exist_ok: bool = False) -> str:
        if not isinstance(dst, str):
            dst = str(dst)
        return shutil.copytree(src, dst, symlinks=symlinks, ignore=ignore, ignore_dangling_symlinks=ignore_dangling_symlinks, dirs_exist_ok=dirs_exist_ok)

    #endregion

#endregion


#region Determine if we should use a backend (if possible, without having to load it)

def get_adapter(path: str|os.PathLike|ZipPath) -> type[BaseAdapter]:
    global _smb_configured_from_env

    detected: Literal['sudo', 'smb', 's3', 'zipentry']|None = None
    if isinstance(path, ZipPath):
        detected = 'zipentry'
    else:
        if not isinstance(path, str):
            path = str(path)        
        
        if path.startswith('sudo:'):
            path = path[5:]
            detected = 'sudo'
        elif path.startswith('s3:'):
            path = path[3:]
            detected = 's3'
        elif path.startswith(("\\\\","//")):
            detected = 'smb'
        else:
            parts = split(path)
            if any(part.lower().endswith('.zip') for part in parts[:-1]):
                detected = 'zipentry'

        if '://' in path and not detected:
            raise ValueError(f"Don't know how to handle URL: {path}")

    # Zip entry?
    if detected == 'zipentry':
        from zut.files.zip import ZipEntryAdapter
        return ZipEntryAdapter

    # Sudo?
    if detected == 'sudo':
        if not is_sudo_available():
            raise SudoNotAvailable()
        
        from zut.files.sudo import SudoAdapter
        return SudoAdapter
    
    # Smb?
    if detected == 'smb':        
        # Configure from environment variables if any
        if not _smb_configured_from_env:
            user = os.environ.get('SMB_USER')
            if user and (is_secret_defined('SMB_PASSWORD')):
                from zut.files.smb import configure_smb
                configure_smb(None, user, Secret('SMB_PASSWORD'))
        
        if sys.platform != 'win32' or is_smb_configured(path): # type: ignore  # Python is natively compatible with Samba shares on Windows
            from zut.files.smb import SmbAdapter
            return SmbAdapter
    
    # S3?
    if detected == 's3':
        access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        if access_key_id and (is_secret_defined('AWS_SECRET_ACCESS_KEY')):
            from zut.files.s3 import configure_s3
            configure_s3(None, access_key_id, Secret('AWS_SECRET_ACCESS_KEY'))
        
        from zut.files.s3 import S3Adapter
        return S3Adapter
        
    # Base
    return FileAdapter


def _split_smb_host_port(path: str|os.PathLike, *, accept_local = False) -> tuple[str,int,str]:
    if not isinstance(path, str):
        path = str(path)

    if not path.startswith(("\\\\","//")):
        if accept_local:
            return '', 0, path
        raise ValueError(f"Not a samba path: {path}")
    path = path.replace('\\', '/')

    parts = urlparse(path)
    if not parts.hostname:
        raise ValueError(f"Server not found in samba path: {path}")
    if parts.username or parts.password:
        raise ValueError(f"Username and password should not be provided through SMB path but using configure_smb()")    
    return parts.hostname, parts.port or 445, parts.path


_smb_configured_from_env = False
_smb_configured_hostports: set[str|None] = set()

def is_smb_configured(path: str|os.PathLike):
    if None in _smb_configured_hostports:
        return True
    host, port, _ = _split_smb_host_port(path)
    return f'{host}:{port}' in _smb_configured_hostports

#endregion
