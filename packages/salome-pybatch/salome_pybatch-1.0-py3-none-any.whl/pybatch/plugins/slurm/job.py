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
import time

from pybatch import GenericJob, GenericProtocol, LaunchParameters
from pybatch import PybatchException
from pybatch.protocols.local import LocalProtocol

from pybatch.tools import path_join, is_absolute, escape_str


def simplified_state(name: str) -> str:
    finished_states = ["COMPLETED"]
    running_states = ["CONFIGURI", "RUNNING"]
    queued_states = ["PENDING"]
    paused_states = ["RESV_DEL_", "REQUEUE", "RESIZING", "SUSPENDED"]
    failed_states = [
        "BOOT_FAIL",
        "CANCELLED",
        "DEADLINE",
        "FAILED",
        "NODE_FAIL",
        "OUT_OF_ME",
        "PREEMPTED",
        "REVOKED",
        "SIGNALING",
        "SPECIAL_E",
        "STAGE_OUT",
        "STOPPED",
        "TIMEOUT",
    ]
    for state in finished_states:
        if name.startswith(state):
            return "FINISHED"
    for state in running_states:
        if name.startswith(state):
            return "RUNNING"
    for state in queued_states:
        if name.startswith(state):
            return "QUEUED"
    for state in paused_states:
        if name.startswith(state):
            return "PAUSED"
    for state in failed_states:
        if name.startswith(state):
            return "FAILED"
    return ""


def reduce_states(states_list: list[str], max_number_of_states: int) -> str:
    simple_states = [simplified_state(s) for s in states_list]
    if "RUNNING" in simple_states:
        return "RUNNING"  # at least one is running
    if "QUEUED" in simple_states:
        return "QUEUED"  # at least one is queued and none is running
    if "PAUSED" in simple_states:
        return "PAUSED"
    if max_number_of_states == len(states_list):
        # if all the jobs are listed by squeue (not always the case!)
        if "FAILED" in simple_states:
            return "FAILED"
        else:
            return "FINISHED"
    return ""


class Job(GenericJob):
    def __init__(
        self, param: LaunchParameters, protocol: GenericProtocol | None
    ):
        self.job_params = param
        self.protocol: GenericProtocol
        if protocol is None:
            self.protocol = LocalProtocol()
        else:
            self.protocol = protocol
        self.jobid = ""
        self.number_of_jobs = self.job_params.total_jobs

    def submit(self) -> None:
        """Submit the job to the batch manager and return.

        If the submission fails, raise an exception.
        """
        # with self.protocol as protocol:
        try:
            # create remote workdir
            # workdir is always a linux path
            logdir = path_join(
                self.job_params.work_directory, "logs", is_posix=True
            )
            command = ["mkdir", "-p", logdir]
            self.protocol.run(command)

            batch_path = path_join(
                self.job_params.work_directory, "batch.cmd", is_posix=True
            )
            self.protocol.create(batch_path, self.batch_file())
            self.protocol.upload(
                self.job_params.input_files, self.job_params.work_directory
            )
            output = self.protocol.run(
                [
                    "sbatch",
                    "--parsable",
                    "--chdir",
                    self.job_params.work_directory,
                    batch_path,
                ]
            )
            self.jobid = output.split(";")[0].strip()
            int(self.jobid)  # check
            self.number_of_jobs = self.job_params.total_jobs
        except Exception as e:
            message = "Failed to submit job."
            raise PybatchException(message) from e

    def wait(self) -> None:
        "Wait until the end of the job."
        if not self.jobid:
            return
        state = self.state()
        while state != "FINISHED" and state != "FAILED":
            time.sleep(1)
            state = self.state()

    def state(self) -> str:
        """Possible states : 'CREATED', 'QUEUED', 'RUNNING',
        'PAUSED', 'FINISHED', 'FAILED'
        """
        if not self.jobid:
            return "CREATED"
        try:
            # with self.protocol as protocol:
            # First try to query the job with "squeue" command
            try:
                command = ["squeue", "-h", "-o", "%T", "-j", self.jobid]
                squeue_state = self.protocol.run(command)
                if squeue_state:
                    st = ""
                    if self.number_of_jobs > 1:
                        list_states = squeue_state.splitlines()
                        st = reduce_states(list_states, self.number_of_jobs)
                    else:
                        st = simplified_state(squeue_state)
                    if st:
                        return st
            except PybatchException:
                # job was finished a long time ago and it is no longer
                # available for squeue
                pass

            # If "squeue" failed, the job may be finished.
            # In this case, try to query the job with "sacct".
            command = [
                "sacct",
                "-X",  # ignore steps
                "-o",  # output fields
                "State%-10",  # state field on less than 10 chars
                "-n",  # no header
                "-j",  # jobid
                self.jobid,
            ]
            sacct_state = self.protocol.run(command)
            max_tries = 5
            while not sacct_state and max_tries:
                # if not sacct_state:
                # Give some time to slurm scheduler to update
                max_tries -= 1
                time.sleep(1)
                sacct_state = self.protocol.run(command)
            st = ""
            if self.number_of_jobs > 1:
                list_states = sacct_state.splitlines()
                st = reduce_states(list_states, self.number_of_jobs)
                if not st:
                    # No RUNNING, no PENDING and
                    # len(list_states) < number_of_jobs
                    # The main job in the array is the job which is launched the
                    # last but its state is PENDING from the start of the array
                    # until the job is actually launched. The other jobs are not
                    # listed from the start. They are listed only when they can
                    # be launched, when the jobs that are before in the array
                    # are finished.
                    # When a job is scheduled to be launched, it takes a little
                    # while before seeing it with the acct command. This is why
                    # it is possible to have all listed jobs FINISHED or FAILED,
                    # but some jobs of the array not listed yet.
                    if "CANCELLED" in sacct_state:
                        # The main job is not "PENDING" and there are less
                        # states listed than the total number of jobs in the
                        # array. At least one job has cancelled state.
                        # This happens when the job array is cancelled, but also
                        # when a particular job in the array is cancelled after
                        # the end of the main job, if the main job is shorter
                        # than other jobs.
                        # WARNING If the main job has started and an individual
                        # job in the array was cancelled, the arrays is set as
                        # FAILED despite some jobs may be still running but not
                        # yet scheduled. To be investigated.
                        st = "FAILED"
                    else:
                        # The main job finished very fast and the scheduler have
                        # not added to queue all the jobs of the last slice in
                        # the array yet.
                        st = "RUNNING"
            else:
                st = simplified_state(sacct_state)
        except Exception as e:
            raise PybatchException("Failed to get the state of the job.") from e
        if st:
            return st
        else:
            raise PybatchException(
                f"Unknown state. squeue_state: {squeue_state}, sacct_state:{sacct_state}"
            )

    def exit_code(self) -> int | None:
        if not self.jobid:
            return None
        state = self.state()
        if state == "FINISHED":
            return 0
        if state != "FAILED":
            return None
        try:
            command = [
                "sacct",
                # "-X",  # ignore steps
                "-o",  # output fields
                "ExitCode%-10",
                "-n",  # no header
                "-j",  # jobid
                self.jobid,
            ]
            # code_str format: <exit_code>:<signal_received>
            # If ok, code_str is "0:0"
            # If cancel, code_str is "0:15"
            # If exit 1, code_str is "1:0"

            code_str = self.protocol.run(command)
            result = None
            if code_str:
                # The result is the first non 0 value found, job steps included.
                result = 0
                for val in code_str.splitlines():
                    signal_received = int(val.split(":")[1])
                    if signal_received != 0:
                        cur_val = signal_received
                    else:
                        cur_val = int(val.split(":")[0])
                    if cur_val != 0:
                        result = cur_val
                        break
        except Exception:
            result = None
        return result

    def cancel(self) -> None:
        "Stop the job."
        if not self.jobid:
            return
        command = ["scancel", self.jobid]
        try:
            self.protocol.run(command)
        except Exception as e:
            raise PybatchException("Failed to cancel the job.") from e

    def get(self, remote_paths: list[str], local_path: str | Path) -> None:
        """Copy a file or directory from the remote work directory.

        :param remote_paths: paths relative to work directory on remote host.
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
        "Get the content of the batch file submited to the batch manager."
        batch = """#!/bin/bash -l
