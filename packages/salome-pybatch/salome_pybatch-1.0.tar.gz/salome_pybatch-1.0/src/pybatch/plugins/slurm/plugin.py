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

# type: ignore
from __future__ import annotations
from pybatch import GenericJob, LaunchParameters, GenericProtocol
from .job import Job


class Plugin:
    @property
    def description(self) -> str:
        return """Job submission using slurm batch manager."""

    def create_job(
        self, param: LaunchParameters, connection_protocol: GenericProtocol
    ) -> GenericJob:
        return Job(param, connection_protocol)
