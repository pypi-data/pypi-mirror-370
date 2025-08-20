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
import typing

import pybatch
import pybatch.protocols.local

import tempfile
from pathlib import Path
import shutil
import os
import sys

import tests.job_cases


def local_case_config(
    plugin: str, config: dict[str, typing.Any], case_name: str, script_name: str
) -> tuple[pybatch.LaunchParameters, pybatch.GenericProtocol, str]:
    if "work_dir" in config:
        work_dir = os.path.join(config["work_dir"], case_name + "_" + plugin)
    else:
        work_dir = tempfile.mkdtemp(suffix="_pybatchtest")
    params = pybatch.LaunchParameters([], work_dir, python_exe=sys.executable)
    if "wckey" in config:
        params.wckey = config["wckey"]
    params.ntasks = 1

    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / script_name
    params.input_files = [script]
    protocol = pybatch.protocols.local.LocalProtocol()
    return params, protocol, work_dir


def test_hello(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "hello", "hello.py"
    )
    tests.job_cases.test_hello(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_sleep(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "sleep", "sleep.py"
    )
    tests.job_cases.test_sleep(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_cancel(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "cancel", "sleep.py"
    )
    tests.job_cases.test_cancel(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_error(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "error", "error.py"
    )
    tests.job_cases.test_error(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_nodefile(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "nodefile", "check_nodefile.py"
    )
    tests.job_cases.test_nodefile(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_reconnect(
    local_plugin: str, local_args: dict[str, typing.Any]
) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "reconnect", "sleep.py"
    )
    tests.job_cases.test_reconnect(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_array(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "array", "array.py"
    )
    tests.job_cases.test_array(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_array_ko(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "array_ko", "array_ko.py"
    )
    tests.job_cases.test_array_ko(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_array_cancel(
    local_plugin: str, local_args: dict[str, typing.Any]
) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "array_cancel", "array.py"
    )
    tests.job_cases.test_array_cancel(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)
