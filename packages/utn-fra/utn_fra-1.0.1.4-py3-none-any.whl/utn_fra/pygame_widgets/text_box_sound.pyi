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

import pygame as pg
from .widget import Widget
from .game_sound import GameSound
import random as rd

class TextBoxSound(Widget):
    def __init__(self, x, y, text, screen, sound_path: str, font_path: str, font_size = 25, color: tuple = (255,0,0), sounds_list_path: list = None, on_click = None, on_click_param = None) -> None:...
    def write_on_box(self, event_list: list) -> None:...
    def update_text(self, new_text: str) -> None: ...
    def draw(self) -> None:...
    def update(self, event_list: list) -> None:...