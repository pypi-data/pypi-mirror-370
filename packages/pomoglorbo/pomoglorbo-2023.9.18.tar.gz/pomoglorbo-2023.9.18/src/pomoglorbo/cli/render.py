# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

from pomoglorbo.core.states import (
    InitialState,
    LongBreakState,
    SmallBreakState,
    State,
    WorkingState,
)
from pomoglorbo.core.util import calc_remainder, format_time
from pomoglorbo.types import Tomato, TomatoRender


def render_time_remaining(tomato: Tomato, state: State) -> str:
    """Give time remaining for this state."""
    match state:
        case (
            SmallBreakState()
            | LongBreakState()
            | WorkingState()
        ) if not tomato.config.no_clock:
            remainder = calc_remainder(state)
            return format_time(state, remainder)
        case InitialState():
            return "Press [start]"
        case _:
            return ""


def render_tomato(tomato: Tomato) -> TomatoRender:
    if tomato.sets == 1:
        set_message = "1 set completed"
    else:
        set_message = f"{tomato.sets} sets completed"

    time = render_time_remaining(tomato, tomato.state)

    tomatoes_per_set = tomato.config.tomatoes_per_set
    tomatoes_remaining = tomatoes_per_set - tomato.tomatoes % tomatoes_per_set
    ascii_tomato = "(`) "
    count = ascii_tomato * tomatoes_remaining

    ftext_lines = [time, count, set_message]
    ftext: str = "\n".join(ftext_lines)

    return TomatoRender(
        text=ftext,
        warning=tomato.last_warning,
        cmd_out=tomato.last_cmd_out,
        status=tomato.state.name,
    )
