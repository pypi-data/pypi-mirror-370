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
import pybatch.plugins.nobatch.pybatch_manager as manager

import tempfile
from pathlib import Path
import os
import shutil
import inspect
import subprocess
import time
import sys


def test_hello():
    py_exe = sys.executable
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "hello.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit
    args = [
        py_exe,
        manager_script,
        "submit",
        workdir,
        py_exe,
        "hello.py",
        "zozo",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # wait
    args = [py_exe, manager_script, "wait", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # check
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FINISHED"
    output_file = Path(workdir) / "logs" / "output.log"
    assert output_file.read_text().strip() == "Hello zozo !"

    # clean
    shutil.rmtree(workdir)


def test_sleep():
    py_exe = sys.executable
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit long job
    args = [
        py_exe,
        manager_script,
        "submit",
        workdir,
        py_exe,
        "sleep.py",
        "1",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # wait
    args = [py_exe, manager_script, "wait", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # check
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FINISHED"
    result_file = Path(workdir) / "wakeup.txt"
    assert result_file.exists()

    # clean
    shutil.rmtree(workdir)


def test_cancel():
    py_exe = sys.executable
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit long job
    args = [
        py_exe,
        manager_script,
        "submit",
        workdir,
        py_exe,
        "sleep.py",
        "1",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # cancel
    args = [py_exe, manager_script, "cancel", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    time.sleep(2)

    # check
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FAILED"
    time.sleep(2)
    result_file = Path(workdir) / "wakeup.txt"
    assert not result_file.exists()

    # clean
    shutil.rmtree(workdir)


def test_timeout():
    """Wall time shorter than execution time."""
    py_exe = sys.executable
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit long job
    args = [
        py_exe,
        manager_script,
        "submit",
        workdir,
        "--wall_time",
        "1",
        py_exe,
        "sleep.py",
        "3",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    time.sleep(2)

    # check
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FAILED"
    time.sleep(2)
    result_file = Path(workdir) / "wakeup.txt"
    assert not result_file.exists()

    # clean
    shutil.rmtree(workdir)


def test_notimeout():
    """Walltime longer than execution time."""
    py_exe = sys.executable
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit
    args = [
        py_exe,
        manager_script,
        "submit",
        workdir,
        "--wall_time",
        "3",
        py_exe,
        "sleep.py",
        "1",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    time.sleep(2)

    # check
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FINISHED"
    result_file = Path(workdir) / "wakeup.txt"
    assert result_file.exists()

    # clean
    shutil.rmtree(workdir)


def test_array():
    "Simulation of a job array Slurm"
    py_exe = sys.executable
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "array.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)
    args = [
        py_exe,
        manager_script,
        "submit",
        workdir,
        "--total_jobs",
        "4",
        py_exe,
        "array.py",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # wait
    args = [py_exe, manager_script, "wait", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # check
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FINISHED"
    for idx in range(4):
        result = Path(workdir) / f"result_{idx}.txt"
        assert result.read_text() == str(idx)

    # clean
    shutil.rmtree(workdir)


def test_array_ko():
    "Job array with a failed job"
    py_exe = sys.executable
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "array_ko.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)
    args = [
        py_exe,
        manager_script,
        "submit",
        workdir,
        "--total_jobs",
        "4",
        py_exe,
        "array_ko.py",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # wait
    args = [py_exe, manager_script, "wait", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # check
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FAILED"
    for idx in range(4):
        result = Path(workdir) / f"result_{idx}.txt"
        assert result.read_text() == str(idx)
    exit_code = Path(workdir) / "logs" / "exit_code.log"
    assert "42" == exit_code.read_text()

    # clean
    shutil.rmtree(workdir)


def test_array_cancel():
    "Cancel on a job array."
    py_exe = sys.executable
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "array.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)
    args = [
        py_exe,
        manager_script,
        "submit",
        workdir,
        "--total_jobs",
        "4",
        py_exe,
        "array.py",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # cancel
    args = [py_exe, manager_script, "cancel", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # state
    args = [py_exe, manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FAILED"

    # clean
    shutil.rmtree(workdir)
