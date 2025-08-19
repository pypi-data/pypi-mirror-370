# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

import typer

from bdns.api.utils import format_url
from bdns.api.types import Ambito
from bdns.api.fetch_write import fetch_and_write
from bdns.api.commands import options
from bdns.api.endpoints import BDNS_API_ENDPOINT_REGLAMENTOS


def reglamentos(
    ctx: typer.Context, vpd: str = options.vpd, ambito: Ambito = options.ambito
) -> None:
    """
    Fetches all regulations (EU) from a portal ordered by the description.
    """
    params = {
        "vpd": vpd,
        "ambito": ambito.value if ambito else None,
    }
    fetch_and_write(
        url=format_url(BDNS_API_ENDPOINT_REGLAMENTOS, params),
        output_file=ctx.obj["output_file"],
    )
