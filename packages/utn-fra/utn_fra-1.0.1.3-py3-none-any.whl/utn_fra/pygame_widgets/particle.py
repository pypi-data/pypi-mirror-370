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

import random as rd
import pygame as pg 

class Particle:
    
    def __init__(self, screen: pg.Surface, circle_radius: int, particle_color: pg.Color = pg.Color('gold')) -> None:
        self.particles = []
        self.screen = screen
        self.radius = circle_radius
        self.particle_color = particle_color
    
    def draw(self) -> None:
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0][1] += particle[2][0]
                particle[0][0] += particle[2][1]
                particle[1] -= 0.2
                pg.draw.circle(self.screen, self.particle_color, particle[0], int(particle[1]))

    def add_particles(self) -> None:
        coords_x_y = list(pg.mouse.get_pos())
        direction_x = rd.randint(-3, 3)
        direction_y = rd.randint(-3, 3)
        particle_circle = [
            coords_x_y,
            self.radius,
            [direction_x, direction_y]
        ]
        self.particles.append(particle_circle)
    
    def delete_particles(self) -> None:
        particles_copy = [
            particle for particle in self.particles
            if particle[1] > 0
        ]
        self.particles = particles_copy