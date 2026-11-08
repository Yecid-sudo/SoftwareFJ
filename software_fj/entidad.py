# -*- coding: utf-8 -*-
"""
Módulo con la clase abstracta EntidadBase.

Representa cualquier entidad general del sistema (clientes, servicios y
reservas). Define lo que todas comparten: un identificador único, la
fecha de creación y la obligación de saber describirse y validarse.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class EntidadBase(ABC):
    """Clase abstracta que representa una entidad general del sistema."""

    # Contadores por prefijo para generar identificadores consecutivos
    # (por ejemplo CLI-001, SRV-001, RES-001).
    _contadores = {}

    def __init__(self, prefijo):
        # Se obtiene el siguiente número para el prefijo dado.
        numero = EntidadBase._contadores.get(prefijo, 0) + 1
        EntidadBase._contadores[prefijo] = numero
        # Atributos privados: solo se leen mediante propiedades.
        self.__id = f"{prefijo}-{numero:03d}"
        self.__fecha_creacion = datetime.now()

    @property
    def id(self):
        """Identificador único de la entidad (solo lectura)."""
        return self.__id

    @property
    def fecha_creacion(self):
        """Fecha y hora en que se creó la entidad (solo lectura)."""
        return self.__fecha_creacion

    @abstractmethod
    def describir(self):
        """Devuelve una descripción legible de la entidad."""

    @abstractmethod
    def validar(self):
        """Verifica que la entidad sea coherente; lanza una excepción si no."""

    @classmethod
    def _revertir_contador(cls, prefijo):
        """Devuelve el contador un paso atrás cuando la creación falla.

        Así un objeto inválido no "consume" un identificador.
        """
        if cls._contadores.get(prefijo, 0) > 0:
            cls._contadores[prefijo] -= 1

    def __str__(self):
        # Al imprimir el objeto se muestra su descripción.
        return self.describir()
