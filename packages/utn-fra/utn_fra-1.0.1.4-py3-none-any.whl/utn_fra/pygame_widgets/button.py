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

class Button(Widget):
    
    def __init__(self, x, y, text, screen, font_path: str, color: tuple = (255,0,0), font_size = 25, on_click = None, on_click_param = None) -> None:
        """
        This function initializes a text object with specified properties and optional click event
        handlers.
        
        :param x: The `x` parameter in the `__init__` method represents the x-coordinate position where
        the text will be rendered on the screen
        :param y: The `y` parameter in the `__init__` method of the class represents the vertical
        position where the text will be displayed on the screen. It determines the y-coordinate of the
        top-left corner of the text box
        :param text: The `text` parameter in the `__init__` method is used to specify the text that will
        be displayed on the button. It is the text that the user will see on the button when it is
        rendered on the screen
        :param screen: The `screen` parameter in the `__init__` method is typically used to pass the
        display surface where the text will be rendered. This surface is usually created using a library
        like Pygame (`pg` in your code snippet) and represents the area where graphics will be displayed
        :param font_path: The `font_path` parameter in the `__init__` method is a string that represents
        the file path to the font file that will be used for rendering text on the screen. This path
        should point to the location of the font file on your system
        :type font_path: str
        :param color: The `color` parameter in the `__init__` method is a tuple that represents the RGB
        color values for the text that will be rendered on the button. By default, the color is set to
        red (255, 0, 0), but you can customize it by providing a different
        :type color: tuple
        :param font_size: The `font_size` parameter in the `__init__` method is used to specify the size
        of the font that will be used to render the text on the button. It determines how big or small
        the text will appear on the button. The default value for `font_size` is set to, defaults to 25
        (optional)
        :param on_click: The `on_click` parameter in the `__init__` method of your class is used to
        store a function that should be called when this particular object is clicked. It allows you to
        define a custom action or behavior that should occur when the user interacts with the object,
        such as clicking on it
        :param on_click_param: The `on_click_param` parameter in the `__init__` method is used to store
        any additional parameter that needs to be passed to the `on_click` function when the button is
        clicked. This allows for flexibility in handling different types of button clicks by passing
        different parameters to the `on_click
        """
        super().__init__(x, y, text, screen, font_size)
        self.font = pg.font.Font(font_path, self.font_size)
        self.image = self.font.render(self.text, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.on_click = on_click
        self.on_click_param = on_click_param 
    
    def update_text(self, text: str, color: tuple[int,int,int]) -> None:
        self.text = text
        self.image = self.font.render(self.text, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)
        
    def button_pressed(self) -> None:
        """
        This function checks if a button is pressed at the mouse position and triggers a delay before
        executing a specified action.
        """
        mouse_pos = pg.mouse.get_pos()
        
        if self.rect.collidepoint(mouse_pos):
            if pg.mouse.get_pressed()[0] == 1:
                pg.time.delay(300)
                self.on_click(self.on_click_param)
    
    def draw(self) -> None:
        super().draw()
    
    def update(self) -> None:
        """
        The `update` function in Python calls the `draw` and `button_pressed` methods.
        """
        self.draw()
        self.button_pressed()