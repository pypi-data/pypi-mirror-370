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

def transposed_matrix(matrix: list[list], add_index: bool = False, truncate_string_value: int = 0) -> list[list]: ...
def transpose(matrix: list[list], add_index: bool = False) -> list[list]: ...
def create_null_matrix(rows: int, columns: int) -> list[list[int]]: ...
def create_identity_matrix(dimention: int = 2, side: str = 'right')-> list[list[int]]: ...
def sum_matrix(matrix_1: list[list[int]], matrix_2: list[list[int]]) -> list[list[int]]: ...
def mul_matrix_by_scalar(matrix_1: list[list[int]], scalar_number: int) -> list[list[int]]: ...