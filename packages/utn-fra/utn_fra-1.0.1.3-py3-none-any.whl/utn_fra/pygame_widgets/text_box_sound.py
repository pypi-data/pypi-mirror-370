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
import random as rd

class TextBoxSound(Widget):
    """Used to show a text box where the user can write text, the widget will play sounds when
        press a key.
    """
    
    def __init__(self, x, y, text, screen, sound_path: str, font_path: str, font_size = 25, color: tuple = (255,0,0), sounds_list_path: list = None, on_click = None, on_click_param = None) -> None:
        """
        Used to show a text box where the user can write text, the widget will play sounds when
        press a key.
        
        :param x: The X axis where the widget will be
        :param y: The Y axis where the widget will be
        :param text: The text that the widget will show
        :param screen: The main screen where the widget should show
        :param sound_path: The path of the widget sound (if you want a single sound, leave empty and use the 'sounds_list_path' if you want varios sounds)
        :param font_path: The path of the font type that you want to use in the widget
        :param font_size: Default 25
        :param color: Default (255,0,0), You can specify here a tuple of a color like RGB
        :param sounds_list_path: Default None. A list of paths to use in the widget, the widget will select randomly a sound constantly and play diferents sounds ever.
        :param on_click: Default None. Function that the widget will execute.
        :param on_click_param: Default None. Function Parameter to pass to the functions used in 'on_click'.
            
        """
        super().__init__(x, y, text, screen, font_size)
        self.font = pg.font.Font(font_path, self.font_size)
        self.image = self.font.render(self.text, True, color)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.click_option_sfx = GameSound()
        self.sound_path = sound_path
        self.sounds_list_paths = sounds_list_path
        
        self.on_click = on_click
        self.on_click_param = on_click_param
        
        self.write_on = True
        self.writing = ''
        self.image_writing = self.font.render(self.writing, True, color)
        self.rect_writing = self.image_writing.get_rect()
        self.rect_writing.center = (x, y)
    
    def write_on_box(self, event_list: list) -> None:
        """
        This Python function writes characters to a box based on keyboard input events.
        
        :param event_list: The `event_list` parameter is a list that contains events, such as key
        presses, that are being monitored by the function. Each event in the list is checked to see if
        it is a key press event (`event.type == pg.KEYDOWN`) and if the `write_on` flag is set
        :type event_list: list
        """
        for evento in event_list:
            if evento.type == pg.KEYDOWN and self.write_on:
                if evento.key == pg.K_BACKSPACE:
                    self.writing = self.writing[:-1]
                else:
                    self.writing += evento.unicode
                sound_path_selected = self.sound_path
                if self.sounds_list_paths:
                    sound_path_selected = rd.choice(self.sounds_list_paths)
                self.click_option_sfx.play_sound(sound_path_selected)
    
    def update_text(self, new_text: str) -> None:
        self.writing = new_text
    
    def draw(self) -> None:
        super().draw()
        self.image.blit(self.screen, (self.rect_writing.x, self.rect_writing.y))
    
    def update(self, event_list: list) -> None:
        """
        The `update` function in Python takes a list of events, draws on the screen, and writes the
        events on a box.
        
        :param event_list: The `event_list` parameter is a list that contains events or items that need
        to be displayed or updated in some way. This method `update` takes this list as input and
        performs two actions: it first draws something on the screen or interface, and then writes the
        contents of the `event_list
        :type event_list: list
        """
        self.write_on_box(event_list)