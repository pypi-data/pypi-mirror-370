# MIT License
#
# Copyright (c) 2023 [UTN FRA](https://fra.utn.edu.ar/) All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pygame as pg

COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_PURPLE = (255, 0, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_NARANJA = (255, 86, 19)
COLOR_CYAN = (5, 239, 250)
COLOR_LIGHT_GREEN = (14, 187, 0)
COLOR_WHITE = (255,255,255)

class LifeBar(pg.sprite.Sprite):
    def __init__(self, screen : pg.Surface, max_life : int, actual_life: int, width : int, heigth: int, pos_x : int, pos_y : int, type: str)-> None:
        self.screen = screen
        self.width = width
        self.heigth = heigth
        self.pos = (pos_x, pos_y)
        self.max_life = max_life
        self.actual_life = actual_life
        self.color_back = COLOR_RED
        self.color_life = None
        self.image = pg.Surface((self.width, self.heigth))
        self.rect = self.image.get_rect(topleft=self.pos)
        self.bar_background = pg.Surface((self.width, self.heigth))
        self.bar_background.fill(self.color_back)
        self.bar_front = pg.Surface((self.calculate_width_life(), self.heigth))
        self.rect_life = self.bar_front.get_rect(topleft=self.pos)
        self.__create_main_bar_color(type)
    
    def calculate_width_life(self) -> float:
        """Calcula el ancho de la barra de vida actual."""
        if self.max_life == 0:
            return 0
        return (self.actual_life / self.max_life) * self.width
    
    def __create_main_bar_color(self, color: str):
        self.__main_color = color
        if self.__main_color == 'hp': self.color_life = COLOR_LIGHT_GREEN
        elif self.__main_color == 'mp': self.color_life = COLOR_CYAN
        elif self.__main_color == 'stamina': self.color_life = COLOR_YELLOW
        elif self.__main_color == 'blank': self.color_life = COLOR_WHITE
        
        self.bar_front.fill(self.color_life)

    def get_actual_amount(self) -> int:
        return self.actual_life
    
    def set_actual_amount(self, amount)-> None:
        self.actual_life = amount
    
    def get_max_amount(self) -> int:
        return self.max_life

    def set_max_amount(self, amount)-> None:
        self.max_life = amount
    
    def draw(self)-> None:
        self.screen.blit(self.bar_background, self.rect)# rojo - barra de atras
        self.screen.blit(self.barra_vida, self.rect) # verde - barra de delante

    def update(self, actual_life: int)-> None:
        self.actual_life = max(0, min(actual_life, self.max_life))  # Asegura que la vida esté dentro de los límites
        self.barra_vida = pg.Surface((self.calculate_width_life(), self.heigth))
        self.barra_vida.fill(self.color_life)
        self.rect_life = self.barra_vida.get_rect(topleft=self.pos)
