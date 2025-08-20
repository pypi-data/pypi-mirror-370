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
import typing
from collections.abc import Iterable
from pathlib import Path
import shutil
import os

from .. import PybatchException
from ..tools import run_check


def copy(src: str | Path, dest: str | Path) -> None:
    """Recursively copy files and directories."""
    if os.path.isfile(src):
        shutil.copy(src, dest)
    elif os.path.isdir(src):
        src_basename = os.path.basename(src)
        dest_dir = Path(dest) / src_basename
        shutil.copytree(src, dest_dir, dirs_exist_ok=True)
    else:
        raise PybatchException(
            f"Copy error. Path {src} is neither a file, nor a directory."
        )


class LocalProtocol:
    "Protocol for localhost."

    def __init__(self, params: typing.Any = None):
        pass

    def upload(
        self, local_entries: Iterable[str | Path], remote_path: str
    ) -> None:
        for entry in local_entries:
            copy(entry, remote_path)

    def download(
        self, remote_entries: Iterable[str], local_path: str | Path
    ) -> None:
        for entry in remote_entries:
            copy(entry, local_path)

    def create(self, remote_path: str, content: str) -> None:
        Path(remote_path).write_text(content)

    def read(self, remote_path: str) -> str:
        return Path(remote_path).read_text()

    def run(self, command: list[str]) -> str:
        proc = run_check(command)
        return proc.stdout


def open() -> LocalProtocol:
    return LocalProtocol()
