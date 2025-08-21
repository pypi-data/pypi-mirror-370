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
    def __init__(self, screen : pg.Surface, max_life : int, actual_life: int, width : int, heigth: int, pos_x : int, pos_y : int, type: str)-> None:...
    def calculate_width_life(self) -> float:...
    def get_actual_amount(self) -> int:...
    def get_max_amount(self) -> int:...
    def set_actual_amount(self, amount)-> None:...
    def set_max_amount(self, amount)-> None:...
    def draw(self)-> None:...
    def update(self, actual_life: int)-> None:...