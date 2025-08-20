# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
#
# SPDX-License-Identifier: MIT

from prompt_toolkit.application.current import get_app


def exit_clicked() -> None:
    get_app().exit()
