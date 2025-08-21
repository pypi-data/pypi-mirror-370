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

class ButtonImageSound(Widget):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, screen: pg.Surface, image_path: str, sound_path: str, font_size = 25, on_click = None, on_click_param = None) -> None:...
    def update_text(self, text: str, color: tuple[int,int,int]) -> None:...
    def button_pressed(self) -> None:...
    def draw(self) -> None:...
    def update(self) -> None:...