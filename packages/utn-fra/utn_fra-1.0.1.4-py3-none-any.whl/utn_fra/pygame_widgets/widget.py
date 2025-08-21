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

class Widget:
    
    def __init__(self, x: int, y: int, text: str, screen, font_size: int = 25) -> None:
        self.x = x
        self.y = y
        self.text = text
        self.screen = screen
        self.font_size = font_size
    
    def draw(self) -> None:
        """
        The `draw` function in the given Python code snippet blits an image onto a screen at the
        specified coordinates.
        """
        self.screen.blit(self.image, (self.rect.x, self.rect.y))
    
    def update(self) -> None:
        """
        The `update` function calls the `draw` method.
        """
        self.draw()
