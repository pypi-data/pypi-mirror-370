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

from ovos_utils import wait_for_exit_signal
from ovos_utils.log import LOG
from ovos_utils.process_utils import reset_sigint_handler, PIDLock as Lock
from neon_utils.log_utils import init_log
from neon_utils.process_utils import (
    start_malloc,
    snapshot_malloc,
    print_malloc,
)
from ovos_config.config import Configuration
from neon_messagebus.service import NeonBusService


def main(**kwargs):
    init_log(log_name="bus")
    reset_sigint_handler()
    # Create PID file, prevent multiple instances of this service
    lock = Lock("bus")
    config = Configuration()
    debug = Configuration().get("debug", False)
    malloc_running = start_malloc(config, stack_depth=4)
    kwargs.setdefault("debug", debug)
    kwargs.setdefault("config", config)

    health_check_port = kwargs.pop("health_check_server_port", None)
    service = NeonBusService(daemonic=True, **kwargs)
    if health_check_port is not None:
        from neon_utils.process_utils import start_health_check_server
        start_health_check_server(service.status, health_check_port,
                                  service.check_health)

    service.start()
    LOG.debug("Waiting for exit signal")
    wait_for_exit_signal()

    if malloc_running:
        try:
            print_malloc(snapshot_malloc())
        except Exception as e:
            LOG.error(e)
    service.shutdown()

    lock.delete()


def deprecated_entrypoint():
    from ovos_utils.log import log_deprecation

    log_deprecation(
        "Use `neon-messagebus run` in place of `neon_messagebus_service`",
        "2.0.0",
    )
    main()


if __name__ == "__main__":
    main()
