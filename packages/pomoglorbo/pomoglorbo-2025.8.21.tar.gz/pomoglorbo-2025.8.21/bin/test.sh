#!/usr/bin/env sh
# SPDX-FileCopyrightText: 2023-2025 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

set -e

if ! reuse lint; then
    echo "There was a problem running reuse lint"
    exit 1
fi

echo "reuse lint finished"

if ! ruff format --check .; then
    echo "Formatting with ruff format"
    if ! ruff format .; then
        echo "Failed running ruff format"
        exit 1
    fi
fi

echo "ruff format --check finished"

if ! ruff check .; then
    echo "Attempting to fix with ruff --fix"
    if ! ruff check --fix .; then
        echo "Failed running ruff --fix"
        exit 1
    fi
    if ! ruff check .; then
        echo "There are still some issues. Please fix and run $0 again"
    fi
fi

echo "ruff finished"

if mypy .; then
    echo "mypy finished"
else
    echo "mypy did not finish successfully"
    exit 1
fi

# This test doesn't run inside a Nix build
echo "Checking playsound3 version consistency..."
# Get playsound3 version from Nix expression
NIX_VERSION=$(nix eval .#playsound3.version --raw)

# Get playsound3 version from installed package
INSTALLED_VERSION=$(python -c "from importlib import metadata; print(metadata.version('playsound3'))")

if [ "$NIX_VERSION" = "$INSTALLED_VERSION" ]; then
    echo "playsound3 versions match: $NIX_VERSION"
else
    echo "ERROR: playsound3 version mismatch!"
    echo "playsound3.nix: $NIX_VERSION"
    echo "installed:      $INSTALLED_VERSION"
    exit 1
fi
