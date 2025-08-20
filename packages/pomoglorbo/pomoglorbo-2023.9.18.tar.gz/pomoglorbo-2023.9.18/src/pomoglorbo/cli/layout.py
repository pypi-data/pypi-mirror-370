# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next,
    focus_previous,
)
from prompt_toolkit.layout import (
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

from pomoglorbo.cli.help import HelpContainer
from pomoglorbo.cli.keybindings import (
    Actions,
    get_key_bindings,
)
from pomoglorbo.cli.util import exit_clicked
from pomoglorbo.core.tomato import (
    make_tomato,
    tomato_interact,
)
from pomoglorbo.types import (
    Configuration,
    Tomato,
    TomatoLayout,
    UserInterface,
)


def create_layout(tomato: Tomato) -> TomatoLayout:
    btn_start = Button("Start", handler=lambda: tomato_interact(tomato, "start"))
    buttons: list[Button] = [
        btn_start,
        Button("Pause", handler=lambda: tomato_interact(tomato, "pause")),
        Button("Reset", handler=lambda: tomato_interact(tomato, "reset")),
        Button("Reset All", handler=lambda: tomato_interact(tomato, "reset_all")),
        Button("Exit", handler=exit_clicked),
    ]

    helpwindow = HelpContainer(tomato.config.key_bindings)
    # All the widgets for the UI.
    warning_display = FormattedTextControl(focusable=False)
    last_cmd_display = FormattedTextControl(focusable=False)
    status = FormattedTextControl(focusable=False)
    text_area = FormattedTextControl(focusable=False, show_cursor=False)
    text_width = Dimension(max=40)
    text_window = HSplit(
        [
            Window(content=status, width=text_width, wrap_lines=True),
            Window(content=text_area, wrap_lines=True),
        ]
    )
    root_container = Box(
        VSplit(
            [
                HSplit(buttons, padding=1),
                HSplit(
                    [
                        text_window,
                        Window(warning_display, width=text_width, wrap_lines=True),
                        Window(last_cmd_display, width=text_width, wrap_lines=True),
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


def make_user_interface(config: Configuration) -> UserInterface:
    def toggle_help_window_state() -> None:
        if layout.helpwindow.is_visible():
            layout.helpwindow.hide()
        else:
            layout.helpwindow.show()

    tomato = make_tomato(config)

    layout = create_layout(tomato)

    actions: Actions = {
        "focus_next": focus_next,
        "focus_previous": focus_previous,
        "exit_clicked": lambda _: exit_clicked(),
        "start": lambda _: tomato_interact(tomato, "start"),
        "pause": lambda _: tomato_interact(tomato, "pause"),
        "reset": lambda _: tomato_interact(tomato, "reset"),
        "reset_all": lambda _: tomato_interact(tomato, "reset_all"),
        "help": lambda _: toggle_help_window_state(),
    }

    application: Application[object] = Application(
        layout=layout.layout,
        key_bindings=get_key_bindings(tomato.config, actions),
        full_screen=True,
    )
    return UserInterface(
        tomato=tomato,
        layout=layout,
        config=config,
        application=application,
    )
