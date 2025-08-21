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

from .lista_nombres import lista_nombres_videos, lista_nombres_videos_small
from .lista_views import lista_vistas_videos, lista_vistas_videos_small
from .lista_duracion import lista_duraciones_videos, lista_duraciones_videos_small

matriz_paulina = [
    lista_nombres_videos,
    lista_vistas_videos,
    lista_duraciones_videos
]

matriz_paulina_small = [
    lista_nombres_videos_small,
    lista_vistas_videos_small,
    lista_duraciones_videos_small
]