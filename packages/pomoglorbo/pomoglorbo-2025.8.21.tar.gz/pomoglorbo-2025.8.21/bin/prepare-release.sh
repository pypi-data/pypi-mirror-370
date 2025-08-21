#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT
# Prepare a new version to release
set -e

version="$(date +%Y.%-m.%-d)"
read -p "about to set version to '$version'. Continue? (c-c to exit)"
sed -i "s/^version = \".*\"/version = \"$version\"/" pyproject.toml
sed -i "s/version = \".*\";/version = \"$version\";/" build.nix
echo "set version to $version in pyproject.toml and build.nix"

read -p "about to commit pyproject.toml, uv.lock, and build.nix. Continue? (c-c to exit)"
git add pyproject.toml uv.lock build.nix
git commit -m "Bump version to $version"

read -p "committed pyproject.toml, uv.lock and build.nix. Continue? (c-c to exit)"

echo "running uv sync"
uv sync

version="$(uv run src/pomoglorbo/cli.py --version)"
echo "version read back from package is: $version"

read -p "about to run git tag $version. Continue? (c-c to exit)"
git tag "$version"

echo "Running uv build"
uv build

read -p "about to run uv publish. Continue? (c-c to exit)"
uv publish

read -p "about to run git push --tags. Continue? (c-c to exit)"
git push --tags
