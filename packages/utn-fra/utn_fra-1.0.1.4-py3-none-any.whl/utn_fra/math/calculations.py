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


def transposed_matrix(matrix: list[list], add_index: bool = False, truncate_string_value: int = 0) -> list[list]:
    """
    The function `transposed_matrix` takes a matrix as input and returns its transposed version, with an
    option to add row indices and truncate string values.
    
    :param matrix: The `matrix` parameter is a list of lists representing a matrix where each inner list
    corresponds to a row in the matrix. Each element in the inner lists represents a value in the matrix
    :type matrix: list[list]
    :param add_index: The `add_index` parameter in the `transposed_matrix` function is a boolean flag
    that determines whether to add the index of each column as the first element in the transposed row.
    If `add_index` is set to `True`, the index of the column will be inserted at the beginning, defaults
    to False
    :type add_index: bool (optional)
    :param truncate_string_value: The `truncate_string_value` parameter in the `transposed_matrix`
    function is used to specify the maximum length of a string value in the matrix columns. If the value
    in a matrix cell is a string and its length exceeds the specified `truncate_string_value`, it will
    be truncated to the specified length, defaults to 0
    :type truncate_string_value: int (optional)
    :return: The function `transposed_matrix` returns a transposed matrix based on the input matrix
    provided. The transposed matrix may include index values for each column if the `add_index`
    parameter is set to `True`. Additionally, string values in the matrix columns may be truncated based
    on the `truncate_string_value` parameter.
    """
    new_transposed_matrix = []
    amount_columns = len(matrix[0])
    
    for index_column in range(amount_columns):
        trasposed_row = []
        for index_row in range(len(matrix)):
            value = matrix[index_row][index_column][:truncate_string_value]\
                if truncate_string_value and type(matrix[index_row][index_column]) == str\
                else matrix[index_row][index_column]
            trasposed_row.append(value)
        if add_index:
            trasposed_row.insert(0, index_column)
        new_transposed_matrix.append(trasposed_row)
    return new_transposed_matrix

def transpose(matrix: list[list], add_index: bool = False) -> list[list]:
    """
    The function transposes a matrix and optionally adds an index to each column.
    
    :param matrix: The `matrix` parameter is a list of lists representing a matrix where each inner list
    is a row of the matrix. Each inner list should have the same length to form a valid matrix
    :type matrix: list[list]
    :param add_index: The `add_index` parameter in the `transpose` function is a boolean flag that
    determines whether to include the column index + 1 as the first element in each transposed row. If
    `add_index` is set to `True`, the column index + 1 will be included. If `, defaults to False
    :type add_index: bool (optional)
    :return: The function `transpose` returns a transposed matrix where the rows of the input matrix
    become columns in the new matrix. Each element in the transposed matrix is a list containing the
    index of the column (if `add_index` is True) followed by the elements from the corresponding row in
    the original matrix.
    """
    amount_columns = len(matrix[0])
    new_transposed_matrix = [
        [index_column + 1 if add_index else None] + 
        [matrix[index_row][index_column] for index_row in range(len(matrix))]
        for index_column in range(amount_columns)
    ]
    return new_transposed_matrix

def create_null_matrix(rows: int, columns: int) -> list[list[int]]:
    """
    The function `create_null_matrix` generates a matrix filled with zeros based on the specified number
    of rows and columns.
    
    :param rows: The `rows` parameter specifies the number of rows in the matrix you want to create. It
    indicates how many lists of integers will be contained within the main list representing the matrix
    :type rows: int
    :param columns: Columns refer to the number of vertical elements in a matrix or a grid. It
    represents the number of elements in each row of the matrix
    :type columns: int
    :return: The function `create_null_matrix` returns a 2D list (matrix) filled with zeros, with the
    specified number of rows and columns.
    """
    new_null_matrix = [
        [0 for _ in range(columns)]
        for _ in range(rows)
    ]
    
    return new_null_matrix

def create_identity_matrix(dimention: int = 2, side: str = 'right') -> list[list[int]]:
    """
    The function creates an identity matrix of a specified dimension in Python
    bassed on the side parameter that could be `right` or `left`. Is `right` by default
    
    :param dimention: The `dimention` parameter in the `create_identity_matrix` function specifies the
    dimension of the square identity matrix to be created. By default, if no value is provided for
    `dimention`, it will create a 2x2 identity matrix. You can specify a different dimension by passing
    an integer, defaults to 2
    :type dimention: int (optional)
    :param side: Side towards which the diagonal formed by numbers 1 will face.
    :type side: str (optional)
    :return: The function `create_identity_matrix` returns a 2D list representing an identity matrix of
    the specified dimension.
    """
    new_identity_matrix = [
        [1 if side.lower() == 'left' and (index_column + index_row == dimention -1) 
         or side.lower() == 'right' and (index_column == index_row) else 0
         for index_column in range(dimention)] 
        for index_row in range(dimention)
    ]
    
    return new_identity_matrix

def sum_matrix(matrix_1: list[list[int]], matrix_2: list[list[int]]) -> list[list[int]]:
    """
    The function `sum_matrix` takes two matrices as input and returns a new matrix that is the sum of
    the input matrices element-wise.
    
    :param matrix_1: A list of lists representing the first matrix
    :type matrix_1: list[list[int]]
    :param matrix_2: The `matrix_2` parameter in the `sum_matrix` function represents a 2D list of
    integers that will be added element-wise to the corresponding elements in `matrix_1`. Both
    `matrix_1` and `matrix_2` should have the same dimensions (number of rows and
    :type matrix_2: list[list[int]]
    :return: The function `sum_matrix` returns a new matrix that is the result of adding corresponding
    elements of two input matrices `matrix_1` and `matrix_2`.
    """
    new_matrix = [
        [matrix_1[index_row][index_column] + matrix_2[index_row][index_column]
        for index_column in range(len(matrix_1[index_row]))]
        for index_row in range(len(matrix_1))
    ]
    
    return new_matrix

def mul_matrix_by_scalar(matrix_1: list[list[int]], scalar_number: int) -> list[list[int]]:
    """
    The function `mul_matrix_by_scalar` multiplies each element of a matrix by a scalar number and
    returns the resulting matrix.
    
    :param matrix_1: A 2D list representing a matrix, where each inner list represents a row of the
    matrix and contains integers
    :type matrix_1: list[list[int]]
    :param scalar_number: The `scalar_number` parameter is the number by which you want to multiply each
    element of the matrix
    :type scalar_number: int
    :return: a new matrix that is the result of multiplying each element in the input matrix by the
    scalar number provided.
    """
    new_matrix = [
        [cell * scalar_number for cell in row]
        for row in matrix_1
    ]
    
    return new_matrix
