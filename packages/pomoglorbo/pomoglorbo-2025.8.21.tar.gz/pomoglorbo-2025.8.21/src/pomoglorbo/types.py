# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023-2025 Justus Perlwitz
#
# SPDX-License-Identifier: MIT
import itertools
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from gettext import gettext as _
from pathlib import Path
from typing import (
    Literal,
    Optional,
    TypedDict,
    Union,
)

from prompt_toolkit.layout import (
    Container,
    FormattedTextControl,
    Layout,
)

OptionalCmd = Optional[list[str]]


KeyBindingsCfg = TypedDict(
    "KeyBindingsCfg",
    {
        "focus_previous": str,
        "focus_next": str,
        "exit_clicked": str,
        "start": str,
        "pause": str,
        "reset": str,
        "reset_all": str,
        "help": str,
    },
)


@dataclass(kw_only=True, frozen=True)
class Configuration:
    no_sound: bool
    audio_file: Optional[Path]
    tomatoes_per_set: int
    work_minutes: float
    small_break_minutes: float
    long_break_minutes: float
    key_bindings: KeyBindingsCfg
    work_state_cmd: OptionalCmd = None
    work_state_cmd_suffix: OptionalCmd = None
    work_paused_state_cmd: OptionalCmd = None
    small_break_state_cmd: OptionalCmd = None
    long_break_state_cmd: OptionalCmd = None
    work_resumed_state_cmd: OptionalCmd = None
    break_over_cmd: OptionalCmd = None

    exit_cmd: OptionalCmd = None

    audio_check: bool = False
    send_command: Optional[str] = None

    state_file: Path
    socket_server: bool


# Pomoglorbo app states
class Tasks(IntEnum):
    WORK = 1
    SMALL_BREAK = 2
    LONG_BREAK = 3
    NO_TASK = 4


class TaskStatus(IntEnum):
    NONE = 111
    STARTED = 222
    PAUSED = 555


# Animation to show when pomodoro is active
PROGRESS = ["|#  |", "| # |", "|  #|", "| # |"]


@dataclass(frozen=True)
class BaseState:
    started_at: datetime
    progress: Iterator[str] = field(default_factory=lambda: itertools.cycle(PROGRESS))


@dataclass(kw_only=True, frozen=True)
class InitialState(BaseState):
    name = _("Ready")
    task: Tasks = Tasks.NO_TASK
    status: TaskStatus = TaskStatus.NONE


@dataclass(kw_only=True, frozen=True)
class WorkingState(BaseState):
    name = _("Work mode")
    task = Tasks.WORK
    status = TaskStatus.STARTED
    time_period: timedelta


@dataclass(kw_only=True, frozen=True)
class WorkPausedState(BaseState):
    name = _("Paused")
    task = Tasks.WORK
    status = TaskStatus.PAUSED
    prev: WorkingState


@dataclass(kw_only=True, frozen=True)
class SmallBreakState(BaseState):
    name = _("Small break")
    task = Tasks.SMALL_BREAK
    status = TaskStatus.STARTED
    time_period: timedelta


@dataclass(kw_only=True, frozen=True)
class LongBreakState(BaseState):
    name = _("Long break")
    task = Tasks.LONG_BREAK
    status = TaskStatus.STARTED
    time_period: timedelta


State = Union[
    InitialState,
    WorkingState,
    WorkPausedState,
    SmallBreakState,
    LongBreakState,
]


RunningState = Union[WorkingState, SmallBreakState, LongBreakState]
RunningStateLiteral = Literal["working", "small-break", "long-break"]
PausedState = WorkPausedState


@dataclass
class Tomato:
    state: State
    tomatoes = 0
    sets = 0
    config: Configuration
    show_help: bool
    last_warning: Optional[str] = None
    last_cmd_out: Optional[str] = None


@dataclass(frozen=True)
class TomatoRender:
    text: str
    show_help: bool


TomatoInput = Literal[
    "start",
    "pause",
    "reset",
    "reset_all",
    "update",
    "toggle_help",
]


MaybeCommand = Optional[list[str]]


@dataclass(frozen=True)
class TomatoInteraction:
    cmd: MaybeCommand
    play_alarm: bool
    new_state: State
    warning: Optional[str]
    show_help: Optional[bool]


@dataclass(frozen=True)
class TomatoLayout:
    layout: Layout
    text_area: FormattedTextControl
    warning_display: FormattedTextControl
    last_cmd_display: FormattedTextControl
    status: FormattedTextControl
    helpwindow: Container
