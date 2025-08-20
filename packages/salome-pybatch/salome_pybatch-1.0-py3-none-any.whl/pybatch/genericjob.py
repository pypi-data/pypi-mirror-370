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


class GenericJob(typing.Protocol):
    "Job protocol to be implemented."

    def submit(self) -> None:
        """Submit the job to the batch manager and return.

        If the submission fails, raise an exception.
        """
        ...

    def wait(self) -> None:
        "Wait until the end of the job."
        ...

    def state(self) -> str:
        """Possible states : 'CREATED', 'IN_PROCESS', 'QUEUED', 'RUNNING',
        'PAUSED', 'FINISHED', 'FAILED'
        """
        ...

    def exit_code(self) -> int | None:
        """Get the exit code of the command if any.
        If the code is not found, for instance when the job is neither FINISHED
        nor FAILED, return None.
        """
        ...

    def cancel(self) -> None:
        "Stop the job."
        ...

    def get(self, remote_path: list[str], local_path: str) -> None:
        """Copy files from the remote work directory.

        :param remote_paths: paths relative to work directory on remote host.
        :param local_path: destination of the copy on local file system.
        """
        ...

    def batch_file(self) -> str:
        """Get the content of the batch file submitted to the batch manager.

        This function is not relevant if the job is not submitted to a batch
        manager that uses a submission file.
        """
        ...

    def stdout(self) -> str:
        "Standard output of the job."
        ...

    def stderr(self) -> str:
        "Standard error of the job."
        ...

    def dump(self) -> str:
        """Serialization of the job in a humanly readable format.

        This feature is not implemented yet because it is possible to use pickle
        for automatic serialization.
        """
        ...
