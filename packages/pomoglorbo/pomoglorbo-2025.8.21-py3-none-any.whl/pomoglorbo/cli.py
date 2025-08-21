#!/usr/bin/env python
# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023-2025 Justus Perlwitz
#
# SPDX-License-Identifier: MIT
"""Pomoglorbo's CLI package."""

import gettext
import socket
import subprocess
import sys
from gettext import gettext as _
from gettext import ngettext
from importlib import resources
from socketserver import BaseServer
from typing import (
    Callable,
    Optional,
)

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import (
    KeyBindings,
    KeyPressEvent,
)
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next,
    focus_previous,
)
from prompt_toolkit.layout import (
    ConditionalContainer,
    Dimension,
    FormattedTextControl,
    HSplit,
    Layout,
    VSplit,
    Window,
)
from prompt_toolkit.widgets import (
    Box,
    Button,
)

from pomoglorbo import messages
from pomoglorbo.config import create_configuration
from pomoglorbo.ipc import create_socket_server, ipc_write_status
from pomoglorbo.tomato import make_tomato, tomato_interact
from pomoglorbo.types import (
    Configuration,
    InitialState,
    LongBreakState,
    SmallBreakState,
    Tomato,
    TomatoLayout,
    TomatoRender,
    WorkingState,
    WorkPausedState,
)
from pomoglorbo.util import format_remaining, play
from pomoglorbo.xdg_base_dirs import xdg_state_home

EventCallback = Callable[[KeyPressEvent], None]


Actions = dict[str, EventCallback]


def exit_clicked() -> None:
    get_app().exit()


def get_key_bindings(
    config: Configuration,
    actions: Actions,
) -> KeyBindings:
    kb = KeyBindings()
    for action, keys in config.key_bindings.items():
        cb: Optional[EventCallback] = actions.get(action)
        if not cb:
            continue
        if not isinstance(keys, str):
            raise ValueError(f"Expected {keys} to be str")
        for key in keys.split(","):
            key = key.strip()
            kb.add(key)(cb)
    return kb


def create_layout(tomato: Tomato) -> TomatoLayout:
    btn_start = Button("Start", handler=lambda: tomato_interact(tomato, "start"))
    buttons: list[Button] = [
        btn_start,
        Button(_("Pause"), handler=lambda: tomato_interact(tomato, "pause")),
        Button(_("Reset"), handler=lambda: tomato_interact(tomato, "reset")),
        Button(_("Reset All"), handler=lambda: tomato_interact(tomato, "reset_all")),
        Button(_("Exit"), handler=exit_clicked),
    ]

    @Condition
    def help_visible() -> bool:
        return tomato.show_help

    help_content = _("""Help
====
Start      | {start}
Pause      | {pause}
Reset      | {reset}
Reset All  | {reset_all}
Help       | {help}
Focus Prev | {focus_previous}
Focus Next | {focus_next}
Exit       | {exit_clicked}
""").format(**tomato.config.key_bindings)
    helpwindow = ConditionalContainer(
        content=Window(FormattedTextControl(help_content)),
        filter=help_visible,
    )

    # All the widgets for the UI.
    warning_display = FormattedTextControl(focusable=False)
    last_cmd_display = FormattedTextControl(focusable=False)
    status = FormattedTextControl(focusable=False)
    text_area = FormattedTextControl(focusable=False, show_cursor=False)
    text_width = Dimension(max=40)
    root_container = Box(
        VSplit(
            [
                HSplit(buttons, padding=1),
                HSplit(
                    [
                        Window(content=text_area, width=text_width, wrap_lines=True),
                        helpwindow,
                    ],
                    padding=1,
                ),
            ],
            padding=4,
        )
    )

    return TomatoLayout(
        layout=Layout(container=root_container, focused_element=btn_start),
        text_area=text_area,
        status=status,
        helpwindow=helpwindow,
        warning_display=warning_display,
        last_cmd_display=last_cmd_display,
    )


