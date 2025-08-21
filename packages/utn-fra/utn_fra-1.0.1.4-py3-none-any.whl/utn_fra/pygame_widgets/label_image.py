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
    
    def __init__(self, x: int, y: int, text: str, screen, image_path: str, width: int, height: int, font_path: str, font_size: int, color: tuple = (255,0,0)) -> None:
        """
        This function initializes a text object with specified properties such as position, text
        content, font style, color, and background image.
        
        :param x: The `x` parameter is used to specify the x-coordinate
        position of the object on the screen. It determines where the object will be placed horizontally
        :param y: The parameter `y` represents the y-coordinate position of the
        object on the screen. It determines the vertical position where the object will be rendered
        :param text: The `text` parameter is a string that represents the text
        content that will be displayed on the screen
        :param screen: The `screen` parameter is typically used to pass the
        display surface where the text will be rendered. This surface is usually created using a
        graphics library like Pygame (`pg` in your code snippet). The text will be displayed on this
        screen surface at the specified
        :param image_path: The `image_path` parameter is a string that
        represents the path to the image file that will be used as the background for the object being
        initialized. This path should point to the location of the image file on the system where the
        code is running
        :param width: The `width` parameter represents the width of the object
        you are creating. It is an integer value that determines the horizontal size of the object on
        the screen
        :param height: The `height` parameter represents the height of the
        object being initialized. It is an integer value that determines the vertical size of the object
        on the screen
        :param font_path: The `font_path` parameter is a string that represents
        the file path to the font file that will be used for rendering text in the graphical user
        interface. This font file will be loaded by the Pygame library to render text on the screen with
        the specified font
        :param font_size: The `font_size` parameter is used to specify the size
        of the font that will be used to render the text on the screen. It is an integer value
        representing the font size in points
        :param color: The `color` parameter is a tuple representing the RGB
        color values. By default, it is set to `(255, 0, 0)`, which corresponds to the color red. You
        can customize this parameter to set a different color for the text rendered
        """
        super().__init__(x, y, text, screen, font_size)

        self.font = pg.font.Font(font_path, self.font_size)
        self.font_color = color
        self.width = width
        self.height = height
        
        self.__set_background(image_path)
        self.img_original = self.image.copy()

        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y

        self.render()

    def __set_background(self, image_path: str) -> None:
        """
        The function sets the background image of an object in Python using Pygame.
        
        :param image_path: The `image_path` parameter is a string that represents the file path to an
        image file that you want to set as the background for a graphical user interface (GUI) element
        :type image_path: str
        """
        aux_image = None
        if image_path:
            aux_image = pg.image.load(image_path)
            aux_image = pg.transform.scale(aux_image, (self.width, self.height))
        else:
            aux_image = pg.Surface((self.width, self.height), masks=(0,0,0))
            # aux_image.set_alpha(0)#Transparente
        self.image = aux_image
            
    
    def render(self) -> None:
        """
        The `render` function in this Python code renders an image with text centered on it.
        """
        self.image.blit(self.img_original, (0, 0))
        image_text = self.font.render(self.text, True, self.font_color)

        media_texto_horizontal = image_text.get_width() / 2
        media_texto_vertical = image_text.get_height() / 2

        media_horizontal = self.width / 2
        media_vertical = self.height / 2
        diferencia_horizontal = media_horizontal - media_texto_horizontal
        diferencia_vertical = media_vertical - media_texto_vertical

        self.image.blit(
            image_text, (diferencia_horizontal, diferencia_vertical)
        )

    def update_text(self, text: str) -> None:
        self.text = text
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.render()
    
    def update_image(self, image_path: str) -> None:
        self.__set_background(image_path)
        self.img_original = self.image.copy()

        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y
        self.render()
            
    def set_text(self, text) -> None:
        """
        The function `set_text` sets the text attribute of an object and then renders it.
        
        :param text: The `set_text` method takes in two parameters: `self` and `text`. The `self`
        parameter refers to the instance of the class that the method is being called on. The `text`
        parameter is the text that will be set to the `text` attribute of the instance
        """
        self.text = text
        self.render()

    def get_text(self) -> str:
        """
        The `get_text` function in Python returns the text attribute of the object it is called on.
        :return: The `get_text` method is returning the `text` attribute of the object instance.
        """
        return self.text

    def update(self, lista_eventos) -> None:
        """
        The function "update" in Python updates a list of events and then calls the "draw" method.
        
        :param lista_eventos: It looks like the `update` method is missing some code inside the
        function. The `self.draw()` line is there, but the rest of the method is not shown
        """
        self.draw()
