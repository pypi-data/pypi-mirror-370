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
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, screen: pg.Surface, image_path: str, sound_path: str, font_size = 25, on_click = None, on_click_param = None) -> None:
        """
        This function initializes a button object with specified properties such as position, size,
        text, image, sound, and click event handlers.
        
        :param x: The parameter `x` in the `__init__` method represents the x-coordinate position of the
        object on the screen. It is an integer value
        :type x: int
        :param y: The `y` parameter in the `__init__` method represents the vertical position of the
        object on the screen. It determines the distance from the top of the screen to the top of the
        object
        :type y: int
        :param width: The `width` parameter in the `__init__` method represents the width of the button
        that will be created. It is an integer value that determines the horizontal size of the button
        in pixels
        :type width: int
        :param height: The `height` parameter in the `__init__` method represents the height of the
        button that is being created. It is an integer value that determines the vertical size of the
        button on the screen
        :type height: int
        :param text: The `text` parameter in the `__init__` method is a string that represents the text
        content that will be displayed on the button or object you are creating. It is used to set the
        text that will be shown on the button or object in the user interface
        :type text: str
        :param screen: The `screen` parameter in the `__init__` method is expected to be a Pygame
        Surface object. This surface represents the window or screen where the button will be displayed
        and interacted with. It is where the button will be drawn and where user input events will be
        handled
        :type screen: pg.Surface
        :param image_path: The `image_path` parameter in the `__init__` method is a string that
        represents the file path to the image that will be loaded and displayed as the button's visual
        representation
        :type image_path: str
        :param sound_path: The `sound_path` parameter in the `__init__` method is a string that
        represents the path to a sound file. This path is used to load a sound effect associated with
        the object being initialized
        :type sound_path: str
        :param font_size: The `font_size` parameter in the `__init__` method is used to specify the size
        of the font for the text displayed on the button. It is set to a default value of 25 if not
        provided when creating an instance of the class, defaults to 25 (optional)
        :param on_click: The `on_click` parameter in the `__init__` method of your class is used to
        specify a function that should be called when this object is clicked. It allows you to define a
        custom action or behavior for the object when it is clicked by the user
        :param on_click_param: The `on_click_param` parameter in the `__init__` method is used to
        specify any additional parameter that needs to be passed to the `on_click` function when the
        button is clicked. This parameter allows for flexibility in handling different types of button
        clicks by passing specific data or arguments along with
        """
        super().__init__(x, y, text, screen, font_size)
        aux_image = pg.image.load(image_path).convert_alpha()
        self.image = pg.transform.scale(aux_image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.on_click = on_click
        self.on_click_param = on_click_param
        self.click_option_sfx = GameSound()
        self.sound_path = sound_path
        
    
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
                self.click_option_sfx.play_sound(self.sound_path)
                if self.on_click and self.on_click_param:
                    self.on_click(self.on_click_param)
    
    def draw(self) -> None:
        super().draw()
    
    def update(self) -> None:
        """
        The `update` function in Python calls the `draw` and `button_pressed` methods.
        """
        self.draw()
        self.button_pressed()