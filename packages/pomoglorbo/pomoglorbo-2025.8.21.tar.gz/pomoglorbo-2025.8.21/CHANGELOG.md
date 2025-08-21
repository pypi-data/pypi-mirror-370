---
title: Changelog
---
<!--
SPDX-FileCopyrightText: 2024-2025 Justus Perlwitz

SPDX-License-Identifier: MIT
-->

# Unreleased

- Add an option to send commands to a running Pomoglorbo instance
- Simplify a few modules

# 2025.8.20

- Switch build system to uv
- Add experimental socket server

# 2025.6.13.1

- Update playsound3 dependency in Nix derivation.

# 2025.6.13

- Update playsound3 dependency to 3.2.4 and fix a layout bug
- Clean up and remove unused code
- Update README.md

# 2025.5.31

- Require Python 3.11 as the minimum version
- Vendor in xdg-base-dirs dependency
- Update flake.nix file to use Nix 25.05
- Simplify flake.nix file
- Refactor Nix build and build without poetry2nix
- Update playsound3 to v3
- Update poetry-core

# 2024.11.22

- Decrease poetry2nix package size by removing check dependencies
- Make pyright a dev dependency
- De-factor UI code and improve performance by simplifying rendering thread
- Improve formatting and comments in README.md

# 2024.8.18

- Mark strings for translation using Babel and add translation utility scripts
  in bin/
- Add German translation
- Add basic Japanese translation
- Refactor some of the code used for layout generation
- Improve rendering performance by consolidating text rendering

# 2024.6.23.1

- Add blocking audio play back for TUI (because blocking will stop it from
  rendering)

# 2024.6.23

- Remove `no_clock` and `focus` configuration variables, and `--no-clock` and
  `--focus` CLI arguments. Always show clock, but leave `no_sound` config
  variable `--no-sound` CLI argument, so the sound can still be disabled.
- Halved volume of b15.wav. It was quite loud.
- Removed `volume` config variable.
- Removed `block` boolean argument in `pomoglorbo.core.sound.play()` method

# 2024.06.22a1 (prerelease)

- Swap out pygame for
  [playsound3](https://github.com/sjmikler/playsound3/tree/main).
  Unfortunately, setting the volume is not possible.

# 2024.06.20

- Allow specifying a config file from the CLI. This will take precedence over
  the default XDG_CONFIG_HOME path, or the POMOGLORBO_CONFIG_FILE environment
  variable.
- Clean up and improve help text
- Add back ability to specify audio file (add a test audio file)
- Simplify the way we derive the playback volume
- Fix `--version` returning old value, use importlib.metadata to find out
  current version
- Add useful documentation
- Hide pygame startup message

# 2024.06.19.3

Fixed j/k key not cycling between buttons correctly

# 2024.06.19.2

Fixed up/down key not cycling between buttons correctly
