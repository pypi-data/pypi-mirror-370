# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

import itertools
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Literal, Union


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
    # config: Configuration

    started_at: int
    progress: Iterator[str] = field(default_factory=lambda: itertools.cycle(PROGRESS))


@dataclass(kw_only=True, frozen=True)
class InitialState(BaseState):
    name = "Ready"
    task: Tasks = Tasks.NO_TASK
    status: TaskStatus = TaskStatus.NONE


@dataclass(kw_only=True, frozen=True)
class WorkingState(BaseState):
    name = "Work mode"
    task = Tasks.WORK
    status = TaskStatus.STARTED
    time_period: int


@dataclass(kw_only=True, frozen=True)
class WorkPausedState(BaseState):
    name = "Paused"
    task = Tasks.WORK
    status = TaskStatus.PAUSED
    prev: WorkingState


@dataclass(kw_only=True, frozen=True)
class SmallBreakState(BaseState):
    name = "Small break"
    task = Tasks.SMALL_BREAK
    status = TaskStatus.STARTED
    time_period: int


@dataclass(kw_only=True, frozen=True)
class LongBreakState(BaseState):
    name = "Long break"
    task = Tasks.LONG_BREAK
    status = TaskStatus.STARTED
    time_period: int


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
