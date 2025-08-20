# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import click

from typing import Optional
from os import environ
from click_default_group import DefaultGroup
from neon_utils.packaging_utils import get_package_version_spec

environ.setdefault("OVOS_CONFIG_BASE_FOLDER", "neon")
environ.setdefault("OVOS_CONFIG_FILENAME", "neon.yaml")


@click.group(
    "neon-messagebus",
    cls=DefaultGroup,
    no_args_is_help=True,
    invoke_without_command=True,
    help="Neon Messagebus Commands\n\nSee also: neon COMMAND --help",
)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    required=False,
    help="Print the current version",
)
def neon_messagebus_cli(version: bool = False):
    if version:
        click.echo(
            f"neon_messagebus version "
            f"{get_package_version_spec('neon_messagebus')}"
        )


@neon_messagebus_cli.command(help="Start Neon Messagebus module")
@click.option(
    "--health-check-server-port",
    "--hp",
    type=int,
    default=None,
    help="Port for the health check server to listen on",
)
def run(health_check_server_port: Optional[int] = None):
    from neon_messagebus.service.__main__ import main

    click.echo("Starting Messagebus Service")
    main(health_check_server_port=health_check_server_port)
    click.echo("Messagebus Service Shutdown")
