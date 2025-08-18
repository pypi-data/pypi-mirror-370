"""
Common wrappers over `subprocess.run`.
"""
from __future__ import annotations

import logging
import os
import subprocess
from queue import Queue
from signal import Signals
from threading import Thread
from typing import (IO, TYPE_CHECKING, Any, Callable, Mapping, Sequence,
                    overload)

from zut import Color, SudoNotAvailable, get_logger, is_sudo_available

if TYPE_CHECKING:
    from typing import Literal

@overload
def run_process(cmd: str|os.PathLike|bytes|Sequence[str|os.PathLike|bytes], *,
                encoding: Literal['bytes'],
                # (no difference with base function)
                sudo = False,
                check: int|Sequence[int]|bool = False,
                capture_output: bool|None = None,
                stdout: Literal['disable','raise','warning','error']|Callable[[bytes],Any]|None = None,
                stderr: Literal['disable','raise','warning','error']|Callable[[bytes],Any]|None = None,
                strip: Literal['rstrip-newline','strip',True]|None = None,
                strip_stderr: Literal['rstrip-newline','strip',True]|None = None,
                input: str|None = None,
                shell = False,
                env: Mapping[str,Any]|None = None,
                logger: logging.Logger|None = None) -> subprocess.CompletedProcess[bytes]:
    ...

@overload
def run_process(cmd: str|os.PathLike|bytes|Sequence[str|os.PathLike|bytes], *,
                encoding: Literal['utf-8', 'cp1252', 'unknown']|None = None,
                # (no difference with base function)
                sudo = False,
                check: int|Sequence[int]|bool = False,
                capture_output: bool|None = None,
                stdout: Literal['disable','raise','warning','error']|Callable[[str],Any]|None = None,
                stderr: Literal['disable','raise','warning','error']|Callable[[str],Any]|None = None,
                strip: Literal['rstrip-newline','strip',True]|None = None,
                strip_stderr: Literal['rstrip-newline','strip',True]|None = None,
                input: str|None = None,
                shell = False,
                env: Mapping[str,Any]|None = None,
                logger: logging.Logger|None = None) -> subprocess.CompletedProcess[str]:
    ...

def run_process(cmd: str|os.PathLike|bytes|Sequence[str|os.PathLike|bytes], *,
                sudo = False,
                check: int|Sequence[int]|bool = False,
                capture_output: bool|None = None,
                stdout: Literal['disable','raise','warning','error']|Callable[[str],Any]|Callable[[bytes],Any]|None = None,
                stderr: Literal['disable','raise','warning','error']|Callable[[str],Any]|Callable[[bytes],Any]|None = None,
                strip: Literal['rstrip-newline','strip',True]|None = None,
                strip_stderr: Literal['rstrip-newline','strip',True]|None = None,
                input: str|None = None,
                encoding: str|Literal['unknown','bytes']|None = None,
                shell = False,
                env: Mapping[str,Any]|None = None,
                logger: logging.Logger|None = None) -> subprocess.CompletedProcess:

    # If stdout or stderr is a callable, use `subprocess.Popen`
    if (stdout and callable(stdout)) or (stderr and callable(stderr)):
        return run_process_callback(cmd, sudo=sudo, check=check, capture_output=capture_output, stdout=stdout, stderr=stderr, strip=strip, strip_stderr=strip_stderr, input=input, encoding=encoding, shell=shell, env=env, logger=logger)
    
    if sudo:
        if not is_sudo_available():
            raise SudoNotAvailable()
        if isinstance(cmd, (str,os.PathLike)):
            cmd = f'sudo {cmd}'
        elif isinstance(cmd, bytes) or any(isinstance(arg, bytes) for arg in cmd):
            raise ValueError(f"Cannot use sudo with a bytes command")
        else:
            cmd = ['sudo', *cmd] # type: ignore
    
    # If neither stdout nor stderr is a callable, use `subprocess.run`
    if capture_output is None:
        if (stdout and stdout != 'disable') or (stderr and stderr != 'disable'):
            capture_output = True
        else:
            capture_output = False

    cp = subprocess.run(cmd,
                        capture_output=capture_output,
                        text=encoding not in {'unknown', 'bytes'},
                        stdout=subprocess.DEVNULL if stdout == 'disable' else None,
                        stderr=subprocess.DEVNULL if stderr == 'disable' else None,
                        input=input,
                        encoding=encoding if encoding not in {'unknown', 'bytes'} else None,
                        shell=shell,
                        env=env)
    
    return verify_run_process(cp, check=check, stdout=stdout, stderr=stderr, strip=strip, strip_stderr=strip_stderr, unknown_encoding=encoding == 'unknown', logger=logger)


