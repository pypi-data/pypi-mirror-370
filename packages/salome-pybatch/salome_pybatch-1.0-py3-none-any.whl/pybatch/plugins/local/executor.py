# Copyright (C) 2025  CEA, EDF
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#
"""Run a command with a supervisor."""

from __future__ import annotations
from typing import Optional
from types import FrameType
from pathlib import Path

import sys
import subprocess
import signal
import functools
import traceback


def handler(
    proc: subprocess.Popen[bytes], signum: int, frame: Optional[FrameType]
) -> None:
    proc.terminate()


def run() -> None:
    wall_time = int(sys.argv[1])
    if wall_time < 1:
        wall_time = None  # type: ignore
    command = sys.argv[2:]
    # daemonize process

    log_path = Path("logs")
    log_path.mkdir(parents=True, exist_ok=True)
    stdout_log = log_path / "output.log"
    stderr_log = log_path / "error.log"
    # file descriptors are automaticaly closed by default
    # (see close_fds argument of Popen).
    stdout_file = open(stdout_log, "w")
    stderr_file = open(stderr_log, "w")
    proc = subprocess.Popen(
        command,
        stdout=stdout_file,
        stderr=stderr_file,
    )
    signal.signal(signal.SIGTERM, functools.partial(handler, proc))
    try:
        exit_code = proc.wait(wall_time)
    except subprocess.TimeoutExpired:
        proc.terminate()
        exit_code = proc.wait()
    exit_log = log_path / "exit_code.log"
    with open(exit_log, "w") as exit_file:
        exit_file.write(str(exit_code))


if __name__ == "__main__":
    try:
        run()
    except Exception:
        error_log = Path("logs") / "error.log"
        error_message = traceback.format_exc()
        with open(error_log, "a") as logfile:
            logfile.write(error_message)
