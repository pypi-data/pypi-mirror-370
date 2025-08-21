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
    
    def __init__(self,input_path: str) -> None:
        """
        Inicializa la clase encargada de reducir el peso de las imagenes sin perdida de calidad.
        Args:
            input_path (str): Ruta de los archivos PNG de entrada.
        """
        self.input_path = input_path
        self.paths_list = list()

    def __reducir_peso_png_pillow(self, path: str, nivel_compresion=9) -> None:
        """
        Reduce el peso de una imagen PNG usando Pillow.

        Args:
            nivel_compresion (int): Nivel de compresión de 0 (sin compresión, rápido)
                                    a 9 (máxima compresión, lento). El valor predeterminado es 9.
        """
        try:
            imagen = Image.open(path)
            imagen.save(path, optimize=True, compress_level=nivel_compresion)
            print(f"Imagen optimizada guardada en: {path}")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo en la ruta: {path}")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

    def __make_files_paths(self,root_path: str, files_path: list[str]) -> None:
        for file in files_path:
            new_path = os.path.join(root_path, file)
            self.paths_list.append(f'{new_path}')

    def __create_paths(self) -> None:
        self.paths_list = list()
        for root, dir, files in os.walk(self.input_path):
            self.__make_files_paths(root, files)
    
    def __redimensionar_imagen_pillow(self, ruta_entrada, nuevo_ancho=None, nuevo_alto=None, factor_escala=None, interpolacion=Image.LANCZOS) -> None:
        """
        Redimensiona una imagen PNG manteniendo la máxima calidad posible.

        Args:
            ruta_entrada (str): Ruta del archivo de imagen de entrada.
            ruta_salida (str): Ruta donde se guardará la imagen redimensionada.
            nuevo_ancho (int, optional): Ancho deseado en píxeles. Si se especifica, el alto se ajusta para mantener la proporción.
            nuevo_alto (int, optional): Alto deseado en píxeles. Si se especifica, el ancho se ajusta para mantener la proporción.
            factor_escala (float, optional): Factor para escalar la imagen (ej: 0.5 para reducir a la mitad, 2.0 para duplicar).
            interpolacion (PIL.Image.Resampling): Algoritmo de interpolación a usar.
                                                Recomendado: Image.LANCZOS.
        """
        ruta_salida = ruta_entrada
        try:
            imagen = Image.open(ruta_entrada)
            ancho_original, alto_original = imagen.size

            if factor_escala:
                if factor_escala <= 0:
                    raise ValueError("El factor de escala debe ser mayor que 0.")
                nuevo_ancho = int(ancho_original * factor_escala)
                nuevo_alto = int(alto_original * factor_escala)
            elif nuevo_ancho and not nuevo_alto:
                if nuevo_ancho <= 0:
                    raise ValueError("El nuevo ancho debe ser mayor que 0.")
                nuevo_alto = int(alto_original * (nuevo_ancho / ancho_original))
            elif nuevo_alto and not nuevo_ancho:
                if nuevo_alto <= 0:
                    raise ValueError("El nuevo alto debe ser mayor que 0.")
                nuevo_ancho = int(ancho_original * (nuevo_alto / alto_original))
            elif nuevo_ancho and nuevo_alto:
                if nuevo_ancho <= 0 or nuevo_alto <= 0:
                    raise ValueError("El nuevo ancho y alto deben ser mayores que 0.")
                # Si se especifican ambos, se usarán tal cual, pero puede haber distorsión si no se mantiene la proporción
                print("Advertencia: Se especificaron ancho y alto. Si no mantienen la proporción, la imagen puede distorsionarse.")
            else:
                raise ValueError("Debes especificar 'nuevo_ancho', 'nuevo_alto' o 'factor_escala'.")

            # Asegurarse de que las dimensiones sean válidas
            if nuevo_ancho == 0 or nuevo_alto == 0:
                print("Error: Las dimensiones calculadas resultaron en cero. No se puede redimensionar.")
                return

            imagen_redimensionada = imagen.resize((nuevo_ancho, nuevo_alto), interpolacion)
            
            # Para PNG, siempre es bueno guardar con optimize=True para la compresión sin pérdida
            imagen_redimensionada.save(ruta_salida, optimize=True)
            print(f"Imagen redimensionada y guardada en: {ruta_salida} (Dimensiones: {nuevo_ancho}x{nuevo_alto})")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo en la ruta: {ruta_entrada}")
        except ValueError as ve:
            print(f"Error en los parámetros de redimensionamiento: {ve}")
        except Exception as e:
            print(f"Ocurrió un error: {e}")
    
    def reduce_image_weight(self, nivel_compresion: int = 9) -> None:
        """
        Reduce el tamaño de las imagenes presentes en el directorio raíz y subdirectorios,
        guardandolas bajo su mismo nombre pero con un peso menor.
        Args:
            nivel_compresion (int): Nivel de compresión de 0 (sin compresión, rápido)
                                    a 9 (máxima compresión, lento). El valor predeterminado es 9.
        """
        self.__create_paths()
        for path in self.paths_list:
            self.__reducir_peso_png_pillow(path, nivel_compresion)
    
    def reduce_image_size(self, nuevo_ancho: int = None, nuevo_alto: int = None, factor_escala: float = None, interpolacion=Image.LANCZOS) -> None:
        """
        Redimensiona imagenes PNG manteniendo la máxima calidad posible.

        Args:
            nuevo_ancho (int, optional): Ancho deseado en píxeles. Si se especifica, el alto se ajusta para mantener la proporción.
            nuevo_alto (int, optional): Alto deseado en píxeles. Si se especifica, el ancho se ajusta para mantener la proporción.
            factor_escala (float, optional): Factor para escalar la imagen (ej: 0.5 para reducir a la mitad, 2.0 para duplicar).
            interpolacion (PIL.Image.Resampling): Algoritmo de interpolación a usar.
                                                Recomendado: Image.LANCZOS.
        """
        self.__create_paths()
        for path in self.paths_list:
            self.__redimensionar_imagen_pillow(path, nuevo_ancho, nuevo_alto, factor_escala, interpolacion)