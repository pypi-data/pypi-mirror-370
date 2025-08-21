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


class ImageLabel(Widget):
    def __init__(self, x: int, y: int, text: str, screen, image_path: str, width: int, height: int, font_path: str, font_size: int, color: tuple = (255,0,0)) -> None:...
    def render(self) -> None:...
    def update_text(self, text: str) -> None:...
    def update_image(self, image_path: str) -> None:...
    def set_text(self, text) -> None:...
    def get_text(self) -> str:...
    def update(self, lista_eventos) -> None:...