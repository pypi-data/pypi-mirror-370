"""
GPG and `pass` utilities.

Includes management of passwords using `pass`, the standard unix password manager (see: https://www.passwordstore.org/).

See also other implementations:
- keyring-pass (v0.9.3, 2024-03-08): https://github.com/nazarewk/keyring_pass
- keyrings.unixpass (v0.0.2, 2022-08-08): https://gitlab.com/chrooti/keyrings.unixpass
- keyrings.passwordstore (v0.1.0, 2021-01-04): https://github.com/stv0g/keyrings.passwordstore
"""
from __future__ import annotations

import logging
import os
import random
import re
from argparse import ArgumentParser
from contextlib import contextmanager
from datetime import datetime
from getpass import getpass
from pathlib import Path
import string
import sys
from tempfile import TemporaryDirectory, mkstemp
from time import time
from typing import TYPE_CHECKING
from uuid import uuid4

from zut import DelayedStr, __version__
from zut.commands import create_command_parser, exec_command
from zut.process import run_process

if TYPE_CHECKING:
    from typing import Literal

_logger = logging.getLogger(__name__)

_pass_dir = Path.home().joinpath('.password-store')
_gpg_id: str|None = '__unset__'


def get_pass_list():
    passes: list[str] = []

    def recurse(dir: Path):
        for path in dir.iterdir():
            if path.is_dir():
                recurse(path)
            elif path.suffix == '.gpg' and not path.name.startswith('.'):
                path = path.relative_to(_pass_dir)
                passes.append(path.with_suffix('').as_posix())

    recurse(_pass_dir)
    passes.sort()
    return passes


def get_pass(name: str, default: str|type[Exception]|None = None):
    path = get_pass_path(name)
    if not path.exists():
        if isinstance(default, type):
            raise default(f"Pass not found: {name}")
        else:
            _logger.debug("Pass not found: %s at %s", name, path)
            return default

    _logger.debug("Decrypt pass %s at %s", name, path)
    log_gpg_decrypt_info(name)
    return run_process(['gpg', '--batch', '--no-tty', '--decrypt', path], check=True, capture_output=True, strip='rstrip-newline').stdout


@contextmanager
def open_pass(file: str|os.PathLike, password_name: str, buffering: int = -1, encoding: str|None = None, newline: str|None = None, **kwargs):
    """
    Open a file encrypted using `pass` with the given password name.
    """
    password = get_pass(password_name, FileNotFoundError)
    with open_gpg_encrypted(file, password=password, buffering=buffering, encoding=encoding, newline=newline, **kwargs) as fp:
        yield fp


def insert_pass(name: str, password: DelayedStr|str):
    path = get_pass_path(name)
    gpg_id = get_pass_gpg_id()
    if not gpg_id:
        raise ValueError(f"Pass GPG id not registered")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_in_fd = None
    tmp_in = None
    tmp_out = path.with_name(f'{path.name}.tmp')
    try:
        tmp_in_fd, tmp_in = mkstemp()
        with open(tmp_in, 'w', encoding='utf-8') as fp:
            password = DelayedStr.ensure_value_notnull(password)
            fp.write(password)
        os.close(tmp_in_fd)
        tmp_in_fd = None
        
        _logger.debug("Encrypt pass %s at %s", name, path)
        run_process(['gpg', '--batch', '--no-tty', '--output', tmp_out, '--encrypt', '--recipient', gpg_id, tmp_in], check=True)
        if path.exists():
            archive_path = path.with_name(f".{path.stem}-{datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y%m%d-%H%M%S')}.gpg")
            oc = 2
            while archive_path.exists():
                archive_path = archive_path.with_name(f"{archive_path.stem}-{oc}.gpg")
                oc += 1
            path.rename(archive_path)
        tmp_out.rename(path)
    finally:
        if tmp_in_fd:
            os.close(tmp_in_fd)
        if tmp_in and os.path.exists(tmp_in):
           os.unlink(tmp_in)
        if tmp_out.exists():
            tmp_out.unlink()


def remove_pass(name: str):
    """
    Remove a password.
    """
    path = get_pass_path(name)
    if not path.exists():
        _logger.error(f"Pass does not exist: {name}")
        return False
    path.unlink()
    return True


def get_pass_gpg_id():
    global _gpg_id
    if _gpg_id == '__unset__':
        path = _pass_dir.joinpath('.gpg-id')
        if path.exists():
            _gpg_id = path.read_text('utf-8').strip()
        else:
            _gpg_id = None        
    return _gpg_id


def get_pass_path(name: str):
    if not name:
        raise ValueError(f"Name cannot be empty")
    name = re.sub(r'\\', '', name)
    parts = name.split('/')
    path = _pass_dir.joinpath(*parts)
    return path.with_name(f'{path.name}.gpg')


def gpg_encrypt(file: str|os.PathLike, *, recipient: str|None = None, output: str|os.PathLike|None = None, delete_existing_encrypted = False, delete_original_clear = False):
    if not recipient:
        recipient = get_pass_gpg_id()
        if not recipient:
            raise ValueError("No GPG recipient configured")

    if not output:
        output = f"{file}.gpg"

    if delete_existing_encrypted:
        if os.path.exists(output):
            os.unlink(output)

    _logger.debug("Encrypt file %s", file)
    run_process(['gpg', '--batch', '--no-tty', '--output', output, '--encrypt', '--recipient', recipient, file], check=True)

    if delete_original_clear:
        os.unlink(file)


