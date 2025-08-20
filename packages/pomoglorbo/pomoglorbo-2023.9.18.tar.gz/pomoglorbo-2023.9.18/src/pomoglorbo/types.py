# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

from dataclasses import (
    dataclass,
)
from pathlib import Path
from typing import (
    Literal,
    Optional,
)

from prompt_toolkit.application import Application
from prompt_toolkit.layout import (
    FormattedTextControl,
    Layout,
)

# Possible circular import?
from pomoglorbo.cli.help import HelpContainer

from .core.states import State

OptionalCmd = Optional[list[str]]


@dataclass(kw_only=True, frozen=True)
class Configuration:
    no_clock: bool
    no_sound: bool
    audio_file: bytes
    tomatoes_per_set: int
    work_minutes: float
    small_break_minutes: float
    long_break_minutes: float
    key_bindings: dict[str, str]
    work_state_cmd: OptionalCmd = None
    work_state_cmd_suffix: OptionalCmd = None
    work_paused_state_cmd: OptionalCmd = None
    small_break_state_cmd: OptionalCmd = None
    long_break_state_cmd: OptionalCmd = None
    work_resumed_state_cmd: OptionalCmd = None
    break_over_cmd: OptionalCmd = None

    exit_cmd: OptionalCmd = None
    volume: Optional[float]

    audio_check: bool = False

    state_file: Path


@dataclass
class Tomato:
    state: State
    tomatoes = 0
    sets = 0
    config: Configuration
    last_warning: Optional[str] = None
    last_cmd_out: Optional[str] = None


@dataclass(frozen=True)
class TomatoRender:
    status: str
    text: str
    cmd_out: Optional[str]
    warning: Optional[str]


TomatoInput = Literal[
    "start",
    "pause",
    "reset",
    "reset_all",
    "update",
]


MaybeCommand = Optional[list[str]]


@dataclass(frozen=True)
class TomatoInteraction:
    cmd: MaybeCommand
    play_alarm: bool
    new_state: State
    warning: Optional[str]


@dataclass(frozen=True)
class TomatoLayout:
    layout: Layout
    text_area: FormattedTextControl
    warning_display: FormattedTextControl
    last_cmd_display: FormattedTextControl
    status: FormattedTextControl
    helpwindow: HelpContainer


@dataclass
class UserInterface:
    config: Configuration
    tomato: Tomato
    application: Application[object]
    layout: TomatoLayout