def render_tomato(tomato: Tomato) -> TomatoRender:
    """Render the main tomato screen."""
    set_message = ngettext(
        "1 set completed", "{sets} sets completed", tomato.sets
    ).format(sets=tomato.sets)

    match tomato.state:
        case SmallBreakState() | LongBreakState() | WorkingState():
            time = format_remaining(tomato.state)
        case WorkPausedState():
            time = _("Press [start] to continue")
        case InitialState():
            time = _("Press [start] to begin")

    tomatoes_per_set = tomato.config.tomatoes_per_set
    tomatoes_remaining = tomatoes_per_set - tomato.tomatoes % tomatoes_per_set
    ascii_tomato = "(`) "
    count = ascii_tomato * tomatoes_remaining

    ftext_lines = [
        tomato.state.name,
        "",
        time,
        count,
        set_message,
        "",
        tomato.last_warning or "",
        tomato.last_cmd_out or "",
    ]
    ftext: str = "\n".join(ftext_lines)

    return TomatoRender(text=ftext, show_help=tomato.show_help)


def draw(tomato: Tomato, layout: TomatoLayout) -> None:
    """Perform a single tomato update cycle."""
    tomato_interact(tomato, "update")
    result = render_tomato(tomato)
    ipc_write_status(tomato.config, tomato.state)
    layout.text_area.text = result.text


def make_user_interface(
    config: Configuration,
) -> tuple[Application[object], Optional[BaseServer]]:
    """
    Create the user interface.

    Optionally, this creates a socket server.
    """
    tomato = make_tomato(config)
    if config.socket_server:
        server = create_socket_server(tomato)
    else:
        server = None

    layout = create_layout(tomato)

    actions: Actions = {
        "focus_next": focus_next,
        "focus_previous": focus_previous,
        "exit_clicked": lambda _: exit_clicked(),
        "start": lambda _: tomato_interact(tomato, "start"),
        "pause": lambda _: tomato_interact(tomato, "pause"),
        "reset": lambda _: tomato_interact(tomato, "reset"),
        "reset_all": lambda _: tomato_interact(tomato, "reset_all"),
        "help": lambda _: tomato_interact(tomato, "toggle_help"),
    }

    application: Application[object] = Application(
        layout=layout.layout,
        key_bindings=get_key_bindings(tomato.config, actions),
        full_screen=True,
        refresh_interval=1,
        before_render=lambda _: draw(tomato, layout),
    )
    return application, server


def send_ipc_command(command: str) -> int:
    """Send a command to the running Pomoglorbo instance via IPC."""
    socket_path = xdg_state_home() / "pomoglorbo" / "socket"

    if not socket_path.exists():
        print(
            _("Could not find socket at {socket_path}").format(socket_path=socket_path)
        )
        return 1

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(str(socket_path))
            sock.sendall(f"{command}\n".encode())
            response = sock.recv(1024).decode().strip()
            print(response)
        return 0
    except ConnectionRefusedError as e:
        raise RuntimeError(_("Error: Could not connect to Pomoglorbo instance")) from e
    except Exception as e:
        raise RuntimeError(_("Encountered other error")) from e


def main() -> int:
    path = resources.files(messages)
    with resources.as_file(path) as path:
        gettext.bindtextdomain("messages", localedir=path)
    gettext.textdomain("messages")

    config = create_configuration()

    if config.send_command:
        return send_ipc_command(config.send_command)

    if config.audio_check:
        # WHY twice: to catch more issues
        print(_("Playing alarm once..."))
        play(config.audio_file, block=True)
        print(_("Playing alarm twice..."))
        play(config.audio_file, block=True)
        print(_("Have a nice day"))
        return 0

    application, server = make_user_interface(config)
    try:
        application.run()
    finally:
        if server:
            server.shutdown()
    if config.exit_cmd:
        subprocess.run(config.exit_cmd)
    return 0


if __name__ == "__main__":
    # Profiling method 1)
    # import pstats
    # import cProfile
    # pr = cProfile.Profile()
    # pr.enable()
    # main()
    # pr.disable()
    # sortby = pstats.SortKey.CUMULATIVE
    # with open("profile.txt", "w") as fd:
    #     ps = pstats.Stats(pr, stream=fd).sort_stats(sortby)
    #     ps.print_stats()
    #
    # Profiling method 2)
    # https://github.com/sumerc/yappi/blob/master/doc/api.md
    # import yappi

    # yappi.set_clock_type("cpu")
    # yappi.start()
    sys.exit(main())
    # with open("profile.txt", "w") as fd:
    #     stats = yappi.get_func_stats()
    #     stats.save("profile.pstat", "pstat")
    # then snakeviz profile.pstat
