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

import pygame.mixer as mixer

class GameSound:
    """
    The `GameSound` class in Python provides methods to play sound effects and music with adjustable
    volume levels.
    """
    
    def __init__(self) -> None:
        mixer.init()

    def play_sound(self, sound_path: str, volume: float = 0.8) -> None:
        """
        The `play_sound` function in Python plays a sound file at a specified volume level.
        
        :param sound_path: The `sound_path` parameter is a string that represents the file path to the
        sound file that you want to play. This could be a path to a .wav, .mp3, or any other supported
        sound file format
        :type sound_path: str
        :param volume: The `volume` parameter in the `play_sound` function is used to specify the volume
        level at which the sound should be played. The default value for the `volume` parameter is set
        to 0.8, but you can provide a different value when calling the function if you want the sound
        :type volume: float
        """
        sound = mixer.Sound(sound_path)
        sound.set_volume(volume)
        sound.play()
    
    def play_music(self, music_path: str, volume: float = 0.5, fade_ms: int = 3000, loop: bool = True) -> None:
        """
        This Python function plays music from a specified path with an optional volume setting.
        
        :param music_path: The `music_path` parameter is a string that represents the file path to the
        music file that you want to play. This parameter specifies the location of the music file on
        your system
        :type music_path: str
        :param volume: The `volume` parameter in the `play_music` function is used to set the volume
        level at which the music will be played. The default value for the `volume` parameter is 0.5,
        which represents 50% volume. You can adjust this parameter to set the desired volume level
        :type volume: float
        """
        mixer.music.load(music_path)
        mixer.music.set_volume(volume)
        mixer.music.play(-1 if loop else 0, 0, fade_ms)
    
    def stop_music(self) -> None:
        """
        The function `stop_music` fades out the currently playing music over a period of 500
        milliseconds.
        """
        mixer.music.fadeout(500)
        