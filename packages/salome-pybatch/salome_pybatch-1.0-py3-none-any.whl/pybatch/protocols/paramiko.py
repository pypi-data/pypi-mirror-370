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
from collections.abc import Iterable
from pathlib import Path
import paramiko
import scp  # type: ignore
from typing import Any
from ..parameter import ConnectionParameters
from .. import PybatchException
from ..tools import escape_str


class ParamikoProtocol:
    """Communication protocol based on python modules paramiko and scp.

    The ssh connection is opened when the object is created and it is closed
    when the object is garbage collected.
    """

    def __init__(self, params: ConnectionParameters):
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client = client
        self.params = params
        self._open()

    def __del__(self) -> None:
        self.client.close()

    def _open(self) -> None:
        try:
            self.client.connect(
                self.params.host,
                username=self.params.user,
                password=self.params.password,
                gss_auth=self.params.gss_auth,
            )
        except Exception as e:
            message = f"Failed to open ssh connection to {self.params.host}."
            raise PybatchException(message) from e

    def upload(
        self, local_entries: Iterable[str | Path], remote_path: str
    ) -> None:
        with scp.SCPClient(self.client.get_transport()) as client:
            for entry in local_entries:
                client.put(entry, remote_path, recursive=True)

    def download(
        self, remote_entries: Iterable[str], local_path: str | Path
    ) -> None:
        with scp.SCPClient(self.client.get_transport()) as client:
            for entry in remote_entries:
                client.get(entry, local_path, recursive=True)

    def create(self, remote_path: str, content: str) -> None:
        with self.client.open_sftp() as sftp:
            with sftp.open(remote_path, "w") as remote_file:
                remote_file.write(content)

    def read(self, remote_path: str) -> str:
        with self.client.open_sftp() as sftp:
            with sftp.open(remote_path, "r") as remote_file:
                return remote_file.read().decode()

    def run(self, command: list[str]) -> str:
        # in case of issues with big stdout|stderr see
        # https://github.com/paramiko/paramiko/issues/563
        if len(command) == 0:
            raise PybatchException("Empty command.")
        str_command = command[0]
        for arg in command[1:]:
            str_command += " " + escape_str(arg)
        stdin, stdout, stderr = self.client.exec_command(str_command)
        stdin.close()
        str_std = stdout.read().decode()
        str_err = stderr.read().decode()
        stdout.close()
        stderr.close()
        ret_code = stdout.channel.recv_exit_status()
        if ret_code != 0:
            message = f"""Error {ret_code}.
  command: {str_command}
  server: {self.params.host}
  stderr: {str_err}
"""
            raise PybatchException(message)
        return str_std

    def __getstate__(self) -> dict[str, Any]:
        # deal with paramiko.client which is not suppported by pickle
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state["client"]
        return state

    def __setstate__(self, state: Any) -> None:
        self.__dict__.update(state)
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client = client
        self._open()


def open(params: ConnectionParameters) -> ParamikoProtocol:
    return ParamikoProtocol(params)
