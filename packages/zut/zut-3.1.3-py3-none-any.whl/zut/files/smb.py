"""
Implementation of `zut.files` for Windows/Samba shares.
"""
from __future__ import annotations

import errno
import os
import re
from typing import Callable

import smbclient
import smbclient.path
import smbclient.shutil
from smbprotocol.exceptions import SMBOSError

from zut import DelayedStr
from zut.files import (BaseAdapter, _smb_configured_hostports,
                       _split_smb_host_port, join)


def configure_smb(hostport: str|None, user: str, password: DelayedStr|str):
    if hostport is not None:
        if hostport.startswith('//'):
            hostport = hostport[2:]
        if hostport.startswith('\\\\'):
            hostport = hostport[2:]

        m = re.match(r'^(.*):(\d+)$', hostport)
        if m:
            server = m[1]
            port = int(m[2])
        else:
            server = hostport
            port = 445

        if server:
            hostport = f'{server}:{port}'
            _smb_configured_hostports.add(hostport)
            smbclient.register_session(server=server, port=port, username=user, password=DelayedStr.ensure_value(password))
            return
    
    # hostport is None
    smbclient.ClientConfig(username=user, password=DelayedStr.ensure_value(password))
    _smb_configured_hostports.add(None)


class SmbAdapter(BaseAdapter):
    @classmethod
    def _split_path(cls, path: str|os.PathLike, *, accept_local = False) -> tuple[str, int]:
        host, port, path = _split_smb_host_port(path, accept_local=accept_local)
        if host:
            return f'//{host}{path}', port
        else: # local/non smb path
            return path, port
    
    @classmethod
    def _join_path(cls, path: str|os.PathLike, port: int) -> str:
        if not port:
            return path if isinstance(path, str) else str(path)
        
        host, _, path = _split_smb_host_port(path, accept_local=True)
        if not host:
            return str(path)
        return join(f'//{host}:{port}', path)

    @classmethod
    def open(cls, path: str|os.PathLike, mode: str = 'r', buffering: int = -1, encoding: str|None = None, errors: str|None = None, newline: str|None = None):
        noport_path, port = cls._split_path(path)
        return smbclient.open_file(noport_path, mode, buffering, encoding=encoding, errors=errors, newline=newline, port=port) # type: ignore

    @classmethod
    def exists(cls, path: str|os.PathLike):
        noport_path, port = cls._split_path(path)
        return smbclient.path.exists(noport_path, port=port)

    @classmethod
    def _makedirs(cls, path: str|os.PathLike):
        noport_path, port = cls._split_path(path)
        try:
            return smbclient.makedirs(noport_path, port=port)
        except SMBOSError as err:
            if err.errno == errno.EEXIST:
                raise FileExistsError(str(err)) from None
            else:
                raise

    @classmethod
    def _remove(cls, path: str|os.PathLike, *, tree_ok = False):
        noport_path, port = cls._split_path(path)
        try:
            smbclient.remove(noport_path, port=port)
            return
        except SMBOSError as err:
            if err.errno == errno.ENOENT:
                raise FileNotFoundError(str(err)) from None
            elif err.errno == errno.EISDIR:
                try:
                    if tree_ok:
                        smbclient.shutil.rmtree(noport_path, port=port)
                    else:
                        smbclient.rmdir(noport_path, port=port)
                except Exception as err:
                    raise err from None
            else:
                raise

    #region Copy

    @classmethod
    def copyfile(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> str:
        noport_src, port_src = cls._split_path(src, accept_local=True)
        noport_dst, port_dst = cls._split_path(dst, accept_local=True)
        port = port_src or port_dst
        dst = smbclient.shutil.copyfile(noport_src, noport_dst, follow_symlinks=follow_symlinks, port=port)
        return cls._join_path(dst, port)

    @classmethod
    def copystat(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> None:
        noport_src, port_src = cls._split_path(src, accept_local=True)
        noport_dst, port_dst = cls._split_path(dst, accept_local=True)
        port = port_src or port_dst
        smbclient.shutil.copystat(noport_src, noport_dst, follow_symlinks=follow_symlinks, port=port)

    @classmethod
    def copymode(cls, src: str|os.PathLike, dst: str|os.PathLike, follow_symlinks=True) -> None:
        noport_src, port_src = cls._split_path(src, accept_local=True)
        noport_dst, port_dst = cls._split_path(dst, accept_local=True)
        port = port_src or port_dst
        smbclient.shutil.copymode(noport_src, noport_dst, follow_symlinks=follow_symlinks, port=port)

    @classmethod
    def copytree(cls, src: str|os.PathLike, dst: str|os.PathLike, symlinks: bool = False, ignore: Callable[[str, list[str]],list[str]]|None = None, ignore_dangling_symlinks: bool = False, dirs_exist_ok: bool = False) -> str:
        noport_src, port_src = cls._split_path(src, accept_local=True)
        noport_dst, port_dst = cls._split_path(dst, accept_local=True)
        port = port_src or port_dst
        dst = smbclient.shutil.copytree(noport_src, noport_dst, symlinks=symlinks, ignore=ignore, ignore_dangling_symlinks=ignore_dangling_symlinks, dirs_exist_ok=dirs_exist_ok, port=port)
        return cls._join_path(dst, port)

    #endregion