#SBATCH --output=logs/output.log
#SBATCH --error=logs/error.log
"""
        if self.job_params.name:
            batch += f"#SBATCH --job-name={self.job_params.name}\n"
        if self.job_params.total_jobs > 1:
            simul = ""
            if self.job_params.max_simul_jobs > 1:
                simul = f"%{self.job_params.max_simul_jobs}"
            array = f"0-{self.job_params.total_jobs - 1}{simul}"
            batch += f"#SBATCH --array={array}\n"
        if self.job_params.ntasks > 0:
            batch += f"#SBATCH --ntasks={self.job_params.ntasks}\n"
        if self.job_params.nodes > 0:
            batch += f"#SBATCH --nodes={self.job_params.nodes}\n"
        if self.job_params.exclusive:
            batch += "#SBATCH --exclusive\n"
        if self.job_params.wall_time:
            batch += f"#SBATCH --time={self.job_params.wall_time}\n"
        if self.job_params.mem_per_node:
            batch += f"#SBATCH --mem={self.job_params.mem_per_node}\n"
        if self.job_params.mem_per_cpu:
            batch += f"#SBATCH --mem-per-cpu={self.job_params.mem_per_cpu}\n"
        if self.job_params.queue:
            batch += f"#SBATCH --qos={self.job_params.queue}\n"
        if self.job_params.partition:
            batch += f"#SBATCH --partition={self.job_params.partition}\n"
        if self.job_params.wckey:
            batch += f"#SBATCH --wckey={self.job_params.wckey}\n"
        for extra in self.job_params.extra_as_list:
            batch += f"#SBATCH {extra}\n"
        if self.job_params.extra_as_string:
            batch += self.job_params.extra_as_string
        if self.job_params.create_nodefile:
            batch += """
LIBBATCH_NODEFILE=`pwd`/batch_nodefile.txt
srun hostname > $LIBBATCH_NODEFILE
export LIBBATCH_NODEFILE
"""
        # batch += "echo Jobid: $SLURM_JOB_ID\n"
        # if self.job_params.total_jobs > 1:
        #     batch += "echo master Jobid: $SLURM_ARRAY_JOB_ID\n"
        command = self.job_params.command
        str_command = command[0]
        for arg in command[1:]:
            str_command += " " + escape_str(arg)
        if self.job_params.total_jobs > 1:
            str_command += " $SLURM_ARRAY_TASK_ID"
        batch += "\n"
        batch += str_command
        return batch

    # A réfléchir, mais il vaut peut-être mieux utiliser la sérialisation
    # pickle.
    # def dump(self) -> str:
    # " Serialization of the job."
    # ...
