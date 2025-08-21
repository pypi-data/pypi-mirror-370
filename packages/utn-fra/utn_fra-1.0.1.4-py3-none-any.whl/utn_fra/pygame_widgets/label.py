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

class Label(Widget):
    '''
    This class represents any non interactable text seen on the screen  
    '''
    def __init__ (self,x: int, y:int, text:str, screen:object, font_path: str, font_size:int = 50, color: tuple = (255,0,0))->None:
        """
        This function initializes a text object with specified attributes such as position, text
        content, font style, and color on a screen.
        
        :param x: The `x` parameter in the `__init__` method is an integer representing the x-coordinate
        position where the text will be displayed on the screen
        :param y: The `y` parameter in the `__init__` method is of type `int` and represents the
        vertical position on the screen where the text will be rendered. It is used to specify the
        y-coordinate of the center of the text rectangle
        :param text: The `text` parameter in the `__init__` method is a string that represents the text
        you want to display on the screen. This text will be rendered using the specified font and color
        onto the screen at the specified position (x, y)
        :param screen: The `screen` parameter in the `__init__` method is expected to be an object
        representing the display surface where the text will be rendered. This object is typically
        provided by a Pygame display window or screen object. It is used to render the text onto the
        screen using Pygame's font
        :param font_path: The `font_path` parameter in the `__init__` method is a string that represents
        the file path to the font file that will be used for rendering text. This font file is loaded
        using the `pg.font.Font` method to create a font object for rendering text in the specified font
        :param font_size: The `font_size` parameter in the `__init__` method is used to specify the size
        of the font that will be used to render the text on the screen. It is an optional parameter with
        a default value of 50 if not provided explicitly, defaults to 50
        :param color: The `color` parameter in the `__init__` method is a tuple that represents the RGB
        color values for the text that will be rendered. The default value for the `color` parameter is
        `(255, 0, 0)`, which corresponds to the color red in RGB format
        """
        super().__init__(x, y, text, screen, font_size)
        self.font = pg.font.Font(font_path, self.font_size)
        self.image = self.font.render(self.text, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
    
    def update_text(self, text: str, color: tuple[int,int,int]) -> None:
        self.text = text
        self.image = self.font.render(self.text, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)
        
    def draw(self)->None:
        super().draw()
       
    
    def update(self)->None:
        '''
        Executes the methods that need update 
        Arguments: None
        Returns: None
        '''
        self.draw()
        
  