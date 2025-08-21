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

from .pyvidplayer import Video
import pygame as pg

class UTNVideoPlayer(Video):
    
    def __init__(self, path, screen: pg.Surface):
        super().__init__(path)
        self.__screen = screen
        self.__video_initial_time = 0
        self.__video_length_time = None
    
    def run_video(self, video_size: tuple):
        """
        This Python function runs a video with specified size and volume, updating the display until the
        video length time has elapsed or a close event is triggered.
        
        :param video_size: The `video_size` parameter in the `run_video` method is a tuple that represents the
        dimensions of the video player window. It is used to set the size of the video player window
        when the video is being played
        :type video_size: tuple
        """
        self.set_video_size((video_size[0], video_size[1]))
        self.set_sound_volume(0.3)
        self.__video_initial_time = int(pg.time.get_ticks() / 1000)
        if not self.__video_length_time:
            self.__video_length_time = self.duration
            
        running = True
        while running:
            if self.active:
                
                self.set_sound_volume(0.9)
                self.draw(self.__screen, (0, 0))
            else:
                running = False
                self.close_video()
            current_time = int(pg.time.get_ticks() / 1000)
            if current_time - self.__video_initial_time >= self.__video_length_time:
                running = False
                self.close_video()
            
            running = self.check_close_event(running)
            pg.display.update()
        pg.display.update()
    
    def check_close_event(self, running: bool):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.close_video()
                running = False
                break
        return running
    
    def set_sound_volume(self, volume: float):
        """
        The function `set_sound_volume` sets the volume of a sound to the specified value.
        
        :param volume: The `volume` parameter in the `set_sound_volume` method is a float value that
        represents the desired volume level for the sound
        :type volume: float
        """
        self.set_volume(volume)
    
    def close_video(self):
        """
        The function `close_video` closes the video.
        """
        self.close()
    
    def set_video_size(self, video_size: tuple[int,int]):
        """
        The function `set_video_size` sets the size of a video based on the input tuple of width and
        height.
        
        :param video_size: The `set_video_size` method takes in a parameter `video_size` which is
        expected to be a tuple containing two integers representing the width and height of a video.
        This method then calls another method `set_size` with the `video_size` parameter to set the size
        of the video
        :type video_size: tuple[int,int]
        """
        self.set_size(video_size)