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
from .widget import Widget

class InputBox(Widget):
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, placeholder_text: str, screen, font_path: str = None, font_size = 25, color_font: tuple = (255,0,0), color_active = pg.Color('dodgerblue2'), color_inactive = pg.Color('lightskyblue3'), bind_text: bool = False) -> None:
        super().__init__(x, y, text, screen, font_size)
        self.rect = pg.Rect(x, y, width, height)
        self.rect.center = (x, y)
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.color = self.color_inactive
        self.color_placeholder = pg.Color('gray')
        self.font_path = font_path
        self.font_color = color_font
        self.real_text = text
        self.text = text
        self.placeholder_text = placeholder_text # Texto de marcador de posición
        self.__make_font()
        self.txt_surface = self.font.render(text, True, self.font_color)
        self.active = False
        self.padding_x = 5 # Pequeño espacio de los bordes laterales
        self.cursor_pos = len(self.text) # Posición actual del cursor (al final por defecto)
        self.bind_text = bind_text
        
        if not self.text:
            self.placeholder_surface = self.font.render(self.placeholder_text, True, self.color_placeholder)
        else:
            self.placeholder_surface = None
        
        self.__update_text_surface() # Llama a esto al inicio para configurar el desplazamiento

    def __make_font(self):
        if self.font_path:
            self.font = pg.font.Font(self.font_path, self.font_size)
        else:
            self.font = pg.font.SysFont('Arial', self.font_size)
    
    def __events(self, event_list: list[pg.event.Event]):
        for event in event_list:
            self.__handle_event(event)
    
    def __handle_event(self, event: pg.event.Event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.cursor_pos = len(self.text)
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
            self.__update_text_surface() # Actualiza la superficie al cambiar de estado
            
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    print(f"Texto ingresado: {self.text}")
                    # Puedes agregar aquí lógica para enviar el texto
                elif event.key == pg.K_BACKSPACE:
                    if self.cursor_pos > 0:
                        self.real_text = self.real_text[:self.cursor_pos-1] + self.real_text[self.cursor_pos:]
                        self.text = self.real_text
                        self.cursor_pos -= 1
                elif event.key == pg.K_DELETE:
                    if self.cursor_pos < len(self.real_text):
                        self.real_text = self.real_text[:self.cursor_pos] + self.real_text[self.cursor_pos+1:]
                        self.text = self.real_text
                elif event.key == pg.K_LEFT:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif event.key == pg.K_RIGHT:
                    self.cursor_pos = min(len(self.real_text), self.cursor_pos + 1)
                else:
                    self.real_text = self.real_text[:self.cursor_pos] + event.unicode + self.real_text[self.cursor_pos:]
                    self.text = self.real_text
                    self.cursor_pos += len(event.unicode) # Maneja caracteres unicode
                
                self.__update_text_surface() # Actualiza después de cada cambio de texto o cursor
    
    def __update_text_surface(self):
        # Renderiza el texto actual
        if self.bind_text:
            text = '*' * len(self.text)
        else: text = self.real_text
        self.txt_surface = self.font.render(text, True, self.font_color)

        # Ancho disponible dentro del InputBox (sin el padding)
        available_width = self.rect.width - (2 * self.padding_x)

        # Calcular el offset necesario
        # Si el texto es más ancho que el espacio disponible, necesitamos un offset negativo.
        # El offset_x representa la posición x donde comenzará a dibujarse el texto.
        # Queremos que la parte del texto que está en cursor_pos esté visible.
        
        # Calcular el ancho del texto hasta la posición del cursor
        text_before_cursor_width = self.font.render(text[:self.cursor_pos], True, self.font_color).get_width()
        
        # Si el ancho de la superficie de texto es mayor que el ancho disponible
        if text_before_cursor_width > available_width:
            # Calcula el offset negativo para mostrar solo la parte final del texto
            self.offset_x = available_width - text_before_cursor_width
        else:
            # Si el texto cabe, no hay offset
            self.offset_x = 0


        # Asegurarse de que el offset no haga que el texto se salga por la derecha
        # Si el texto completo es más estrecho que el available_width, el offset debe ser 0.
        # Si el offset calculado es demasiado grande (positivo), ajustarlo a 0.
        # O si el texto completo + offset es menor que available_width, ajustarlo para que el final del texto esté al borde derecho
        if self.txt_surface.get_width() + self.offset_x < available_width:
             self.offset_x = available_width - self.txt_surface.get_width()
             # Si el resultado es positivo, significa que el texto es corto, entonces el offset debe ser 0
             if self.offset_x > 0:
                 self.offset_x = 0
        

        self.txt_surface = self.txt_surface # Guardamos la superficie completa
        
        # Vuelve a renderizar el placeholder si el texto está vacío y no está activo
        if not text and not self.active:
            self.placeholder_surface = self.font.render(self.placeholder_text, True, self.color_placeholder)
        else:
            self.placeholder_surface = None

    def draw(self):
        # Dibuja la superficie de texto (o el placeholder)
        if self.text or self.active:
            # Crea un área de visualización (clip rect) para que el texto no se salga del InputBox
            # La posición del clip es (x del rect + padding_x, y del rect)
            # El tamaño del clip es (ancho del rect - 2*padding_x, alto del rect)
            clip_rect = pg.Rect(self.rect.x + self.padding_x, self.rect.y, 
                                    self.rect.width - (2 * self.padding_x), self.rect.height)
            
            # Guarda la superficie original de la pantalla y establece el clip
            original_clip = self.screen.get_clip()
            self.screen.set_clip(clip_rect)

            # Dibuja el texto dentro del área visible, usando el offset
            self.screen.blit(self.txt_surface, (self.rect.x + self.padding_x + self.offset_x, self.rect.y + self.padding_x))
            
            # Restaura el clip original de la pantalla
            self.screen.set_clip(original_clip)

            # Dibuja el cursor si está activo y hay texto
            if self.active:
                # Calcular la posición del cursor en relación con el texto
                cursor_x = self.font.render(self.text[:self.cursor_pos], True, self.font_color).get_width()
                cursor_rect = pg.Rect(self.rect.x + self.padding_x + self.offset_x + cursor_x, 
                                          self.rect.y + self.padding_x, 2, self.rect.height - (2 * self.padding_x))
                pg.draw.rect(self.screen, self.font_color, cursor_rect)


        elif self.placeholder_surface:
            self.screen.blit(self.placeholder_surface, (self.rect.x + self.padding_x, self.rect.y + self.padding_x))

        # Dibuja el borde del InputBox
        pg.draw.rect(self.screen, self.color, self.rect, 2)
    
    def update(self, event_list: list[pg.event.Event]) -> None:
        self.__events(event_list)