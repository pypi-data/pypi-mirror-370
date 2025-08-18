"""
Implementation of `zut.files` for entries of ZIP archives.
"""
from __future__ import annotations

import logging
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime
from stat import S_ISDIR
from time import localtime
from typing import TYPE_CHECKING, Sequence

from zut import DelayedStr, NotImplementedBy, NotSupportedBy
from zut.files import BaseAdapter, BaseStat, basename, get_adapter, join, split

if TYPE_CHECKING:
    from typing import Literal

if sys.version_info < (3, 10):
    # See: https://bugs.python.org/issue40564
    from zipp import Path as ZipPath
else:
    from zipfile import Path as ZipPath

_logger = logging.getLogger(__name__)
    

def unzip(path: str|os.PathLike|ZipPath, target: str|os.PathLike, *, existing: Literal['ignore','update','replace','warn'] = 'warn', omit_single_dir: bool|str|re.Pattern = False, password: DelayedStr|str|bytes|None = None, mkdir = False, insecure = False):
    """
    Unzip an archive file in a target directory.

    :param existing: If 'ignore', entries that already exist in the target are ignored. If 'update', they are replaced only if the archive entry are newer. If 'replace', they are always replaced. If 'warn' (the default), a warning is issued and the file is ignored.
    :param omit_single_dir: If there is a single dir and it matches the given pattern (if any), the directory is omitted when extracting to the target.
    """
    target_adapter = get_adapter(target)
    if not target_adapter.exists(target):
        if mkdir:
            target_adapter.makedirs(target, exist_ok=True)
        else:
            raise FileNotFoundError(f"Target directory not found: {target}")
    password = get_zip_password_bytes(password)

    def unzip_file(entry: ZipPath, target: str):
        entry_modified_at = None

        # Check if we should extract
        if existing != 'replace':
            if os.path.exists(target):
                if existing == 'update':
                    entry_modified_at = get_zipentry_modified_at(entry)
                    target_modified_at = target_adapter.stat(target).modified_at
                    if target_modified_at >= entry_modified_at:
                        _logger.debug("Ignore extraction from %s:%s to newer existing file: %s", entry.root.filename, entry.at, target)
                        return
                else:
                    _logger.log(logging.DEBUG if existing == 'ignore' else logging.WARNING, "Ignore extraction from %s:%s to existing file: %s", entry.root.filename, entry.at, target)
                    return
        
        # Do extract
        _logger.debug("Extract file from %s:%s to %s", entry.root.filename, entry.at, target)
        with entry.root.open(entry.at, pwd=password) as src_fp, open(target, "wb") as dst_fp:
            shutil.copyfileobj(src_fp, dst_fp)

        if not entry_modified_at:
            entry_modified_at = get_zipentry_modified_at(entry)
        target_adapter.stat(target).modified_at = entry_modified_at

    def unzip_dir(entry: ZipPath, target: str):
        if (entry.at != '' and entry.at != '/') and not entry.exists():
            raise FileNotFoundError("No directory %s in archive %s" % (entry.at, entry.root.filename))

        entry_modified_at_if_mkdir = None
        if not target_adapter.exists(target):
            entry_modified_at_if_mkdir = get_zipentry_modified_at(entry)
            target_adapter.makedirs(target)
        
        _logger.debug("Extract directory from %s:%s to %s", entry.root.filename, entry.at, target)
        for sub_entry in entry.iterdir():
            if '..' in sub_entry.name or '/' in sub_entry.name or '\\' in sub_entry.name:
                if not insecure:
                    raise ValueError(f'Insecure zip entry name "{sub_entry.name}" (at {entry})')
            sub_target = join(target, sub_entry.name)

            if sub_entry.is_dir():
                unzip_dir(sub_entry, sub_target)
            else:
                unzip_file(sub_entry, sub_target)
        
        if entry_modified_at_if_mkdir:
            target_adapter.stat(target).modified_at = entry_modified_at_if_mkdir

    with ZipContext(path, dir=True) as path:
        dir_to_omit = None
        if omit_single_dir:
            dirs = [entry for entry in path.iterdir() if entry.is_dir()]
            if len(dirs) == 1:
                if isinstance(omit_single_dir, (str,re.Pattern)):
                    if re.match(omit_single_dir, dirs[0].name):
                        dir_to_omit = dirs[0]
                else:
                    dir_to_omit = dirs[0]

        if not isinstance(target, str):
            target = str(target)
        if dir_to_omit:
            unzip_dir(dir_to_omit, target)
        else:
            unzip_dir(path, target)
        

