<!--
SPDX-FileCopyrightText: 2023 Justus Perlwitz
SPDX-FileCopyrightText: 2024 Justus Perlwitz
SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera

SPDX-License-Identifier: MIT
-->

Links: [PyPI](https://pypi.org/project/pomoglorbo/)
[Codeberg](https://codeberg.org/justusw/Pomoglorbo)

# Pomoglorbo

A Pomodoro Technique timer for your terminal! Runs over SSH! A bell rings
when your Pomodoro is over!

_muuuuuust haaaaaaaveeeeee_

![A screenshot of Pomoglorbo running in alacritty on
macOS](docs/pomoglorbo.png)

But what are Pomodoros? And why would I run this in my terminal? Read my [blog
post about
Pomoglorbo](https://www.justus.pw/posts/2024-06-18-try-pomoglorbo.html) for
more info.

## Installation

__Recommended__: Install using
[pipx](https://pipx.pypa.io/stable/#install-pipx):

```bash
pipx install pomoglorbo
```

Then run using

```bash
pomoglorbo
```

You can also install using `pip`, if you don't mind clobbering packages:

```bash
pip3 install --user pomoglorbo
```

### With Nix

For [NixOS](https://nixos.org/) or [Home
Manager](https://nix-community.github.io/home-manager/) users, you can also use
and install Pomoglorbo as a [Nix
Flake](https://hydra.nixos.org/build/263397466/download/1/manual/command-ref/new-cli/nix3-flake.html#description).

The easiest way is to use `nix run` with this Codeberg repository:

```bash
nix run git+https://codeberg.org/justusw/Pomoglorbo.git
```

If you want to pass additional arguments, append a `--` argument separator
first, and you are good to go:

```bash
nix run git+https://codeberg.org/justusw/Pomoglorbo.git -- --audio-check
```

It's almost a bit too magical. Reproducible builds? Builds on
many different systems? _whooooosh_ Nix is the cave allegory of build systems.

This is how you can add it to your Home Manager configuration, if you use [Nix
Flakes with Home
Manager](https://nix-community.github.io/home-manager/index.xhtml#ch-usage):

```nix
{
  description = "My awesome nix home manager configuration";

  inputs = {
    # Make sure that you use the latest supported version of the NixOS packages
    # here
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    pomoglorbo = {
      url = "git+https://codeberg.org/justusw/Pomoglorbo.git";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, pomoglorbo }: {
    # do what you must here
  };
}
```

How to evaluate package size:

```bash
nix run github:utdemir/nix-tree -- --derivation .#pomoglorbo
# Or, if you are inside a Nix shell for this repository's Nix flake, run
nix-tree --derivation .#pomoglorbo
```

Do you want to know more about Nix Flakes? I recommend these posts by Xe Iaso:

- [Nix Flakes: an
Introduction](https://xeiaso.net/blog/nix-flakes-1-2022-02-21/)
- [Building Go programs with Nix
Flakes](https://xeiaso.net/blog/nix-flakes-go-programs/)

## Usage

See `pomoglorbo --help` for a complete overview of available options. At the
time of writing, these are all available flags:

<!--
uv run src/pomoglorbo/cli.py --help | sed -n -E -e 's/^  (.+)/\1/p'
-->

```
usage: pomoglorbo [-h] [--no-sound] [--audio-check] [-v] [--audio-file path] [--config-file path] [--work-state-cmd-suffix suffix [suffix ...]] [command]

Pomoglorbo: TUI Pomodoro Technique Timer

positional arguments:
  command               Send command to running pomoglorbo instance via IPC

options:
  -h, --help            show this help message and exit
  --no-sound            Mute alarm
  --audio-check         Play alarm and exit
  -v, --version         Display version and exit
  --audio-file path     Custom audio file for alarm
  --config-file path    Use a different config file. Overrides POMOGLORBO_CONFIG_FILE environment variable. Default is "$XDG_CONFIG_HOME/pomoglorbo/config.ini".
  --work-state-cmd-suffix suffix [suffix ...]
                        Append these arguments to external command invocation when starting the next Pomodoro
```

## Configure Pomoglorbo

A configuration file is automatically created in
`$XDG_CONFIG_HOME/pomoglorbo/config.ini` when you launch Pomoglorbo. You can
customize how Pomoglorbo behaves. The default configuration can be found in
`src/pomoglorbo/core/config.py` under `DEFAULT_CONFIG`.

### Use a different audio file

Set the following in your `config.ini` file:

```ini
[General]
audio_file = path/to/your/audio/file.ogg
```

or run Pomoglorbo with the following flag:

```bash
pomoglorbo --audio-file path/to/your/audio/file.ogg
```

If you want to just check whether the sound plays correctly, add the
`--audio-check` flag as well.

```bash
pomoglorbo --audio-file path/to/your/audio/file.ogg --audio-check
```

### Change Pomodoro intervals

The duration of work and break times can be set using the following variables
in your configuration file:

```ini
[Time]
# How many tomatoes need to elapse to get to a long break
tomatoes_per_set = 4
# Duration of a single pomodoro in minutes
work_minutes = 25
# Duration of a short break between Pomodoros in minutes
small_break_minutes = 5
# Duration of a long break after a set, in minutes
long_break_minutes = 15
```

### Change key bindings

The default key bindings are:

<!-- Please update me if needed -->

- Focus previous: shift-tab, up, left, h, or k
- Focus next: tab, right, down, l, or j
- Exit: q
- Start: s
- Pause: p
- Reset: r
- Reset all: a
- Help: ? or f1

While Pomoglorbo is running, you can always review the current keybindings
by opening the help menu. You can open the help menu by pressing `?` or F1

You can customize Pomoglorbo TUI key bindings using the following configuration
variables, illustrated with some examples values:

```ini
[KeyBindings]
# Focus on previous button in TUI
focus_previous = s-tab
# Focus on next button in TUI
focus_next = tab
# Quit Pomoglorbo
exit_clicked = q
# Start the next Pomodoro or break
start = s
# Pause the current Pomodoro or break
pause = p
# Reset elapsed time of current Pomodoro or break
reset = r
# Reset elapsed time, go back to 0 elapsed Pomodoros (see tomatoes_per_set)
reset_all = a
# Show current key bindings
help = ?
```

You can find more documentation on keybindings on `prompt_toolkit`s documentation
site
[here](https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html#list-of-special-keys).

### Run a command when something happens (Triggers)

You can configure Pomoglorbo to execute a command for you automatically when
one of the following things happens:

- A new Pomodoro is started
- A Pomodoro is paused
- A Pomodoro is resumed
- A long break is started
- A short break is started
- A break is over
- Pomoglorbo exits

The commands can be given as string array-like string in the configuration file
section `Trigger`. A good use case for this is automatically starting time
tracking in time tracking software like
[Timewarrior](https://timewarrior.net/). Here are some ideas on what you can
put in each command.

```ini
[Trigger]
work_state_cmd = ["curl", "https://example.com"]
work_paused_state_cmd = ["timew", "stop"]
work_resumed_state_cmd = ["timew", "start"]
long_break_state_cmd = ["i3lock"]
small_break_state_cmd = ["timew", "start", "break"]
break_over_cmd = ["timew", "stop"]
exit_cmd = ["espeak", "bye"]
```

*Note from Justus*: But that's not all! Here's something I do a lot. When I
start Pomoglorbo, I want it to start Timewarrior with a specific tag. The work
state command is `timew start`, which would start time tracking without any
tags. I can then add `--work-state-cmd-suffix` when calling Pomoglorbo like so:

```bash
pomoglorbo --work-state-cmd-suffix development pomoglorbo
```

Pomoglorbo will call `timew` for me when the next Pomodoro starts like so:

```bash
timew start development pomoglorbo
```

This could be extended to the other commands as well, if required. Patches are
very welcome here.

## Development

To start developing Pomoglorbo this, clone this repository from Codeberg:

```bash
git clone https://codeberg.org/justusw/Pomoglorbo.git
```

Use [uv](https://docs.astral.sh/uv/getting-started/installation/) to install all
dependencies:

```bash
# This will install packages used for testing as well
uv sync
```

Run Pomoglorbo inside the uv virtual environment using the following
command:

```bash
uv run src/pomoglorbo/cli.py
```

You can additionally specify a configuration file to be used like so:

```bash
uv run src/pomoglorbo/cli.py --config-file test/config.ini
```

### Testing

Run all tests and formatters using

```bash
uv run bin/test.sh
```

Format code using

```bash
uv run bin/format.sh
```

### Translations

Provided you installed all dependencies with uv,
you can translate strings like so:

__Mark a string for translation__: If you want to mark a string for
translation, you have to mark it using
[gettext](https://docs.python.org/3/library/gettext.html). For example, if you
want to print the string "Hello, World!" and automatically translate it, write
the following:

```python
# Assuming this file is called source_file.py
from pomoglorbo.cli.util import gettext_lazy as _
print(_("Hello, World!))
```

We use our own `gettext_lazy` here (similar to Django), to make sure that
strings are not translated at module import time.

__Extract strings__: Run

```bash
bin/pybabel-update.sh
```

This will populate all message catalogs for the languages in
`src/pomoglorbo/messages/`. You will see a new string added to each `.po`
file and the `.pot` file. Edit the new message and translate it. Here, we
translate it into German.

```po
#: source_file.py
msgid "Hello, World!"
msgstr "Hallo, Welt!"
```

__Compile message catalogs__: Now, you have to compile the translations into MO
files.

```bash
bin/pybabel-compile.sh
```

And you are done.

The translation uses GNU Gettext, the Python `gettext` module and
[Babel](https://babel.pocoo.org/en/latest/index.html). Refer to Babel's
[Command-Line Interface help](https://babel.pocoo.org/en/latest/cmdline.html)
to learn more about how the `bin/pybabel-*.sh` commands work.

## Sending commands to Pomoglorbo

If you have a running Pomoglorbo instance with the socket server enabled, you
can send commands directly using:

```bash
pomoglorbo start # Start next Pomodoro
pomoglorbo pause # Pause current timer
pomoglorbo reset # Reset current timer
pomoglorbo reset_all # Reset Pomoglorbo start
```

## Experimental socket server

Pomoglorbo includes an experimental Unix domain socket server that lets you
control Pomoglorbo from other programs.

### How to enable the socket server

Enable the socket server by adding the following to your Pomoglorbo
configuration:

```ini
[Ipc]
socket_server = True
```

When you've enabled the socket server, Pomoglorbo creates a Unix domain socket
at `$XDG_STATE_HOME/pomoglorbo/socket`. In most cases, this should be
`~/.local/state/pomoglorbo/socket`.

### Commands that you can use

The socket server accepts the following text commands:

- `start` - Start the next Pomodoro
- `pause` - Pause the current timer
- `reset` - Reset the current timer
- `reset_all` - Reset all progress

Each command returns a response:
- `OK: <command>` - This lets you to know that Pomoglorbo accepted your command
- `ERROR: Unknown command '<command>'` - Pomoglorbo could not process your
  command

### How to use the socket server

You can interact with the socket using the `socat` command:

```bash
echo "start" | socat - UNIX-CONNECT:"$XDG_STATE_HOME/pomoglorbo/socket"
```

You can also send these commands by running `pomoglorbo [COMMAND]`, where
`[COMMAND]` is one of the accepted text commands `start`, `pause`, `reset`, or
`reset_all`.

For more information on how to use the `pomoglorbo [COMMAND]` feature, see the
**Sending commands to Pomoglorbo** section

## Contributing

Would you like to make a contribution? Your ideas are very welcome as this is
an open source project welcoming all contributors! Please read the
[CONTRIBUTING.md](CONTRIBUTING.md) file for more info. Please also refer to the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Credits

Pomoglorbo is a fork of the original
[pydoro](https://github.com/JaDogg/pydoro).

- [pydoro](https://github.com/JaDogg/pydoro) - by Bhathiya Perera
- Pomodoro - Invented by Francesco Cirillo
- prompt-toolkit - Awesome TUI library
- b15.wav - [Dana](https://freesound.org/s/377639/) robinson designs,
  CC0 from freesound

See the `CONTRIBUTORS` file in the root directory for a list of contributors to
the original pydoro project.

## Copyright

See the LICENSES folder for more information.
