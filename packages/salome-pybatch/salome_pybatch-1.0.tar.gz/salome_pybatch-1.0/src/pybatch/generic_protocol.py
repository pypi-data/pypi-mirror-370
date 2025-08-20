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


class GenericProtocol(typing.Protocol):
    """Connection protocol (ssh, local, ...).

    This interface defines the services expected from a connection protocol.
    """

    def upload(
        self, local_entries: Iterable[str | Path], remote_path: str
    ) -> None:
        "Upload files and directories to the server."
        ...

    def download(
        self, remote_entries: Iterable[str], local_path: str | Path
    ) -> None:
        "Download files and directories from the server."
        ...

    def create(self, remote_path: str, content: str) -> None:
        "Create a file on the server."
        ...

    def read(self, remote_path: str) -> str:
        "Get the content of a file."
        ...

    def run(self, command: list[str]) -> str:
        "Run a command on the server."
        ...