def get_zipentry_modified_at(path: zipfile.ZipInfo|ZipPath|zipfile.ZipFile, at: str|None = None) -> datetime:
    """
    Return the (naive) modified_at of an entry in the zip archive:
    - naive: inside zip files, dates and times are stored in local time in 16 bits, not UTC (Coordinated Universal Time/Temps Universel Coordonné) as is conventional, using an ancient MS DOS format.
    - inprecise: there was not room in 16 bit to accurately represent time even to the second, so the seconds field contains the seconds divided by two, giving accuracy only to the even second.
    """
    if isinstance(path, zipfile.ZipInfo):
        info = path
        if at is not None:
            raise ValueError("'at' must be null when a ZipInfo is given as 'path'")
    else:
        if isinstance(path, ZipPath):
            root = path.root
            at = at if at is not None else path.at
        else:
            root = path
            if at is None:
                raise ValueError("'at' cannot be null when a ZipFile is given as 'path'")
            
        try:
            info = root.getinfo(at)
        except KeyError as err:
            if not at.endswith('/'):
                info = None
            else:
                raise err from None
            
        if info is None:
            try:
                info = root.getinfo(at + '/')
            except KeyError as err:
                raise err from None

    y, m, d, hour, min, sec = info.date_time
    return datetime(y, m, d, hour, min, sec)


def get_zip_password_bytes(password: DelayedStr|str|bytes|None, *, encoding = 'utf-8') -> bytes|None:
    if not isinstance(password, str) and isinstance(password, Sequence):
        return password
    else:
        password = DelayedStr.ensure_value(password)
        return password.encode(encoding) if password is not None else None


def get_zipentry_or_standard_path(path: str|os.PathLike|ZipPath, *, dir: bool|None = None, mode: Literal['r','a','w']|None = None, compression: int|None = None, no_implicit_root_entry = False) -> ZipPath|str:
    """
    :param compression: `zipfile.ZIP_DEFLATED` for example.
    """
    if isinstance(path, ZipPath):        
        recreate = False
        if (mode is not None and path.root.mode != mode) or (compression is not None and path.root.compression != compression):
            recreate = True
        elif dir is not None:
            if dir:
                if path.at != '' and not path.at.endswith('/'):
                    recreate = True
            else:
                if path.at.endswith('/'):
                    recreate = True

        if recreate:
            root_path_str: str = path.root.filename # type: ignore
            root = zipfile.ZipFile(root_path_str, mode=mode or 'r', compression=compression if compression is not None else zipfile.ZIP_DEFLATED)
            at = path.at
            if dir is not None:
                if dir:
                    if not at.endswith('/'):
                        at += '/'
                else:
                    if at.endswith('/'):
                        at = at.rstrip('/')
            return ZipPath(root, at)
        else:
            return path
    
    if not isinstance(path, str):
        if dir is None:
            if not isinstance(path, str):
                path = str(path)
            if path.endswith('/'):
                dir = True
        path = str(path)

    parts = split(path)
    root_parts = []
    at = None
    for i, part in enumerate(parts):
        root_parts.append(part)
        if part.lower().endswith('.zip'):
            at_parts = parts[i+1:]
            if len(at_parts) >= 1 and at_parts[0] == '(ziproot)':
                at_parts = at_parts[1:]
                at = '/'.join(at_parts) if at_parts else ''
            elif at_parts:
                at = '/'.join(at_parts)
            elif no_implicit_root_entry:
                at = None # -> will be converted to str if this is the zip file without an inner entry
            else:
                at = ''
            break

    root_path = join(*root_parts, sep = '\\' if '\\' in path else None)
    if at is None:
        return root_path
        
    if dir and at and not at.endswith('/'):
        at += '/'
    
    root = zipfile.ZipFile(root_path, mode=mode or 'r', compression=compression if compression is not None else zipfile.ZIP_DEFLATED)
    return ZipPath(root, at=at)


