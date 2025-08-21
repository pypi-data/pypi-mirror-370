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

from .listas_nombres import lista_bzrp_nombres
from .listas_vistas import lista_bzrp_vistas
from .listas_duracion import lista_bzrp_duracion

matriz_bzrp = [
    lista_bzrp_nombres,
    lista_bzrp_vistas,
    lista_bzrp_duracion
]

matriz_bzrp_small = matriz_bzrp[:20]