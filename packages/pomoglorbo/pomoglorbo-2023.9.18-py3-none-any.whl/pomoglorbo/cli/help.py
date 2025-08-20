# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

from collections.abc import Mapping

from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import (
    ConditionalContainer,
    HSplit,
)
from prompt_toolkit.widgets import (
    Box,
    Label,
)


class HelpContainer(ConditionalContainer):
    visible: bool

    def __init__(self, keybindings: Mapping[str, str] = {}) -> None:
        self.visible = False

        content = Box(
            HSplit(
                [
                    Label(text="----------------Help------------------\n"),
                    Label(text=f"start         | {keybindings['start']}"),
                    Label(text=f"pause         | {keybindings['pause']}"),
                    Label(text=f"reset         | {keybindings['reset']}"),
                    Label(text=f"reset all     | {keybindings['reset_all']}"),
                    Label(text=f"help          | {keybindings['help']}"),
                    Label(text=f"focus prev    | {keybindings['focus_previous']}"),
                    Label(text=f"focus next    | {keybindings['focus_next']}"),
                    Label(text=f"exit          | {keybindings['exit_clicked']}"),
                ]
            )
        )

        @Condition
        def is_visible() -> bool:
            return self.visible

        super().__init__(filter=is_visible, content=content)

    def is_visible(self) -> bool:
        return self.visible

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False
