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

import os
import sys
from ..common_variables import VERSION
from tabulate import tabulate as tabu


def __color_text(text: str, message_type: str = '') -> str:
    """
    The function `color_text` takes a text input and a message type, and returns the text formatted
    with color based on the message type.
    
    :param text: The `text` parameter in the `color_text` function is the string that you want to
    colorize based on the `message_type`. It is the main content that will be displayed with the
    specified color and message type
    :type text: str
    :param message_type: The `message_type` parameter in the `color_text` function is used to specify
    the type of message being displayed. It has a default value of an empty string, which means if no
    message type is provided when calling the function, it will default to a general system message
    :type message_type: str
    """
    _b_red: str = '\033[41m'
    _b_green: str = '\033[42m'
    _b_blue: str = '\033[44m'
    _f_white: str = '\033[37m'
    _no_color: str = '\033[0m'
    message_type = message_type.strip().capitalize()
    match message_type:
        case 'Error':
            text =  f'{_b_red}{_f_white}> Error: {text}{_no_color}'
        case 'Success':
            text = f'{_b_green}{_f_white}> Success: {text}{_no_color}'
        case 'Info':
            text = f'{_b_blue}{_f_white}> Information: {text}{_no_color}'
        case _:
            text =  f'{_b_red}{_f_white}> System: {text}{_no_color}'

    return text

def clear_console() -> None:
    """
    The function `clear_console` clears the console screen and prompts the user to press Enter to
    continue.
    """
    _ = input(__color_text("\nPresiona Enter para continuar..."))
    os.system('cls' if os.name in ['nt', 'dos'] else 'clear')

def saludo() -> None:
    """
    The function `saludo()` prints a greeting message with information about the UTN community and
    dataset version.
    """
    message =\
        f"UTN (v{VERSION}, Python {'.'.join([str(num) for num in sys.version_info[0:3]])})"\
        f'\nHello from the UTN community. https://pypi.org/project/UTN-FRA/'
    print(__color_text(message, 'Success'))

def show_matrix_as_table(matrix: list[list], headers: list[str], tablefmt: str = 'rounded_grid') -> None:
    """
    The function `show_matrix_as_table` displays a matrix as a formatted table with headers in Python.
    
    :param matrix: The `matrix` parameter is a list of lists that represents the data to be displayed in
    the table. Each inner list corresponds to a row in the table, and the elements within each inner
    list represent the columns of the table
    :type matrix: list[list]
    :param headers: The `headers` parameter is a list of strings that represent the column headers of
    the table. Each string in the list corresponds to a column in the table and provides a label for
    that column
    :type headers: list[str]
    :param tablefmt: The `tablefmt` parameter in the `show_matrix_as_table` function is used to specify
    the format of the table that will be displayed when the function is called. It determines the style
    and appearance of the table output. In this case, the default value for `tablefmt` is set, defaults
    to rounded_grid
    :type tablefmt: str (optional)
    """
    text = tabu(matrix, headers, tablefmt, numalign = 'right')
    print(text)
