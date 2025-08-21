# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023-2025 Justus Perlwitz
#
# SPDX-License-Identifier: MIT
from datetime import datetime, timedelta
from gettext import gettext as _
from importlib import resources
from pathlib import Path
from typing import Literal, Optional

from playsound3 import playsound

import pomoglorbo
from pomoglorbo.types import RunningState, TaskStatus


def calc_remainder(state: RunningState) -> timedelta:
    return state.started_at + state.time_period - datetime.now()


def format_remaining(
    state: RunningState, style: Literal["fancy", "plain"] = "fancy"
) -> str:
    remainder = calc_remainder(state)
    minutes, seconds = divmod(max(int(remainder.total_seconds()), 0), 60)
    match style:
        case "fancy":
            if state.status == TaskStatus.STARTED:
                progress = next(state.progress) + " "
            else:
                progress = ""

            return _("{}{minutes}min {seconds:02d}s remaining").format(
                progress,
                minutes=minutes,
                seconds=seconds,
            )
        case "plain":
            return _("{minutes:02}:{seconds:02}").format(
                minutes=minutes, seconds=seconds
            )


def play(path: Optional[Path], block: bool) -> None:
    if path is None:
        with resources.path(pomoglorbo, "b15.wav") as file:
            playsound(str(file), block=block)
    else:
        playsound(str(path), block=block)
