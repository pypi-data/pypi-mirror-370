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
from .button import Button
from .game_sound import GameSound

class ButtonSound(Button):
    
    def __init__(self, x, y, text, screen, font_path: str, sound_path: str, color: tuple = (255,0,0), font_size = 25, on_click = None, on_click_param = None) -> None:
        """
        This function initializes an object with specified attributes and assigns a sound path.
        
        :param x: The `x` parameter in the `__init__` method represents the x-coordinate position where
        the object will be displayed on the screen
        :param y: The `y` parameter in the `__init__` method is used to specify the vertical position of
        the object on the screen. It determines where the object will be placed along the y-axis
        :param text: The `text` parameter in the `__init__` method is used to specify the text content
        that will be displayed on the button or object being initialized
        :param screen: The `screen` parameter in the `__init__` method is typically used to pass the
        display surface or screen where the button will be rendered. This surface is where the button
        will be drawn and displayed to the user. It allows the button to interact with the screen and
        handle user input such as
        :param font_path: The `font_path` parameter in the `__init__` method is a string that represents
        the file path to the font that will be used for rendering text in the user interface component
        being initialized. This font file will be loaded and used to display the text on the screen
        :type font_path: str
        :param sound_path: The `sound_path` parameter in the `__init__` method is a string that
        represents the path to the sound file that will be associated with the object being initialized.
        This path will be used to load and play the sound when certain actions or events occur within
        the object
        :type sound_path: str
        :param color: The `color` parameter in the `__init__` method is a tuple that represents the RGB
        color values for the text. The default value for `color` is `(255, 0, 0)`, which corresponds to
        the color red in RGB format. You can customize this parameter to
        :type color: tuple
        :param font_size: The `font_size` parameter in the `__init__` method is used to specify the size
        of the font for the text that will be displayed. It determines how big or small the text will
        appear on the screen. The default value for `font_size` is set to 25 if no, defaults to 25
        (optional)
        :param on_click: The `on_click` parameter in the `__init__` method is used to specify a function
        that should be called when the button is clicked. It allows you to define a custom action or
        behavior that should occur when the button is clicked by the user
        :param on_click_param: The `on_click_param` parameter in the `__init__` method is used to
        specify any additional parameter that needs to be passed to the `on_click` function when the
        button is clicked. This allows for flexibility in handling different types of button clicks by
        passing different parameters to the `on_click
        """
        super().__init__(x, y, text, screen, font_path, color, font_size, on_click, on_click_param)
        self.click_option_sfx = GameSound()
        self.sound_path = sound_path
        
    def button_pressed(self) -> None:
        """
        This function checks if a button is pressed and triggers an action when it is clicked.
        """
        mouse_pos = pg.mouse.get_pos()
        
        if self.rect.collidepoint(mouse_pos):
            if pg.mouse.get_pressed()[0] == 1:
                pg.time.delay(300)
                self.click_option_sfx.play_sound(self.sound_path)
                self.on_click(self.on_click_param)
                
    def draw(self) -> None:
        super().draw()
    
    def update(self) -> None:
        """
        The `update` function in Python calls the `draw` and `button_pressed` methods.
        """
        super().update()