def get_zipentry_path(path: str|os.PathLike|ZipPath, *, dir: bool|None = None, mode: Literal['r','a','w']|None = None, compression: int|None = None, no_implicit_root_entry = False) -> ZipPath:
    path = get_zipentry_or_standard_path(path, dir=dir, mode=mode, compression=compression, no_implicit_root_entry=no_implicit_root_entry)

    if isinstance(path, str):
        raise ValueError(f"Not a zip entry: {path}")
    else:
        return path
    

def get_std_path(path: str|os.PathLike|ZipPath) -> str:
    if isinstance(path, ZipPath):
        return str(path)
    elif isinstance(path, str):
        return path
    else:
        return str(path)


class ZipContext:
    def __init__(self, path: str|os.PathLike|ZipPath, *, dir: bool|None = None, mode: Literal['r','a','w'] = 'r', compression = zipfile.ZIP_DEFLATED):
        self.path = get_zipentry_path(path, dir=dir, mode=mode, compression=compression)

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type= None, exc= None, exc_tb = None):
        self.path.root.close()


def write_zip_entry(src: str|os.PathLike, path: ZipPath, *, modified_at_now = False):
    """ Must be used with an open ZipFile. """
    if isinstance(src, os.PathLike):
        src = os.fspath(src)
    st = os.stat(src)
    isdir = S_ISDIR(st.st_mode)
    if modified_at_now:
        modified_at_struct = localtime()
    else:
        modified_at_struct = localtime(st.st_mtime)
    modified_at_tuple = modified_at_struct[0:6]
    strict_timestamps = getattr(path.root, '_strict_timestamps', True)
    if not strict_timestamps and modified_at_tuple[0] < 1980:
        modified_at_tuple = (1980, 1, 1, 0, 0, 0)
    elif not strict_timestamps and modified_at_tuple[0] > 2107:
        modified_at_tuple = (2107, 12, 31, 23, 59, 59)
    # Create ZipInfo instance to store file information
    arcname = path.at
    if isdir and not arcname.endswith('/'):
        arcname += '/'
    zinfo = zipfile.ZipInfo(arcname, modified_at_tuple)
    zinfo.external_attr = (st.st_mode & 0xFFFF) << 16  # Unix attributes
    if isdir:
        zinfo.file_size = 0
        zinfo.external_attr |= 0x10  # MS-DOS directory flag
    else:
        zinfo.file_size = st.st_size

    if zinfo.is_dir():
        zinfo.compress_size = 0
        zinfo.CRC = 0
        path.root.mkdir(zinfo)
    else:
        zinfo.compress_type = path.root.compression
        zinfo._compresslevel = path.root.compresslevel # type: ignore

        with open(src, "rb") as src_fp, path.root.open(zinfo, 'w') as dst_fp:
            shutil.copyfileobj(src_fp, dst_fp, 1024*8)

    return zinfo


class ZipEntryStat(BaseStat[ZipPath]):
    def __init__(self, path):
        super().__init__(path)
        raw = self._path.root.getinfo(self._path.at)
        self._size = raw.file_size
        self._compressed_size = raw.compress_size
        self._modified_at = get_zipentry_modified_at(raw)

    @property
    def size(self) -> int:
        return self._size

    @property
    def compressed_size(self) -> int:
        return self._compressed_size
    
    @property
    def accessed_at(self) -> datetime:
        raise NotSupportedBy(self.__class__.__name__)
    
    @property
    def created_at(self) -> datetime:
        raise NotSupportedBy(self.__class__.__name__)
    
    @property
    def modified_at(self) -> datetime:
        return self._modified_at
    
    @modified_at.setter
    def modified_at(self, value: datetime):
        raise NotSupportedBy("zip entry", "change field 'modified_at' of a zip entry")


