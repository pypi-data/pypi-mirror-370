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
from datetime import datetime, timedelta

from pomoglorbo.types import (
    Configuration,
    InitialState,
    LongBreakState,
    MaybeCommand,
    RunningState,
    SmallBreakState,
    Tomato,
    TomatoInput,
    TomatoInteraction,
    WorkingState,
    WorkPausedState,
)
from pomoglorbo.util import calc_remainder, play


def state_done(state: RunningState) -> bool:
    """Return if state is done."""
    return calc_remainder(state).total_seconds() <= 0


def _tomato_interact(tomato: Tomato, input: TomatoInput) -> TomatoInteraction:
    config = tomato.config
    maybe_cmd: MaybeCommand = None
    play_alarm = False
    warning = None
    show_help = None
    match (input, tomato.state):
        case "toggle_help", _:
            show_help = not tomato.show_help
            state = tomato.state
        case "start", SmallBreakState() | LongBreakState() | InitialState() as state:
            play_alarm = True
            if cmd := config.work_state_cmd:
                maybe_cmd = cmd + (tomato.config.work_state_cmd_suffix or [])
            state = WorkingState(
                started_at=datetime.now(),
                time_period=timedelta(minutes=config.work_minutes),
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
            state = WorkPausedState(prev=state, started_at=datetime.now())
        case "pause", state:
            warning = "Can't pause here"
        case "reset", WorkingState() | SmallBreakState() | LongBreakState() as state:
            state = replace(state, started_at=datetime.now())
        case "reset", WorkPausedState(prev=prev) as state:
            state = replace(state, prev=replace(prev, started_at=datetime.now()))
        case "reset", state:
            warning = "Can't reset here"
        case "reset_all", _:
            state = InitialState(started_at=datetime.now())
            tomato.tomatoes = 0
        case "update", WorkingState() as running_state if state_done(running_state):
            play_alarm = True
            tomato.tomatoes += 1
            is_end_of_set = tomato.tomatoes % tomato.config.tomatoes_per_set == 0
            if is_end_of_set:
                tomato.sets += 1
                state = LongBreakState(
                    time_period=timedelta(minutes=config.long_break_minutes),
                    started_at=datetime.now(),
                )
                maybe_cmd = config.long_break_state_cmd
            else:
                state = SmallBreakState(
                    time_period=timedelta(minutes=config.small_break_minutes),
                    started_at=datetime.now(),
                )
                maybe_cmd = config.small_break_state_cmd
        case "update", SmallBreakState() | LongBreakState() as state if state_done(
            state
        ):
            play_alarm = True
            state = InitialState(started_at=datetime.now())
            maybe_cmd = config.break_over_cmd
        case "update", state:
            pass  # no op
    return TomatoInteraction(
        new_state=state,
        cmd=maybe_cmd,
        play_alarm=play_alarm,
        warning=warning,
        show_help=show_help,
    )


def tomato_interact(tomato: Tomato, input: TomatoInput) -> None:
    result = _tomato_interact(tomato, input)
    if result.play_alarm and not tomato.config.no_sound:
        play(tomato.config.audio_file, block=False)
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
    if result.show_help is not None:
        tomato.show_help = result.show_help


def make_tomato(config: Configuration) -> Tomato:
    return Tomato(
        config=config,
        state=InitialState(started_at=datetime.now()),
        show_help=False,
    )
