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
def test_version():
    import pybatch

    assert pybatch.__version__ == "1.0"


def test_plugin():
    import pybatch

    params = pybatch.LaunchParameters("script", "dir")
    import pybatch.plugins.local.job

    job = pybatch.create_job("local", params)
    assert isinstance(job, pybatch.plugins.local.job.Job)

    import pybatch.plugins.slurm.job

    job = pybatch.create_job("slurm", params)
    assert isinstance(job, pybatch.plugins.slurm.job.Job)

    import pybatch.plugins.nobatch.job

    job = pybatch.create_job("nobatch", params)
    assert isinstance(job, pybatch.plugins.nobatch.job.Job)
