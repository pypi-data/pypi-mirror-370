# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

"""
Functionality for IPC.

With this, we can let other programs know what we are up to by writing into
a file our current status.
"""

import logging
import socketserver
import threading
from socket import socket
from typing import Any

from pomoglorbo.tomato import tomato_interact
from pomoglorbo.types import (
    Configuration,
    InitialState,
    LongBreakState,
    PausedState,
    SmallBreakState,
    State,
    Tomato,
    WorkingState,
)
from pomoglorbo.util import format_remaining
from pomoglorbo.xdg_base_dirs import xdg_state_home

logger = logging.getLogger(__name__)


class PomoglorboHandler(socketserver.StreamRequestHandler):
    """Handler for socket connections."""

    def __init__(
        self,
        request: socket,
        client_address: Any,
        server: socketserver.BaseServer,
        tomato: Tomato,
    ):
        self.tomato = tomato
        super().__init__(request, client_address, server)

    def handle(self) -> None:
        """Handle incoming socket connections."""
        while True:
            data = self.rfile.readline()
            if not data:
                break

            command = data.decode().strip()
            match command:
                case "start" | "pause" | "reset" | "reset_all":
                    tomato_interact(self.tomato, command)
                case _:
                    response = f"ERROR: Unknown command '{command}'"
            response = f"OK: {command}"

            self.wfile.write(f"{response}\n".encode())
            self.wfile.flush()


def create_socket_server(tomato: Tomato) -> socketserver.BaseServer:
    """Create and run a unix domain socket server."""
    socket_path = xdg_state_home() / "pomoglorbo" / "socket"
    if not socket_path.parent.exists():
        socket_path.parent.mkdir(parents=True)
    if socket_path.exists():
        logger.warning("Socket path at %s already exists. Unlinking.", socket_path)
        socket_path.unlink()

    def handler_factory(
        request: socket, client_address: Any, server: socketserver.BaseServer
    ) -> socketserver.BaseRequestHandler:
        return PomoglorboHandler(request, client_address, server, tomato)

    server = socketserver.UnixStreamServer(str(socket_path), handler_factory)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    return server


def ipc_write_status(config: Configuration, state: State) -> None:
    """Write to our state file."""
    state_file = config.state_file
    if not state_file.parent.exists():
        state_file.parent.mkdir(parents=True)
    match state:
        case WorkingState() | LongBreakState() | SmallBreakState():
            content = f"""{format_remaining(state, "plain")}"""
        case PausedState():
            content = "paused"
        case InitialState():
            content = "ready"
    with open(state_file, "w") as fd:
        fd.write(f"Pomoglorbo: {content}")