def verify_run_process(cp: subprocess.CompletedProcess, *,
                       check: int|Sequence[int]|bool = False,
                       stdout: Literal['disable','raise','warning','error']|None = None,
                       stderr: Literal['disable','raise','warning','error']|None = None,
                       strip: Literal['rstrip-newline','strip',True]|None = None,
                       strip_stderr: Literal['rstrip-newline','strip',True]|None = None,
                       unknown_encoding = False,
                       logger: logging.Logger|None = None) -> subprocess.CompletedProcess:
    
    if strip_stderr is None:
        strip_stderr = strip
    
    cp.stdout = parse_output(cp.stdout, strip=strip, unknown_encoding=unknown_encoding)
    cp.stderr = parse_output(cp.stderr, strip=strip_stderr, unknown_encoding=unknown_encoding)
    
    invalid_returncode = False
    if check:
        if check is True:
            check = 0
        invalid_returncode = not (cp.returncode in check if not isinstance(check, int) else cp.returncode == check)

    invalid_stdout = stdout == 'raise' and cp.stdout
    invalid_stderr = stderr == 'raise' and cp.stderr

    if cp.stdout:
        level = None
        if stdout == 'warning':
            level = logging.WARNING
        elif stdout == 'error':
            level = logging.ERROR
        if level:
            (logger or get_logger(__name__)).log(level, f"{Color.PURPLE}[stdout]{Color.RESET} %s", stdout)
            
    if cp.stderr:
        level = None
        if stderr == 'warning':
            level = logging.WARNING
        elif stderr == 'error':
            level = logging.ERROR
        if level:
            (logger or get_logger(__name__)).log(level, f"{Color.PURPLE}[stderr]{Color.RESET} %s", stderr)

    if invalid_returncode or invalid_stdout or invalid_stderr:
        raise RunProcessError(cp.returncode, cp.args, cp.stdout, cp.stderr)    
    return cp


