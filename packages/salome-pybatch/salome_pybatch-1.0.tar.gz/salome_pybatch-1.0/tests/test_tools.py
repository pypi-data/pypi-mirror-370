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
def test_slurm_time_to_seconds():
    from pybatch.tools import slurm_time_to_seconds as converter
    from pybatch import PybatchException

    assert converter(" ") == ""
    assert converter("10") == "600"
    assert converter("10:30") == "630"
    assert converter("100:30") == "6030"
    assert converter("2:10:5") == "7805"
    assert converter("2:10:05") == "7805"
    assert converter("2-2:10:30") == "180630"
    assert converter("2-2") == "180000"
    assert converter("2-2:10") == "180600"
    try:
        converter("2-0-4")
    except PybatchException:
        pass
    else:
        assert 0  # Exception expected
    try:
        converter("xvi")
    except PybatchException:
        pass
    else:
        assert 0  # Exception expected
    try:
        converter("1:2:3:4")
    except PybatchException:
        pass
    else:
        assert 0  # Exception expected
