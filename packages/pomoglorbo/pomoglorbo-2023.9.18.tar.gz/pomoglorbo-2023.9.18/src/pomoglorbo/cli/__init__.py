#!/usr/bin/env python

# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

import subprocess
import threading

from pomoglorbo.cli.layout import make_user_interface
from pomoglorbo.cli.render import render_tomato
from pomoglorbo.core import sound
from pomoglorbo.core.config import create_configuration
from pomoglorbo.core.tomato import tomato_interact
from pomoglorbo.core.util import (
    every,
)
from pomoglorbo.types import UserInterface


def draw(interface: UserInterface) -> None:
    tomato_interact(interface.tomato, "update")
    result = render_tomato(interface.tomato)
    layout = interface.layout
    layout.status.text = result.status
    layout.text_area.text = result.text
    layout.warning_display.text = result.warning or ""
    layout.last_cmd_display.text = result.cmd_out or ""
    interface.application.invalidate()


def run(interface: UserInterface) -> None:
    draw(interface)
    threading.Thread(
        target=lambda: every(1, lambda: draw(interface)),
        daemon=True,
    ).start()
    interface.application.run()


def main() -> None:
    config = create_configuration()
    if config.audio_check:
        # WHY twice: to catch more issues
        sound.play(config.audio_file, config.volume, block=True)
        sound.play(config.audio_file, config.volume, block=True)
        return
    ui = make_user_interface(config)
    run(ui)
    if config.exit_cmd:
        subprocess.run(config.exit_cmd)


if __name__ == "__main__":
    main()
