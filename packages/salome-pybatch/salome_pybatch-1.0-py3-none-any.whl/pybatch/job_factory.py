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
from importlib.metadata import entry_points
from .genericjob import GenericJob
from .generic_protocol import GenericProtocol
from .parameter import LaunchParameters


def create_job(
    plugin_name: str,
    params: LaunchParameters,
    connection_protocol: GenericProtocol | None = None,
) -> GenericJob:
    """Create the job with the chosen plugin.

    :param plugin_name: name of the plugin to use for the job creation.
    :param params: job parameters.
    :param connection_protocol: protocol for remote connection. None for local
     use.
    """

    # for entry_point in entry_points().get("pybatch.plugins"):
    ep = entry_points()
    if isinstance(ep, dict):
        # older python version
        ep_it = ep["pybatch.plugins"]
    else:
        ep_it = ep.select(group="pybatch.plugins")
    for entry_point in ep_it:
        if entry_point.name == plugin_name:
            plugin = entry_point.load()()
            job: GenericJob = plugin.create_job(params, connection_protocol)
            return job
    raise Exception(f"Plugin {plugin_name} not found.")


def reload_job(dump: str) -> GenericJob:  # type: ignore
    """Reload a job from a dumped string - for future use, not implemented.

    :param dump: representation of the job.
    """
    ...  # TODO