def run_process_callback(cmd: str|os.PathLike|bytes|Sequence[str|os.PathLike|bytes], *,
                         sudo = False,
                         check: int|Sequence[int]|bool = False,
                         capture_output: bool|None = None,
                         stdout: Literal['disable','raise','warning','error']|Callable[[str],Any]|Callable[[bytes],Any]|None = None,
                         stderr: Literal['disable','raise','warning','error']|Callable[[str],Any]|Callable[[bytes],Any]|None = None,
                         strip: Literal['rstrip-newline','strip',True]|None = None,
                         strip_stderr: Literal['rstrip-newline','strip',True]|None = None,
                         input: str|None = None,
                         encoding: str|Literal['unknown','bytes']|None = None,
                         shell = False,
                         env: Mapping[str,Any]|None = None,
                         logger: logging.Logger|None = None) -> subprocess.CompletedProcess:
    """
    Run a process, transfering live output to callbacks.
    """
    # See: https://stackoverflow.com/a/60777270
    queue = Queue()

    def enqueue_stream(stream: IO, source: str):
        for data in iter(stream.readline, ''):
            queue.put((source, data))
        stream.close()

    def enqueue_process(proc: subprocess.Popen):
        if input is not None:
            returncode = proc.communicate(input)
        else:
            returncode = proc.wait()
        queue.put(('process', returncode))
    
    captured: dict[str, str|bytes] = {}

    def capture_callback(output, stream_name: str):
        if stream_name in captured:
            content = captured[stream_name]
            content = content + output
            captured[stream_name] = content
        else:
            captured[stream_name] = output

    verify_stdout = None
    if stdout == 'disable' or (not stdout and not capture_output):
        stdout = None
    elif stdout and not callable(stdout):
        verify_stdout = stdout
        stdout = lambda output: capture_callback(output, 'stdout')

    verify_stderr = None
    if stderr == 'disable' or (not stderr and not capture_output):
        stderr = None
    elif stderr and not callable(stderr):
        verify_stderr = stderr
        stderr = lambda output: capture_callback(output, 'stderr')

    if sudo:
        if not is_sudo_available():
            raise SudoNotAvailable()
        if isinstance(cmd, (str,os.PathLike)):
            cmd = f'sudo {cmd}'
        elif isinstance(cmd, bytes) or any(isinstance(arg, bytes) for arg in cmd):
            raise ValueError(f"Cannot use sudo with a bytes command")
        else:
            cmd = ['sudo', *cmd] # type: ignore

    proc = subprocess.Popen(cmd,
                        text=encoding not in {'unknown', 'bytes'},
                        encoding=encoding if encoding not in {'unknown', 'bytes'} else None,
                        shell=shell,
                        env=env,
                        stdout=subprocess.PIPE if stdout is not None else subprocess.DEVNULL,
                        stderr=subprocess.PIPE if stderr is not None else subprocess.DEVNULL,
                        stdin=subprocess.PIPE if input is not None else None)
    
    if stdout:
        Thread(target=enqueue_stream, args=[proc.stdout, 'stdout'], daemon=True).start()
    if stderr:
        Thread(target=enqueue_stream, args=[proc.stderr, 'stderr'], daemon=True).start()
    Thread(target=enqueue_process, args=[proc], daemon=True).start()

    if strip_stderr is None:
        strip_stderr = strip
        
    while True:
        source, data = queue.get()
        if source == 'stdout':
            if callable(stdout):
                parsed_data = parse_output(data, strip=strip, unknown_encoding=True)
                stdout(parsed_data) # type: ignore
        elif source == 'stderr':
            if callable(stderr):
                parsed_data = parse_output(data, strip=strip_stderr, unknown_encoding=True)
                stderr(parsed_data) # type: ignore
        else: # process
            cp = subprocess.CompletedProcess(cmd, returncode=data, stdout=captured.get('stdout'), stderr=captured.get('stderr'))    
            return verify_run_process(cp, check=check, stdout=verify_stdout, stderr=verify_stderr, logger=logger)


def parse_output(output: str|bytes, *, strip: Literal['rstrip-newline','strip',True]|None = None, unknown_encoding = False) -> str|bytes:
    if unknown_encoding and isinstance(output, bytes):
        try:
            output = output.decode('utf-8')
        except UnicodeDecodeError:
            output = output.decode('cp1252')

    if strip:
        if isinstance(output, str):
            if strip == 'rstrip-newline':
                return output.rstrip('\r\n')
            elif strip == 'rstrip':
                return output.rstrip()
            else:
                return output.strip()
        else:
            raise TypeError(f"Cannot strip output of type {type(output).__name__}")
    else:
        return output


class RunProcessError(subprocess.CalledProcessError):
    def __init__(self, returncode, cmd, stdout, stderr):
        super().__init__(returncode, cmd, stdout, stderr)
        self.maxlen: int|None = 200
        self._message = None

    def with_maxlen(self, maxlen: int|None):
        self.maxlen = maxlen
        return self

    @property
    def message(self):
        if self._message is None:
            self._message = ''

            if self.returncode and self.returncode < 0:
                try:
                    self._message += "died with %r" % Signals(-self.returncode)
                except ValueError:
                    self._message += "died with unknown signal %d" % -self.returncode
            else:
                self._message += "returned exit code %d" % self.returncode

            if self.output:
                info = self.output[0:self.maxlen] + '…' if self.maxlen is not None and len(self.output) > self.maxlen else self.stdout
                self._message += ('\n' if self._message else '') + f"[stdout] {info}"

            if self.stderr:
                info = self.stderr[0:self.maxlen] + '…' if self.maxlen is not None and len(self.stderr) > self.maxlen else self.stderr
                self._message += ('\n' if self._message else '') + f"[stderr] {info}"

            self._message = f"Command '{self.cmd}' {self._message}"

        return self._message

    def __str__(self):
        return self.message
