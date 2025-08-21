"""
Utilities to help manage and launch processes
"""

from pathlib import Path
import subprocess
from subprocess import Popen
import os
import logging
import shlex
import select
import threading
import weakref
from typing import Callable, Any
from io import TextIOWrapper

from pydantic import BaseModel

from iccore.runtime import ctx

logger = logging.getLogger(__name__)


class Process(BaseModel, frozen=True):

    local_rank: int = 0
    pid: int = 0
    username: str


def _open_io_handles(stdout_path: Path | None = None, stderr_path: Path | None = None):
    if stdout_path:
        stdout_f: TextIOWrapper | None = open(stdout_path, "w", encoding="utf-8")
    else:
        stdout_f = None

    if stderr_path:
        stderr_f: TextIOWrapper | None = open(stderr_path, "w", encoding="utf-8")
    else:
        stderr_f = None
    return stdout_f, stderr_f


def _close_io_handles(stdout_f, stderr_f):
    if stderr_f:
        stderr_f.close()
    if stdout_f:
        stdout_f.close()


def run(
    cmd: str,
    cwd: Path = Path(os.getcwd()),
    is_read_only: bool = False,
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
    check: bool = True,
) -> str:
    """
    This method is intended to be a drop-in for subprocess.run with
    a couple of modifications:

    1) It supports a 'dry run' including a hint on whether
    the command will be 'read only'
    2) It doesn't allow running via a shell, but does convert
    string-like args to a list as needed by execv
    3) It defaults to checking the return code and capturing
    standard out as text
    """

    can_run = ctx.can_modify() or (is_read_only and ctx.can_read())
    if not can_run:
        ctx.add_cmd(f"run {cmd}")
        return ""

    stdout_f, stderr_f = _open_io_handles(stdout_path, stderr_path)
    capture_output = not stdout_f
    text = not stdout_f

    shell_cmd = shlex.split(cmd)
    try:
        result = subprocess.run(
            shell_cmd,
            check=check,
            capture_output=capture_output,
            text=text,
            cwd=cwd,
            stderr=stderr_f,
            stdout=stdout_f,
        )
    except subprocess.CalledProcessError as e:
        msg = f"Error code: {e.returncode} | sterr: {e.stderr}"
        logger.error(msg)
        raise e

    _close_io_handles(stdout_f, stderr_f)

    return result.stdout


def run_async(
    cmd: str,
    cwd: Path = Path(os.getcwd()),
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
    pass_fd: int = -1,
):

    stdout_f, stderr_f = _open_io_handles(stdout_path, stderr_path)
    shell_cmd = shlex.split(cmd)

    pass_fds: tuple = ()
    if pass_fd != -1:
        pass_fds = (pass_fd,)

    proc = Popen(
        shell_cmd,
        env=os.environ.copy(),
        cwd=cwd,
        stdout=stdout_f,
        stderr=stderr_f,
        pass_fds=pass_fds,
    )
    _close_io_handles(stdout_f, stderr_f)
    return proc


def _close_and_join(fd, thread):
    os.close(fd)
    thread.join()


def _run_poll(
    quitfd: int, poll, callbacks: dict[int, Callable | None], procs: dict[int, Any]
):
    poll.register(quitfd, select.POLLHUP)
    while True:
        for fd, _ in poll.poll(1000.0):
            poll.unregister(fd)
            if fd == quitfd:
                return
            callback = callbacks.pop(fd)
            proc = procs.pop(fd)
            # The fd has been signalled - but the Popen may not have what it needs
            # to give a return node. Wait until it does.
            retcode = proc.wait()
            if callback is not None:
                callback(proc.pid, retcode)


class ProcessLauncher:
    """
    This class allows processes to be launched through the normal subprocess
    mechanism but fires a callback when the process is finished.

    It does this by have a dedicated thread polling for a pipe file descriptor
    hangup which happens when the launched process closes.
    """

    def __init__(self) -> None:
        self.poll = select.poll()
        self.callbacks: dict[int, Callable | None] = {}
        self.procs: dict[int, Any] = {}
        self.closed: bool = False

        r, w = os.pipe()
        self.thread = threading.Thread(
            target=_run_poll, args=(r, self.poll, self.callbacks, self.procs)
        )
        self.thread.start()
        self.finalizer = weakref.finalize(self, _close_and_join, w, self.thread)

    def run(
        self,
        cmd: str,
        cwd: Path = Path(os.getcwd()),
        stdout_path: Path | None = None,
        stderr_path: Path | None = None,
        callback: Callable | None = None,
    ):
        if self.closed:
            return None

        r, w = os.pipe()
        self.callbacks[r] = callback
        self.poll.register(r, select.POLLHUP)

        proc = run_async(cmd, cwd, stdout_path, stderr_path, w)
        self.procs[r] = proc
        os.close(w)
        return proc
