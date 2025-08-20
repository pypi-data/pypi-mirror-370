# SPDX-FileCopyrightText: 2023 Justus Perlwitz
# SPDX-FileCopyrightText: 2024 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

from time import sleep
from typing import Optional

import pygame

pygame.mixer.init()


def play(buffer: bytes, volume: Optional[float] = None, block: bool = True) -> None:
    sound = pygame.mixer.Sound(buffer=buffer)
    if volume:
        sound.set_volume(volume)
    sound.play()
    if not block:
        return
    while pygame.mixer.get_busy():
        sleep(0.1)
