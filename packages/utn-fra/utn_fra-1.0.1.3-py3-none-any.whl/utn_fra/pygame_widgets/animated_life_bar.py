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

class AnimatedLifeBar(pg.sprite.Sprite):
    
    def __init__(self, screen: pg.Surface, current_healt: float, maximum_healt: float, health_bar_length, pos: tuple[int,int], health_speed: int=20, bar_type: str = 'vitality') -> None:
        """
        This function initializes a health bar object with specified parameters and color schemes.
        
        :param screen: The `screen` parameter is expected to be a Pygame Surface object where the health
        bar will be displayed. It is the surface on which the health bar will be rendered
        :type screen: pg.Surface
        :param current_healt: The `current_healt` parameter in the `__init__` method represents the
        current health value of the entity or character for which the health bar is being displayed. It
        is a float value indicating the current health level at the time of initialization
        :type current_healt: float
        :param maximum_healt: The `maximum_health` parameter represents the maximum health value that
        the health bar can display. It is used to calculate the health ratio based on the length of the
        health bar. In the provided code snippet, `maximum_healt` seems to be a typo, and it should be
        corrected to `maximum
        :type maximum_healt: float
        :param health_bar_length: The `health_bar_length` parameter represents the total length of the
        health bar that will be displayed on the screen. It is used to calculate the ratio between the
        maximum health value and the length of the health bar, which in turn determines how much of the
        bar should be filled based on the current health
        :param pos: The `pos` parameter in the `__init__` method represents the position of the health
        bar on the screen. It is a tuple containing two integers representing the x and y coordinates of
        the top-left corner of the health bar's bounding box. For example, if `pos = (100,
        :type pos: tuple[int,int]
        :param health_speed: The `health_speed` parameter in the `__init__` method represents the speed
        at which the health bar transitions from the current health value to the target health value. It
        determines how quickly the visual representation of the health bar changes when the health value
        is updated. In this case, the default value, defaults to 20
        :type health_speed: int (optional)
        :param bar_type: The `bar_type` parameter in the `__init__` method is used to specify the type
        of health bar to be displayed. It determines the colors used for the health bar based on the
        type of bar selected. The available options for `bar_type` are "stamina", "mana",, defaults to
        vitality
        :type bar_type: str (optional)
        """
        super().__init__()
        self.base_colors = {
            "stamina": {
                "primary": pg.Color('yellow'),
                "secondary": pg.Color('gold'),
                "background": (125,125,0)
            },
            "mana": {
                "primary": pg.Color('cyan'),
                "secondary": pg.Color('lightblue'),
                "background": pg.Color('aliceblue')
            },
            "vitality": {
                "primary": pg.Color('green'),
                "secondary": pg.Color('yellow'),
                "background": pg.Color('red')
            },
        }
        self.background_empty_bar_color = (30,30,30)
        self.screen = screen
        self.pos = pos
        self.bar_type = self.base_colors.get(bar_type, 'vitality')
        self.image = pg.Surface((40,40))
        self.image.fill((240,240,240))
        self.rect = self.image.get_rect(center = (400,400))
        self.current_health = current_healt
        self.target_health = self.current_health + 100
        self.maximum_health = maximum_healt
        self.health_bar_length = health_bar_length
        self.health_ratio = self.maximum_health / self.health_bar_length
        self.health_change_speed = health_speed
        self.transition_width = 0
        self.transition_color = (255,0,0)
        
    def get_max_amount(self) -> int:
        """
        This function returns the maximum health amount.
        :return: The method `get_max_amount` is returning the value of `maximum_health` attribute of the
        object.
        """
        return self.maximum_health
    
    def get_actual_amount(self) -> int:
        """
        The function `get_actual_amount` returns the target health value as an integer.
        :return: The `get_actual_amount` method is returning the `target_health` attribute of the
        object.
        """
        return self.target_health
    
    def set_damage(self, amount: int) -> None:
        """
        This function reduces the target's health by a specified amount and ensures it does not go below
        zero.
        
        :param amount: The `amount` parameter in the `set_damage` method represents the amount of damage
        that will be subtracted from the `target_health` attribute of the object. This parameter should
        be an integer value indicating the damage to be inflicted on the target
        :type amount: int
        """
        if self.target_health > 0:
            self.target_health -= amount
        if self.target_health <= 0:
            self.target_health = 0
    
    def set_health(self, amount: int) -> None:
        """
        This function increases the target health by a specified amount, ensuring it does not exceed the
        maximum health.
        
        :param amount: The `amount` parameter in the `set_health` method represents the value by which
        the target's health will be increased. It is an integer value that determines how much the
        health of the target will be adjusted
        :type amount: int
        """
        if self.target_health < self.maximum_health:
            self.target_health += amount
        if self.target_health >= self.maximum_health:
            self.target_health = self.maximum_health
    
    def advanced_health(self) -> None:
        """
        The `advanced_health` function updates a health bar with transition effects based on current and
        target health values.
        """
        transition_width = 0
        transition_color = self.bar_type.get('primary')
        
        if self.current_health < self.target_health:
            self.current_health += self.health_change_speed
            transition_width = int((self.target_health- self.current_health)/self.health_ratio)
            transition_color = self.bar_type.get('secondary')
        
        elif self.current_health > self.target_health:
            self.current_health -= self.health_change_speed
            transition_width = int((self.target_health - self.current_health)/ self.health_ratio)
            transition_color = (255,0,0)
        
        health_bar_rect =  pg.Rect(self.pos[0], self.pos[1], self.current_health/self.health_ratio, 25)
        transition_bar_rect = pg.Rect(health_bar_rect.right, self.pos[1], transition_width, 25)
        
        pg.draw.rect(self.screen, self.bar_type.get('background'), (self.pos[0],self.pos[1], self.health_bar_length, 25))
        pg.draw.rect(self.screen, self.bar_type.get('primary'), health_bar_rect)
        pg.draw.rect(self.screen, transition_color, transition_bar_rect)
        pg.draw.rect(self.screen, (255,255,255), (self.pos[0],self.pos[1], self.health_bar_length, 25), 4)
        
        pg.draw.rect(self.screen, pg.Color('white'), (self.pos[0],self.pos[1], self.health_bar_length, 25), 4)
    
    def update_target_health(self, amount: int) -> None:
        """
        The function `update_target_health` adjusts the health of a target based on the provided amount.
        
        :param amount: The `amount` parameter in the `update_target_health` method represents the new
        health value that you want to set for the target. This method is designed to update the health
        of a target based on the provided amount. If the amount is greater than the current target
        health, it will call the `
        :type amount: int
        """
        if amount > self.target_health:
            total = amount - self.target_health
            self.set_health(total)
        elif amount < self.target_health:
            total = self.target_health - amount
            self.set_damage(total)
    
    def update(self, actual_health: int) -> None:
        """
        The function `update` takes an integer `actual_health` as input and updates the target health
        using the `update_target_health` method.
        
        :param actual_health: The `actual_health` parameter in the `update` method is an integer
        representing the current health value that you want to update for the target entity
        :type actual_health: int
        """
        self.update_target_health(actual_health)
    
    def draw(self) -> None:
        """
        The function `draw` in the Python code likely includes a call to `advanced_health`.
        """
        self.advanced_health()
