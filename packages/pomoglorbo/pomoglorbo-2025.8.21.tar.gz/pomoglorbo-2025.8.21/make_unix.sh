#!/bin/bash

# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
#
# SPDX-License-Identifier: MIT

pyinstaller -F pomoglorbo_tui.py -n pomoglorbo --add-data "./pomoglorbo/core/b15.wav:." --add-data "./.venv/lib/python3.7/site-packages/wcwidth:wcwidth" --hidden-import="pkg_resources.py2_warn"

