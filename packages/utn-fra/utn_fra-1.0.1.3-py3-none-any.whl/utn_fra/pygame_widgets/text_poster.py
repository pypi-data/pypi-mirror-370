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
    '''
    This class represents any non interactable text seen on the screen  
    '''
    def __init__ (self, text:str, screen:object, background_dimentions: tuple[int,int], background_coords: tuple[int,int], font_path: str, font_size:int = 50, color: tuple = (255,0,0), background_color: tuple = (0,0,0), padding: tuple = (20, 20))->None:
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
        super().__init__(background_coords[0], background_coords[1], text, screen, font_size)
        self.font = pg.font.Font(font_path, self.font_size)
        self.font_color = color
        self.text_padding = padding
        self.background_dimentions = background_dimentions
        self.background_coords = background_coords
        self.background_color = background_color
        self.__config_surface()
    
    def __create_surface(self) -> dict:
        cuadro = {}
        cuadro['superficie'] = pg.Surface(self.background_dimentions)
        cuadro['rectangulo'] = cuadro.get('superficie').get_rect()
        cuadro['rectangulo'].topleft = self.background_coords
        cuadro['superficie'].fill(pg.Color(self.background_color))
        return cuadro
    
    def __config_surface(self):
        self.background_surface = self.__create_surface()
        self.image = self.background_surface.get('superficie')
        self.rect = self.background_surface.get('rectangulo')
    
    def update_text(self, new_text: str):
        """Update the widget text and fill the surface with background_color
        
        Args:
            new_text: The new text to set
        """
        self.text = new_text
        self.image.fill(pg.Color(self.background_color))
    
    def update_dimentions(self, new_dimentions: tuple[int, int]) -> None:
        """Update the dimentions (size) of the widget
        Args:
            new_dimentions: tuple = The new dimention as a tuple[int, int] to set the widget for width and heigth
        """
        self.background_dimentions = new_dimentions
        self.__config_surface()
    
    def update_coords(self, new_coords: tuple[int, int]) -> None:
        """Update the coords of the widget
        Args:
            new_coords: tuple = The new coords as a tuple[int, int] to set the widget for the left-upper corner
        """
        self.x = new_coords[0]
        self.y = new_coords[1]
        self.background_coords = new_coords
        self.__config_surface()
    
    def draw_text(self):
        """Draw the text into the main surface"""
        words = []
        
        for word in self.text.splitlines():
            words.append(word.split(' '))
        
        space = self.font.size(' ')[0]
        ancho_max, alto_max = self.background_surface.get('superficie').get_size()
        x, y = self.text_padding
        for line in words:
            for word in line:
                word_surface = self.font.render(word, False, self.font_color)
                ancho_palabra, alto_palabra = word_surface.get_size()
                if x + ancho_palabra >= ancho_max:
                    x = self.text_padding[0]
                    y += alto_palabra
                self.background_surface.get('superficie').blit(word_surface, (x, y))
                x += ancho_palabra + space
            x = self.text_padding[0]
            y += alto_palabra
    
    def draw(self):
        self.draw_text()
        self.screen.blit(self.image, self.rect.topleft)
    
    def update(self):
        pass