class ZipEntryAdapter(BaseAdapter[ZipPath]):
    stat_cls = ZipEntryStat

    @classmethod
    def normalize_path(cls, path):
        return get_zipentry_path(path)

    @classmethod
    def exists(cls, path: str|os.PathLike|ZipPath) -> bool:
        try:
            path = get_zipentry_path(path)
        except FileNotFoundError as err:
            return False
        
        if path.at == '' or path.at == '/':
            return True # The root necessarily exists
        
        if not path.exists():       
            # Try the directory if not already tried
            if path.at.endswith('/'):
                return False
            return get_zipentry_path(path, dir=True).exists()
        
        return True
    
    #region Copy

    @classmethod
    def copy2(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True):
        # Override it for writting to an archive, because we cannot use copystat in this case (Cannot change field 'modified_at' of a zip entry)
        src_path = get_zipentry_or_standard_path(src)
        dst_path = get_zipentry_or_standard_path(dst)
        if not isinstance(src_path, ZipPath) and isinstance(dst_path, ZipPath):
            if not dst_path.exists() and not dst_path.at.endswith('/'):
                dir = ZipPath(dst_path.root, dst_path.at+'/')
                if dir.exists():
                    dst_path = dir.joinpath(basename(src_path))

            with ZipContext(dst_path, mode='a') as dst_path:
                write_zip_entry(src_path, dst_path, modified_at_now=False)

            return get_std_path(dst_path)
        else:
            return super().copy2(src, dst, follow_symlinks=follow_symlinks)

    @classmethod
    def copyfile(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True):
        src_path = get_zipentry_or_standard_path(src)
        dst_path = get_zipentry_or_standard_path(dst)
        if isinstance(src_path, ZipPath):
            if isinstance(dst_path, ZipPath):
                raise NotImplementedBy(cls, f"zip src to zip dst") #ROADMAP
            
            if os.path.isdir(dst_path):
                dst_path = join(dst_path, src_path.name)

            with src_path.root.open(src_path.at) as src_fp, open(dst_path, "wb") as dst_fp:
                shutil.copyfileobj(src_fp, dst_fp)
                
            #ROADMAP: should we instead extract to a tempdir and handle the case of an already existing destination file? Example:
            # with TemporaryDirectory() as tmpdir:
            #     result = src.root.extract(src.at, tmpdir)
            #     if os.path.exists(dst):
            #         os.remove(dst)
            #     os.rename(result, dst)

            return dst_path
        elif isinstance(dst_path, ZipPath):
            if not dst_path.exists() and not dst_path.at.endswith('/'):
                dir = ZipPath(dst_path.root, dst_path.at+'/')
                if dir.exists():
                    dst_path = dir.joinpath(basename(src_path))

            with ZipContext(dst_path, mode='a') as dst_path:
                write_zip_entry(src_path, dst_path, modified_at_now=True)

            return get_std_path(dst_path)
        else:
            raise ValueError("No zip entry")

    @classmethod
    def copystat(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True):
        src_path = get_zipentry_or_standard_path(src)
        dst_path = get_zipentry_or_standard_path(dst)
        if isinstance(src_path, ZipPath):
            if isinstance(dst_path, ZipPath):
                raise NotImplementedBy(cls, f"zip src to zip dst") #ROADMAP
            
            if os.path.isdir(dst_path):
                dst_path = join(dst_path, src_path.name)

            modified_at = get_zipentry_modified_at(src_path)
            get_adapter(dst_path).stat(dst_path).modified_at = modified_at
        elif isinstance(dst_path, ZipPath):
            raise ValueError("Cannot change field 'modified_at' of a zip entry")
        else:
            raise ValueError("No zip entry")

    @classmethod
    def copymode(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True):
        return

    #endregion
