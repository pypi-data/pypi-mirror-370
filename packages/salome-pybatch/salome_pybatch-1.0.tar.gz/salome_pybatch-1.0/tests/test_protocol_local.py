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
import tempfile
import os
import shutil
import sys
from pathlib import Path
import pybatch
import pybatch.protocols.local


def test_protocol_local() -> None:
    py_exe = sys.executable
    # Test configuration
    test_dir = tempfile.mkdtemp(suffix="_pybatchtest")
    work_dir = os.path.join(test_dir, "remote_dir")
    local_work_dir = os.path.join(test_dir, "local_dir")
    os.mkdir(work_dir)
    os.mkdir(local_work_dir)
    p = pybatch.protocols.local.LocalProtocol()
    test_file_name = "local_test.txt"
    remote_test_file = os.path.join(work_dir, test_file_name)
    local_test_file = os.path.join(local_work_dir, test_file_name)
    # Test download a remote path that does not exist.
    try:
        p.download([remote_test_file], local_test_file)
    except pybatch.PybatchException as e:
        assert remote_test_file in str(e)
    else:
        assert 0

    ## Test create a file in an inaccessible place
    try:
        p.create("/no/directory/", "file content")
    except FileNotFoundError as e:
        assert "directory" in str(e)
    else:
        assert 0

    # Test create + download
    file_content = "Servus!"
    p.create(remote_test_file, file_content)
    remote_content = p.read(remote_test_file)
    assert remote_content == file_content
    p.download([remote_test_file], local_test_file)
    assert Path(local_test_file).read_text() == file_content

    # download in an inaccessible place
    local_wrong_path = os.path.join(local_work_dir, "nodir", "nofile")
    try:
        p.download([remote_test_file], local_wrong_path)
    except FileNotFoundError as e:
        assert "nodir" in str(e)
    else:
        assert 0

    # upload nonexistent file
    try:
        p.upload([local_wrong_path], work_dir)
    except pybatch.PybatchException as e:
        assert "nodir" in str(e)
    else:
        assert 0

    # upload file to an inaccessible place
    try:
        p.upload([local_test_file], "/no/directory/")
    except FileNotFoundError as e:
        assert "directory" in str(e)
    else:
        assert 0

    # upload + download + check
    name_bis = "local_test_bis.txt"
    remote_test_file_bis = os.path.join(work_dir, name_bis)
    local_test_file_bis = os.path.join(local_work_dir, name_bis)
    p.upload([local_test_file], remote_test_file_bis)
    assert Path(remote_test_file_bis).read_text() == file_content
    p.download([remote_test_file_bis], local_test_file_bis)
    assert Path(local_test_file_bis).read_text() == file_content

    # run
    command = [py_exe, "-c", 'print("Cool!")']
    res = p.run(command)
    assert res.strip() == "Cool!"

    ## run error
    command = [py_exe, "-c", "exit(1)"]
    try:
        res = p.run(command)
    except pybatch.PybatchException as e:
        assert "Error 1" in str(e)
    else:
        assert 0

    shutil.rmtree(test_dir)
