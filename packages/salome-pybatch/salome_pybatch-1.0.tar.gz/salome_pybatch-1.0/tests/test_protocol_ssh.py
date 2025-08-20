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
import tempfile
import os
import shutil
from pathlib import Path
import pybatch
import pybatch.protocols.ssh
from pybatch.tools import path_join


def test_protocol_ssh(remote_args: dict[str, typing.Any]) -> None:
    if "python_exe" in remote_args:
        python_exe = remote_args["python_exe"]
    else:
        python_exe = "python3"
    # Test connection to a host that does not exist
    connect_param = pybatch.ConnectionParameters(host="noname_zozo")
    p = pybatch.protocols.ssh.SshProtocol(connect_param)
    try:
        p.run([python_exe, "-c", "exit(0)"])
    except pybatch.PybatchException as e:
        assert "noname_zozo" in str(e)
        assert f"command: ['ssh', 'noname_zozo', '{python_exe}', '-c', " in str(
            e
        )
    else:
        assert 0

    # Test configuration
    hostname = remote_args["host"]
    work_dir = remote_args["work_dir"]
    gss_auth = False
    if "gss_auth" in remote_args:
        gss_auth = remote_args["gss_auth"]
    is_posix = True
    if "is_posix" in remote_args:
        is_posix = remote_args["is_posix"]
    connect_param = pybatch.ConnectionParameters(
        host=hostname, gss_auth=gss_auth
    )
    if "user" in remote_args:
        connect_param.user = remote_args["user"]
    if "password" in remote_args:
        connect_param.password = remote_args["password"]
    p = pybatch.protocols.ssh.SshProtocol(connect_param)
    local_work_dir = tempfile.mkdtemp(suffix="_pybatchtest")
    test_file_name = "ssh_test.txt"
    remote_test_file = path_join(work_dir, test_file_name, is_posix=is_posix)
    local_test_file = os.path.join(local_work_dir, test_file_name)
    # Test download a remote path that does not exist.
    try:
        p.download([remote_test_file], local_test_file)
    except pybatch.PybatchException as e:
        # The remote path should be included in the error message
        # but the full message may depend on the language.
        assert remote_test_file in str(e)
    else:
        assert 0

    # Test create a file in an inaccessible place
    try:
        p.create("/no/directory/", "file content")
    except pybatch.PybatchException as e:
        assert "/no/directory" in str(e)
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
    except pybatch.PybatchException as e:
        # assert compatible Linux & Windows
        assert "nodir" in str(e)
        assert "nofile" in str(e)
    else:
        assert 0

    # upload nonexistent file
    try:
        p.upload([local_wrong_path], work_dir)
    except pybatch.PybatchException as e:
        # assert compatible Linux & Windows
        assert "nodir" in str(e)
        assert "nofile" in str(e)
    else:
        assert 0

    # upload file to an inaccessible place
    try:
        p.upload([local_test_file], "/no/directory/")
    except pybatch.PybatchException as e:
        assert "/no/directory/" in str(e)
    else:
        assert 0

    # upload + download + check
    name_bis = "ssh_test_bis.txt"
    remote_test_file_bis = path_join(work_dir, name_bis, is_posix=is_posix)
    local_test_file_bis = os.path.join(local_work_dir, name_bis)
    p.upload([local_test_file], remote_test_file_bis)
    p.download([remote_test_file_bis], local_test_file_bis)
    assert Path(local_test_file_bis).read_text() == file_content

    # run
    command = [python_exe, "-c", 'print("Cool!")']
    res = p.run(command)
    assert res.strip() == "Cool!"

    # run error
    command = [python_exe, "-c", "exit(1)"]
    try:
        res = p.run(command)
    except pybatch.PybatchException as e:
        assert "Error 1" in str(e)
    else:
        assert 0

    # remove remote files
    pycommand = f'import os; os.remove("{remote_test_file}")'
    p.run([python_exe, "-c", pycommand])
    pycommand = f'import os; os.remove("{remote_test_file_bis}")'
    p.run([python_exe, "-c", pycommand])

    shutil.rmtree(local_work_dir)
