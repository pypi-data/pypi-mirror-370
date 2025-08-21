#!/usr/bin/env sh
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
# SPDX-License-Identifier: MIT
set -e
for lang in de ja; do
    pybabel init \
        --input-file=src/pomoglorbo/messages/pomoglorbo.pot \
        --output-dir=src/pomoglorbo/messages/ \
        --locale="$lang"
done
