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
from pathlib import Path
import os

from ... import GenericJob, GenericProtocol, LaunchParameters, PybatchException
from ...protocols.local import LocalProtocol
from ...tools import path_join, is_absolute, slurm_time_to_seconds, remote_mkdir


class Job(GenericJob):
    def __init__(self, param: LaunchParameters, protocol: GenericProtocol):
        self.job_params = param
        self.protocol: GenericProtocol
        if protocol is None:
            self.protocol = LocalProtocol()
        else:
            self.protocol = protocol
        self.jobid = ""
        self.remote_manager_path = path_join(
            param.work_directory, "pybatch_manager.py", is_posix=param.is_posix
        )

    def submit(self) -> None:
        try:
            logdir = path_join(
                self.job_params.work_directory,
                "logs",
                is_posix=self.job_params.is_posix,
            )
            remote_mkdir(self.protocol, logdir, self.job_params.python_exe)

            file_dir = Path(os.path.dirname(__file__))
            manager_script = file_dir / "pybatch_manager.py"
            input_files = self.job_params.input_files + [manager_script]
            self.protocol.upload(input_files, self.job_params.work_directory)
            command = [
                self.job_params.python_exe,
                self.remote_manager_path,
                "submit",
                self.job_params.work_directory,
            ]
            if self.job_params.wall_time:
                seconds = slurm_time_to_seconds(self.job_params.wall_time)
                command += ["--wall_time", seconds]
            if self.job_params.create_nodefile:
                if self.job_params.ntasks > 0:
                    command += ["--ntasks", str(self.job_params.ntasks)]
            if self.job_params.total_jobs > 1:
                command += ["--total_jobs", str(self.job_params.total_jobs)]
                if self.job_params.max_simul_jobs > 1:
                    command += [
                        "--max_simul_jobs",
                        str(self.job_params.max_simul_jobs),
                    ]
            command += self.job_params.command
            self.jobid = self.protocol.run(command).strip()
            int(self.jobid)  # check
        except Exception as e:
            message = "Failed to submit job."
            raise PybatchException(message) from e

    def wait(self) -> None:
        "Wait until the end of the job."
        if not self.jobid:
            return
        try:
            command = [
                self.job_params.python_exe,
                self.remote_manager_path,
                "wait",
                self.jobid,
            ]
            self.protocol.run(command)
        except Exception as e:
            message = "Failed to wait job."
            raise PybatchException(message) from e

    def state(self) -> str:
        if not self.jobid:
            return "CREATED"
        try:
            command = [
                self.job_params.python_exe,
                self.remote_manager_path,
                "state",
                self.jobid,
                self.job_params.work_directory,
            ]
            result: str = self.protocol.run(command).strip()

        except Exception as e:
            message = "Failed to wait job."
            raise PybatchException(message) from e
        return result

    def exit_code(self) -> int | None:
        exit_code_path = path_join(
            self.job_params.work_directory,
            "logs",
            "exit_code.log",
            is_posix=self.job_params.is_posix,
        )
        try:
            result = int(self.protocol.read(exit_code_path).strip())
        except Exception:
            result = None
        return result

    def cancel(self) -> None:
        if not self.jobid:
            return
        try:
            command = [
                self.job_params.python_exe,
                self.remote_manager_path,
                "cancel",
                self.jobid,
            ]
            self.protocol.run(command)
        except Exception as e:
            message = "Failed to cancel job."
            raise PybatchException(message) from e

    def get(self, remote_paths: list[str], local_path: str | Path) -> None:
        """Copy a file or directory from the remote work directory.

        :param remote_path: path relative to work directory on the remote host.
        :param local_path: destination of the copy on local file system.
        """
        checked_paths = []
        for path in remote_paths:
            if is_absolute(path, self.job_params.is_posix):
                checked_paths.append(path)
            else:
                p = path_join(
                    self.job_params.work_directory,
                    path,
                    is_posix=self.job_params.is_posix,
                )
                checked_paths.append(p)
        self.protocol.download(checked_paths, local_path)

    def stdout(self) -> str:
        output_file = path_join(
            self.job_params.work_directory,
            "logs",
            "output.log",
            is_posix=self.job_params.is_posix,
        )
        return self.protocol.read(str(output_file))

    def stderr(self) -> str:
        output_file = path_join(
            self.job_params.work_directory,
            "logs",
            "error.log",
            is_posix=self.job_params.is_posix,
        )
        return self.protocol.read(str(output_file))

    def batch_file(self) -> str:
        return ""
