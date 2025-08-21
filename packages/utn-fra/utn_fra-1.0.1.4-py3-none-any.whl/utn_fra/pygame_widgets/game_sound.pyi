# Copyright (C) 2025 <UTN FRA>
#
# Author: Facundo Falcone <f.falcone@sistemas-utnfra.com.ar>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygame.mixer as mixer

class GameSound:
    def __init__(self):...
    def play_sound(self, sound_path: str, volume: float = 0.8) -> None:...
    def play_music(self, music_path: str, volume: float = 0.5, fade_ms: int = 3000, loop: bool = True) -> None:...
    def stop_music(self) -> None:...