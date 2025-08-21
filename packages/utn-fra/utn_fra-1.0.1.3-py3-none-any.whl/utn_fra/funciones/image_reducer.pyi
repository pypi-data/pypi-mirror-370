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

from PIL import Image # pip install pillow
import os

class ImageReducer:
    def __init__(self,input_path: str) -> None:...
    def reduce_image_weight(self, nivel_compresion: int = 9) -> None:...
    def reduce_image_size(self, nuevo_ancho: int = None, nuevo_alto: int = None, factor_escala: float = None, interpolacion=Image.LANCZOS) -> None:...
    