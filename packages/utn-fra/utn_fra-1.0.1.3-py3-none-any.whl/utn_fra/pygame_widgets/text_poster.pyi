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

class TextPoster(Widget):
    def __init__ (self, text:str, screen:object, background_dimentions: tuple[int,int], background_coords: tuple[int,int], font_path: str, font_size:int = 50, color: tuple = (255,0,0), background_color: tuple = (0,0,0), padding: tuple = (20, 20)) -> None:...
    def update_text(self, new_text: str) -> None:...
    def update_dimentions(self, new_dimentions: tuple[int, int]) -> None: ...
    def update_coords(self, new_coords: tuple[int, int]) -> None: ...
    def draw_text(self): ...
    def draw(self) -> None:...
    def update(self) -> None:...