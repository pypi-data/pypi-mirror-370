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
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LaunchParameters:
    """Parameters of a job to be launched.

    List of parameters :

      * command - full command to run with arguments as a list.
      * work_directory - remote work directory, with path separator at the end.
      * host - remote host where the job will be launched.
      * user - user name if needed.
      * name - name of the job.
      * total_jobs - total number of jobs using a job array. The job index is
        passed as the last argument to the command.
      * max_simul_jobs - maximum number of simultaneous jobs using a job array.
      * nodes - number of required nodes, 0 for undefined.
      * ntasks - number of required tasks, 0 for undefined.
      * exclusive - activate exclusive mode.
      * wall_time - maximum time of the job.
        Acceptable time formats include "minutes", "minutes:seconds",
        "hours:minutes:seconds", "days-hours", "days-hours:minutes" and
        "days-hours:minutes:seconds".
      * mem_per_node - memory required per node (ex. "32G").
      * mem_per_cpu - minimum memory required per usable allocated CPU.
      * queue - required queue.
      * partition - required partition.
      * wckey
      * extra_as_string - extra parameters as a string
        (ex. "#SBATCH --cpus-per-task=4").
      * extra_as_list - extra parameters as a list (ex. ["--cpus-per-task=4"]).
        job.
      * input_files - list of local files to be copied to remote work_directory.
      * is_posix - Unix like server (True) or Windows server (False).
      * python_exe - path to the python executable. Default to "python3".
      * create_nodefile - create LIBBATCH_NODEFILE which contains the list of
        allocated nodes.
    """

    command: list[str]
    work_directory: str
    name: str = ""
    total_jobs: int = 1
    max_simul_jobs: int = 1
    nodes: int = 0
    ntasks: int = 0
    exclusive: bool = False
    wall_time: str = ""
    mem_per_node: str = ""
    mem_per_cpu: str = ""
    queue: str = ""
    partition: str = ""
    wckey: str = ""
    extra_as_string: str = ""
    extra_as_list: list[str] = field(default_factory=list)
    input_files: list[str | Path] = field(default_factory=list)
    is_posix: bool = True
    python_exe: str = "python3"
    create_nodefile: bool = False


@dataclass
class ConnectionParameters:
    """Parameters needed to connect to a remote server.

    List of parameters :

    * host
    * user
    * password
    * gss_auth - use the gss api for authentication. It has to be True when
      using Kerberos protocole.
    """

    host: str = ""
    user: str | None = None
    password: str | None = None
    gss_auth: bool = False
