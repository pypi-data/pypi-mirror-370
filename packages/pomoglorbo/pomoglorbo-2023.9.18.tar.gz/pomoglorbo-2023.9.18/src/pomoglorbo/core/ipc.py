# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

"""
Functionality for IPC.

With this, we can let other programs know what we are up to by writing into
a file our current status.
"""

from pomoglorbo.core.util import calc_remainder, format_time

from ..types import Configuration
from . import states


def ipc_write_status(config: Configuration, state: states.State) -> None:
    """Write to our state file."""
    state_file = config.state_file
    if not state_file.parent.exists():
        state_file.parent.mkdir(parents=True)
    match state:
        case states.WorkingState() | states.LongBreakState() | states.SmallBreakState():
            remainder = calc_remainder(state)
            content = f"""{format_time(state, remainder, "plain")}"""
        case states.PausedState():
            content = "paused"
        case states.InitialState():
            content = "ready"
    with open(state_file, "w") as fd:
        fd.write(f"Pomoglorbo: {content}")
