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
"""Local tests for any plugin."""

import tempfile
from pathlib import Path
import os
import shutil
import time
import sys


def test_python_script(job_plugin):
    """Launch a python script which ends without errors.

    Check files from 'logs' folder.
    """
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "hello.py"
    is_posix = os.name == "posix"
    params = pybatch.LaunchParameters(
        [sys.executable, "hello.py", "world"],
        workdir,
        input_files=[script],
        python_exe=sys.executable,
        is_posix=is_posix,
    )
    job = pybatch.create_job(job_plugin, params)
    job.submit()
    job.wait()

    assert "Hello world !" in job.stdout()
    assert not job.stderr()
    assert job.exit_code() == 0
    shutil.rmtree(workdir)


def test_finish_without_wait(job_plugin):
    "Test that a job can finish without using job.wait()."
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "hello.py"
    is_posix = os.name == "posix"
    params = pybatch.LaunchParameters(
        [sys.executable, "hello.py", "world"],
        workdir,
        input_files=[script],
        python_exe=sys.executable,
        is_posix=is_posix,
    )
    job = pybatch.create_job(job_plugin, params)
    job.submit()
    time.sleep(2)  # instead of job.wait()
    assert job.state() == "FINISHED"
    shutil.rmtree(workdir)


def test_error_script(job_plugin):
    """Launch a python script which ends in error.

    Check files from 'logs' folder.
    """
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "error.py"
    is_posix = os.name == "posix"
    params = pybatch.LaunchParameters(
        [sys.executable, "error.py"],
        workdir,
        input_files=[script],
        python_exe=sys.executable,
        is_posix=is_posix,
    )
    job = pybatch.create_job(job_plugin, params)
    job.submit()
    job.wait()

    assert "Problems comming..." in job.stdout()
    assert "Oups!" in job.stderr()
    assert job.exit_code() == 1
    shutil.rmtree(workdir)


def test_state(job_plugin):
    """Test the state of a job."""
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    is_posix = os.name == "posix"
    params = pybatch.LaunchParameters(
        [sys.executable, "sleep.py", "1"],
        workdir,
        input_files=[script],
        python_exe=sys.executable,
        is_posix=is_posix,
    )
    job = pybatch.create_job(job_plugin, params)
    assert job.state() == "CREATED"
    job.submit()
    assert job.state() == "RUNNING"
    job.wait()
    assert job.state() == "FINISHED"
    assert job.exit_code() == 0
    assert (Path(workdir) / "wakeup.txt").exists()
    shutil.rmtree(workdir)


def test_cancel(job_plugin):
    """Cancel a running job."""
    import pybatch
    import time

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    is_posix = os.name == "posix"
    params = pybatch.LaunchParameters(
        [sys.executable, "sleep.py", "2"],
        workdir,
        input_files=[script],
        python_exe=sys.executable,
        is_posix=is_posix,
    )
    job = pybatch.create_job(job_plugin, params)
    assert job.state() == "CREATED"
    job.submit()
    time.sleep(1)
    job.cancel()
    job.wait()
    time.sleep(2)  # sleep.py would have had the time to finish if not canceled.
    assert not (Path(workdir) / "wakeup.txt").exists()
    assert job.exit_code() != 0
    shutil.rmtree(workdir)


def test_serialization(job_plugin):
    """Serialization / deserialization of a submited job in the same script."""
    import pybatch
    import pickle

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    is_posix = os.name == "posix"
    params = pybatch.LaunchParameters(
        [sys.executable, "sleep.py", "1"],
        workdir,
        input_files=[script],
        python_exe=sys.executable,
        is_posix=is_posix,
    )
    job = pybatch.create_job(job_plugin, params)
    job.submit()
    pick_job = pickle.dumps(job)
    new_job = pickle.loads(pick_job)
    assert new_job.state() == "RUNNING"
    new_job.wait()
    assert new_job.state() == "FINISHED"
    shutil.rmtree(workdir)


def test_wall_time(job_plugin):
    """Job with wall time."""
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    is_posix = os.name == "posix"
    params = pybatch.LaunchParameters(
        [sys.executable, "sleep.py", "3"],
        workdir,
        input_files=[script],
        wall_time="0:1",  # 1s
        python_exe=sys.executable,
        is_posix=is_posix,
    )
    job = pybatch.create_job(job_plugin, params)
    job.submit()
    job.wait()
    assert not (Path(workdir) / "wakeup.txt").exists()
    assert job.exit_code() != 0  # return value is OS specific
    shutil.rmtree(workdir)


def test_files_and_directories(job_plugin):
    """Job that uses and produces files and directories."""
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "code.py"
    file_input = Path(current_file_dir) / "data" / "input.txt"
    dir_input = Path(current_file_dir) / "data" / "data"
    is_posix = os.name == "posix"
    params = pybatch.LaunchParameters(
        [sys.executable, "code.py", "1"],
        workdir,
        input_files=[script, file_input, dir_input],
        python_exe=sys.executable,
        is_posix=is_posix,
    )
    job = pybatch.create_job(job_plugin, params)
    job.submit()
    job.wait()
    assert not job.stderr()
    assert job.exit_code() == 0
    job.get(["output.txt"], resultdir)
    assert (Path(resultdir) / "output.txt").read_text() == "51"
    job.get(["data"], resultdir)
    assert (Path(resultdir) / "data" / "output.txt").read_text() == "69"
    shutil.rmtree(workdir)
    shutil.rmtree(resultdir)
