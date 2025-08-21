#!/usr/bin/env sh
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
# SPDX-License-Identifier: MIT
set -e
bin/pybabel-extract.sh
pybabel update \
    --input-file=src/pomoglorbo/messages/pomoglorbo.pot \
    --output-dir=src/pomoglorbo/messages/ \
    --ignore-pot-creation-date
