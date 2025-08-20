# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

from typing import (
    Callable,
    Optional,
)

from prompt_toolkit.key_binding import (
    KeyBindings,
    KeyPressEvent,
)

from pomoglorbo.types import Configuration

EventCallback = Callable[[KeyPressEvent], None]


Actions = dict[str, EventCallback]


def get_key_bindings(
    config: Configuration,
    actions: Actions,
) -> KeyBindings:
    kb = KeyBindings()
    for action, keys in config.key_bindings.items():
        cb: Optional[EventCallback] = actions.get(action)
        if not cb:
            continue
        for key in keys.split(","):
            key = key.strip()
            kb.add(key)(cb)
    return kb
