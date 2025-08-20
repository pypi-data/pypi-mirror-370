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
from __future__ import annotations
import pathlib
import subprocess
import typing
from . import PybatchException
from .generic_protocol import GenericProtocol


def path_join(base: str, *paths: str, is_posix: bool) -> str:
    result: pathlib.PurePath
    if is_posix:
        result = pathlib.PurePosixPath(base)
    else:
        result = pathlib.PureWindowsPath(base)
    for path in paths:
        result = result / path
    return str(result)


def is_absolute(path: str, is_posix: bool) -> bool:
    if is_posix:
        return pathlib.PurePosixPath(path).is_absolute()
    else:
        return pathlib.PureWindowsPath(path).is_absolute()


def slurm_time_to_seconds(val: str) -> str:
    """Convert a slurm time format string to seconds.

    See https://slurm.schedmd.com/sbatch.html#OPT_time
    Acceptable time formats:
       "minutes", "minutes:seconds", "hours:minutes:seconds",
       "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"
    """
    val = val.strip()
    if not val:
        return val
    try:
        day_split = val.split("-")
        if len(day_split) == 2:
            days = int(day_split[0])
            rem = day_split[1]
        elif len(day_split) == 1:
            days = 0
            rem = day_split[0]
        else:
            raise PybatchException(f"Invalid time format: {val}.")
        hour_split = rem.split(":")
        if len(hour_split) == 3:
            hours = int(hour_split[0])
            minutes = int(hour_split[1])
            seconds = int(hour_split[2])
        elif len(hour_split) == 2:
            if days > 0:  # days-hours:minutes
                hours = int(hour_split[0])
                minutes = int(hour_split[1])
                seconds = 0
            else:  # minutes:seconds
                hours = 0
                minutes = int(hour_split[0])
                seconds = int(hour_split[1])
        elif len(hour_split) == 1:
            if days > 0:  # days-hours
                hours = int(hour_split[0])
                minutes = 0
                seconds = 0
            else:  # minutes
                hours = 0
                minutes = int(hour_split[0])
                seconds = 0
        else:
            raise PybatchException(f"Invalid time format: {val}.")
    except Exception as e:
        raise PybatchException(f"Invalid time format: {val}.") from e
    result = seconds + 60 * minutes + 3600 * hours + 24 * 3600 * days
    return str(result)


def run_check(
    command: list[str], **extra: typing.Any
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(command, capture_output=True, text=True, **extra)
    ret_code = proc.returncode
    if ret_code != 0:
        message = f"""Error {ret_code}.
  command: {command}.
  stderr: {proc.stderr}
"""
        raise PybatchException(message)
    return proc


def escape_str(val: str) -> str:
    """Escape characters with special meaning in bash.
    a'b -> 'a'\''b'
    a b -> 'a b'
    """
    special_chars = " ()[]{}*?$#'\\"
    special_found = False
    for c in special_chars:
        if c in val:
            special_found = True
            break
    if special_found:
        result = "'" + val.replace("'", "'\\''") + "'"
    else:
        result = val
    return result


def remote_mkdir(protocol: GenericProtocol, dir: str, python_exe: str) -> None:
    """Create a directory on a remote server.

    The directory is created by running a python command.
    :param protocol: Connection protocol to the remote server.
    :param dir: Path of the remote directory to be created.
    :param python_exe: Path to the python executable on the remote server.
    """
    py_script = f"from pathlib import Path; Path({repr(dir)}).mkdir(parents=True, exist_ok=True)"
    command = [python_exe, "-c", py_script]
    protocol.run(command)