@contextmanager
def open_gpg_encrypted(file: str|os.PathLike, password: DelayedStr|str|None = None, buffering: int = -1, encoding: str|None = None, newline: str|None = None, **kwargs):
    """
    Open a GPG encrypted file.
    """
    tmpdir = TemporaryDirectory()
    fp = None
    try:
        tmp = os.path.join(tmpdir.name, str(uuid4()))

        _logger.debug("Decrypt %s to %s%s", file, tmp, ' using a password' if password is not None else '')
        args = ['gpg', '--batch', '--no-tty', '--output', tmp, '--decrypt', file]
        if password is not None:
            args += ['--passphrase-fd', '0']
            if isinstance(password, DelayedStr):
                password = password.value
        log_gpg_decrypt_info()
        run_process(args, check=True, input=password)
        
        fp = open(tmp, 'r', buffering=buffering, encoding=encoding, newline=newline, **kwargs)
        yield fp

    finally:
        if fp:
            fp.close()
        tmpdir.cleanup()


_last_decrypt_info: float = 0.0

def log_gpg_decrypt_info(pass_name: str|None = None):
    r"""
    Log an information message about decryption using the given key. The message is displayed only once per period (default 1 min).

    Used to inform user that a pinentry window might be loaded, because this may be take a very long time (especially on Windows) and give the impression that the program is locked.
    
    NOTE: The very long time it might take on Windows is generally caused by Windows Defender.
    Consider adding exclusions to Windows Defender for processes `C:\Program Files (x86)\GnuPG\bin` and `C:\Program Files (x86)\Gpg4win\bin`.
    """
    global _last_decrypt_info
    
    now = time()
    if _last_decrypt_info < now - 60:
        if pass_name:
            _logger.info(f"Decrypt pass entry %s using GPG …", pass_name)
        else:
            _logger.info(f"Decrypt using GPG …")
    _last_decrypt_info = now


#region Command

def main():
    from zut.config import configure_logging

    parser = create_command_parser('pass', version=f"zut:{__version__}", doc="Manage passwords using `pass`, the standard unix password manager (see: https://www.passwordstore.org/).")
    parser.add_argument('-i', '--info', action='store_true', help="Display an informational message before first decryption of a password.")

    add_arguments(parser)

    args = vars(parser.parse_args())

    info = args.pop('info')
    configure_logging('INFO' if info else 'WARNING')

    exec_command(args, default='ls')

def add_arguments(parser: ArgumentParser):
    from zut.commands import add_command
    
    subparsers = parser.add_subparsers(title='subcommands')
    add_command(subparsers, _handle_ls)
    add_command(subparsers, _handle_show)
    add_command(subparsers, _handle_insert)
    add_command(subparsers, _handle_rm)
    add_command(subparsers, _handle_generate)

def handle():
    """
    Manage passwords using `pass`, the standard unix password manager (see: https://www.passwordstore.org/).
    """
    return _handle_ls()

setattr(handle, 'name', 'pass')

# ----- ls -----

def _handle_ls():
    """
    List password names.
    """
    gpg_id = get_pass_gpg_id()
    _logger.debug("GPG id: %s", gpg_id)
    for p in get_pass_list():
        print(p)

setattr(_handle_ls, 'name', 'ls')

# ----- show -----

def _add_arguments(parser: ArgumentParser): # type: ignore
    parser.add_argument('name')

def _handle_show(name: str):
    """
    Show a password value.
    """
    try:
        password = get_pass(name, default=FileNotFoundError)
        print(password)
        return 0
    except FileNotFoundError as err:
        _logger.error(err)
        return 2

setattr(_handle_show, 'name', 'show')
setattr(_handle_show, 'add_arguments', _add_arguments)

# ----- insert -----

def _add_arguments(parser: ArgumentParser): # type: ignore
    parser.add_argument('name')
    parser.add_argument('password', nargs='?')

def _handle_insert(name: str, password: DelayedStr|str|None = None):
    """
    Insert a new password.
    """
    if password is None:
        password = getpass("Password: ")
        confirm_password = None
        while confirm_password != password:
            if confirm_password is not None:
                _logger.error("Invalid password confirmation. Try again.")
            confirm_password = getpass("Confirm password: ")
    
    insert_pass(name, password)

setattr(_handle_insert, 'name', 'insert')
setattr(_handle_insert, 'add_arguments', _add_arguments)

# ----- rm -----

def _add_arguments(parser: ArgumentParser): # type: ignore
    parser.add_argument('name')

def _handle_rm(name: str):
    """
    Remove a password.
    """
    remove_pass(name)

setattr(_handle_rm, 'name', 'rm')
setattr(_handle_rm, 'add_arguments', _add_arguments)

# ----- generate -----

def _add_arguments(parser: ArgumentParser): # type: ignore
    parser.add_argument('-l', '--length', type=int, default=16)

def _handle_generate(length: int = 16):
    """
    Generate and display an alphanumeric password.
    """
    generated = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))
    print(generated)

setattr(_handle_generate, 'name', 'generate')
setattr(_handle_generate, 'add_arguments', _add_arguments)

#endregion


if __name__ == '__main__':
    main()
