#!/usr/bin/env sh
# SPDX-FileCopyrightText: 2024-2025 Justus Perlwitz
#
# SPDX-License-Identifier: MIT
# Extract translated strings and put into messages/pomoglorbo.pot
# PO template file
set -e
version="$(uv run src/pomoglorbo/cli.py --version)"
# This is not clean at all
argparse="$(python3 -c 'import argparse; print(repr(argparse)[25:-2])')"
 # REUSE-IgnoreStart
pybabel extract \
    --input-dirs=src,"$argparse"\
    --output-file=src/pomoglorbo/messages/pomoglorbo.pot \
    --project=Pomoglorbo \
    --msgid-bugs-address=justus@jwpconsulting.net \
    --version="$version" \
    --add-location=file \
    --header-comment="# Translations template for Pomoglorbo.
# SPDX-FileCopyrightText: 2024-2025 Justus Perlwitz
# SPDX-License-Identifier: MIT"
# REUSE-IgnoreEnd
