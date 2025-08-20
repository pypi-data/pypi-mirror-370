# SPDX-FileCopyrightText: 2021-2023 Bhatihya Perera
# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

import argparse
import ast
import configparser
import os
import pathlib
from dataclasses import replace

from xdg_base_dirs import xdg_config_home, xdg_state_home

from pomoglorbo.core.util import in_app_resource
from pomoglorbo.types import Configuration

from ..const import VERSION

# File is located in '~/.config/pomoglorbo/config.ini' or the location
# specified by POMOGLORBO_CONFIG_FILE environment variable
CONFIG_PATH = pathlib.Path(
    os.environ.get(
        "POMOGLORBO_CONFIG_FILE", xdg_config_home() / "pomoglorbo/config.ini"
    )
)
STATE_FILE_PATH = pathlib.Path(xdg_state_home() / "pomoglorbo" / "state.pomoglorbo")


def get_argument_parser() -> argparse.ArgumentParser:
    """Create argument parser."""

    parser = argparse.ArgumentParser(
        "pomoglorbo", description="Terminal Pomodoro Timer"
    )
    parser.add_argument(
        "--focus",
        help="focus mode: hides clock and \
                        mutes sounds (equivalent to --no-clock and --no-sound)",
        action="store_true",
    )
    parser.add_argument("--no-clock", help="hides clock", action="store_true")
    parser.add_argument("--no-sound", help="mutes all sounds", action="store_true")
    parser.add_argument(
        "--audio-check", help="play audio and exit", action="store_true"
    )
    parser.add_argument(
        "-v",
        "--version",
        help="display version and exit",
        action="version",
        version=VERSION,
    )
    parser.add_argument("--audio-file", metavar="path", help="custom audio file")
    parser.add_argument(
        "--work-state-cmd-suffix",
        nargs="+",
        help="arguments to append to every command invocation",
    )
    return parser


def create_default_ini(conf: configparser.ConfigParser) -> None:
    """Creates default ini configuration file."""
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    with CONFIG_PATH.open("w+") as configfile:
        conf.write(configfile)


def ini_parse(conf: configparser.ConfigParser) -> None:
    """Parse configuration file."""
    if not CONFIG_PATH.exists():
        create_default_ini(conf)
    conf.read(CONFIG_PATH)


def get_config_parser() -> configparser.ConfigParser:
    """Create configuration parser."""
    conf = configparser.ConfigParser()
    conf["DEFAULT"] = {}

    conf["General"] = {
        "no_clock": "false",
        "no_sound": "false",
        "audio_file": "",
        # We do not give volume here because getfloat does not like that
        # We want the default to be None
        # "volume": "",
    }
    conf["Ipc"] = {}

    conf["Time"] = {
        "tomatoes_per_set": "4",
        "work_minutes": "25",
        "small_break_minutes": "5",
        "long_break_minutes": "15",
    }

    conf["KeyBindings"] = {
        "focus_previous": "s-tab,left,h,j",
        "focus_next": "tab,right,l,k",
        "exit_clicked": "q",
        "start": "s",
        "pause": "p",
        "reset": "r",
        "reset_all": "a",
        "help": "?,f1",
    }

    conf["Trigger"] = {
        "work_state_cmd": "None",
        "work_paused_state_cmd": "None",
        "work_resumed_state_cmd": "None",
        "long_break_state_cmd": "None",
        "small_break_state_cmd": "None",
        "break_over_cmd": "None",
        "exit_cmd": "None",
    }

    return conf


def parse_configuration() -> Configuration:
    """Parse configuration from ini file."""
    conf = get_config_parser()
    ini_parse(conf)
    return Configuration(
        no_clock=conf.getboolean("General", "no_clock"),
        no_sound=conf.getboolean("General", "no_sound"),
        audio_file=in_app_resource("b15.wav"),
        volume=conf.getfloat("General", "volume", fallback=None),
        state_file=pathlib.Path(
            conf.get("Ipc", "state_file", fallback=STATE_FILE_PATH)
        ),
        tomatoes_per_set=conf.getint("Time", "tomatoes_per_set"),
        work_minutes=conf.getfloat("Time", "work_minutes"),
        small_break_minutes=conf.getfloat("Time", "small_break_minutes"),
        long_break_minutes=conf.getfloat("Time", "long_break_minutes"),
        key_bindings={
            "focus_previous": conf.get("KeyBindings", "focus_previous"),
            "focus_next": conf.get("KeyBindings", "focus_next"),
            "exit_clicked": conf.get("KeyBindings", "exit_clicked"),
            "start": conf.get("KeyBindings", "start"),
            "pause": conf.get("KeyBindings", "pause"),
            "reset": conf.get("KeyBindings", "reset"),
            "reset_all": conf.get("KeyBindings", "reset_all"),
            "help": conf.get("KeyBindings", "help"),
        },
        work_state_cmd_suffix=ast.literal_eval(
            conf.get("Trigger", "work_state_cmd_suffix", fallback="None")
        ),
        work_state_cmd=ast.literal_eval(conf.get("Trigger", "work_state_cmd")),
        work_paused_state_cmd=ast.literal_eval(
            conf.get("Trigger", "work_paused_state_cmd")
        ),
        small_break_state_cmd=ast.literal_eval(
            conf.get("Trigger", "small_break_state_cmd")
        ),
        long_break_state_cmd=ast.literal_eval(
            conf.get("Trigger", "long_break_state_cmd")
        ),
        work_resumed_state_cmd=ast.literal_eval(
            conf.get("Trigger", "work_resumed_state_cmd")
        ),
        break_over_cmd=ast.literal_eval(conf.get("Trigger", "break_over_cmd")),
        exit_cmd=ast.literal_eval(conf.get("Trigger", "exit_cmd")),
    )


def cli_load(
    configuration: Configuration,
) -> Configuration:
    """
    Loads the command line arguments

    Command line arguments override file configurations.
    """
    cli_args = get_argument_parser().parse_args()
    return replace(
        configuration,
        no_clock=(cli_args.no_clock or cli_args.focus or configuration.no_clock),
        no_sound=(cli_args.no_sound or cli_args.focus or configuration.no_sound),
        work_state_cmd_suffix=cli_args.work_state_cmd_suffix or [],
        audio_check=cli_args.audio_check,
        # TODO add back support for cli_args.audio_file or configuration.audio_file
        # audio_file=,
    )


def create_configuration() -> Configuration:
    config = parse_configuration()
    config = cli_load(config)
    return config
