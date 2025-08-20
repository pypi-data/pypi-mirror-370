# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

"""
Tomato state machine
====================

This can be modelled as a state machine.

Pydoro implementation
---------------------

States are

┌────────────────────────────────────────────────────────────────┐
│   Initial ───► WorkingState  ──► IntermediateState───────┐     │
│   State        ▲   ▲     ▲               │               │     │
│                │   │     └────────────┐  │               │     │
│                │   │       Break over │  │               │     │
│           Long │   ▼                  ▼  ▼               │     │
│           break│   WorkPausedState   SmallBreakState     │     │
│           over │                       ▲                 │     │
│                │                       │                 │     │
│                │                       │                 │     │
│                │                       ▼                 │     │
│                LongBreakState    SmallBreakPausedState   │     │
│                ▲          ▲                              │     │
│                │          └──────────────────────────────┘     │
│                │              Pomodoro set over                │
│                ▼                                               │
│                LongBreakPausedState                            │
└────────────────────────────────────────────────────────────────┘

Pomoglorbo implementation
-------------------------

Here we use

┌────────────────────────────────────────────────────────────────┐
│                   WorkPausedState                              │
│                        ▲                                       │
│              start     │ pause  auto transition                │
│ InitialState ───► WorkingState ────► SmallBreakState           │
│        ▲               │                   │                   │
│        │               │ After pomodoro    │ auto transition   │
│        │               │ set is over       │                   │
│        ├───────────────│───────────────────┘                   │
│        │               │                                       │
│        │               ▼                                       │
│        └────────────LongBreakState                             │
│        auto transition                                         │
└────────────────────────────────────────────────────────────────┘

Idea (2023-08-29)
-----------------

If we allow skipping from break to work it would be

┌─────────────────────────────────────────────────────────────────┐
│                   WorkPausedState                               │
│                        ▲                                        │
│                        │pause                                   │
│                        │       auto                             │
│              start     │     transition                         │
│ InitialState ───► WorkingState ────► SmallBreakState            │
│        ▲             ▲ │  ▲            │   │                    │
│        │           s │ │  │    skip    │   │                    │
│        │           k │ │  └────────────┘   │                    │
│        │           i │ │                   │    auto            │
│        │           p │ │                   │ transition         │
│        │             │ │   After pomodoro  │                    │
│        │             │ │    set is over    │                    │
│        ├─────────────┼─┼───────────────────┘                    │
│        │             │ ▼                                        │
│        └────────────LongBreakState                              │
│           auto                                                  │
│        transition                                               │
└─────────────────────────────────────────────────────────────────┘
"""

import subprocess
from dataclasses import replace

from pomoglorbo.const import SECONDS_PER_MIN
from pomoglorbo.core import sound
from pomoglorbo.core.ipc import ipc_write_status
from pomoglorbo.types import (
    Configuration,
    MaybeCommand,
    Tomato,
    TomatoInput,
    TomatoInteraction,
)

from .states import (
    InitialState,
    LongBreakState,
    RunningState,
    RunningStateLiteral,
    SmallBreakState,
    WorkingState,
    WorkPausedState,
)
from .util import calc_remainder, cur_time


def calculate_time_period(config: Configuration, state: RunningStateLiteral) -> int:
    match state:
        case "working":
            return int(config.work_minutes * SECONDS_PER_MIN)
        case "small-break":
            return int(config.small_break_minutes * SECONDS_PER_MIN)
        case "long-break":
            return int(config.long_break_minutes * SECONDS_PER_MIN)


def state_done(state: RunningState) -> bool:
    """Return if state is done."""
    return calc_remainder(state) <= 0


def is_end_of_set(tomato: Tomato) -> bool:
    return tomato.tomatoes % tomato.config.tomatoes_per_set == 0


def _tomato_interact(tomato: Tomato, input: TomatoInput) -> TomatoInteraction:
    config = tomato.config
    maybe_cmd: MaybeCommand = None
    play_alarm = False
    warning = None
    match (input, tomato.state):
        case "start", SmallBreakState() | LongBreakState() | InitialState() as state:
            play_alarm = True
            if cmd := config.work_state_cmd:
                maybe_cmd = cmd + (tomato.config.work_state_cmd_suffix or [])
            state = WorkingState(
                started_at=cur_time(),
                time_period=calculate_time_period(config, "working"),
            )
        case "start", WorkPausedState() as state:
            maybe_cmd = config.work_resumed_state_cmd
            # We know when the original task was started
            # And when we went into pause.
            # Then, the already elapsed time for the paused task is
            # the distance between
            elapsed_time = state.started_at - state.prev.started_at
            # Then we decrease the original tasks time period by this
            time_period = state.prev.time_period - elapsed_time
            state = replace(
                state.prev,
                time_period=time_period,
            )
        case "start", state:
            warning = "Can't start from here"
        case "pause", WorkingState() as state:
            maybe_cmd = config.work_paused_state_cmd
            state = WorkPausedState(prev=state, started_at=cur_time())
        case "pause", state:
            warning = "Can't pause here"
        case "reset", WorkingState() | SmallBreakState() | LongBreakState() as state:
            state = replace(state, started_at=cur_time())
        case "reset", WorkPausedState(prev=prev) as state:
            state = replace(state, prev=replace(prev, started_at=cur_time()))
        case "reset", state:
            warning = "Can't reset here"
        case "reset_all", _:
            state = InitialState(started_at=cur_time())
            tomato.tomatoes = 0
        case "update", WorkingState() as running_state if state_done(running_state):
            play_alarm = True
            tomato.tomatoes += 1
            if is_end_of_set(tomato):
                tomato.sets += 1
                state = LongBreakState(
                    time_period=calculate_time_period(config, "long-break"),
                    started_at=cur_time(),
                )
                maybe_cmd = config.long_break_state_cmd
            else:
                state = SmallBreakState(
                    time_period=calculate_time_period(config, "small-break"),
                    started_at=cur_time(),
                )
                maybe_cmd = config.small_break_state_cmd
        case "update", SmallBreakState() | LongBreakState() as state if state_done(
            state
        ):
            play_alarm = True
            state = InitialState(started_at=cur_time())
            maybe_cmd = config.break_over_cmd
        case "update", state:
            pass  # no op
    return TomatoInteraction(
        new_state=state,
        cmd=maybe_cmd,
        play_alarm=play_alarm,
        warning=warning,
    )


def tomato_interact(tomato: Tomato, input: TomatoInput) -> None:
    result = _tomato_interact(tomato, input)
    if result.play_alarm and not tomato.config.no_sound:
        sound.play(tomato.config.audio_file, tomato.config.volume, block=False)
    if result.warning:
        tomato.last_warning = result.warning
    if (command := result.cmd) is not None:
        try:
            out = subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as error:
            tomato.last_cmd_out = error.output.decode()
            tomato.last_warning = f"Command {command} did not run successfully"
        else:
            tomato.last_cmd_out = out.stdout.decode()
    tomato.state = result.new_state
    ipc_write_status(tomato.config, tomato.state)


def make_tomato(config: Configuration) -> Tomato:
    return Tomato(
        config=config,
        state=InitialState(started_at=cur_time()),
    )
