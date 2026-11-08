# -*- coding: utf-8 -*-
"""
Módulo con la clase Cliente.

Los datos personales se guardan en atributos privados (encapsulación) y
solo se modifican mediante propiedades que validan cada valor antes de
asignarlo. Si un dato no es válido se lanza DatoInvalidoError o
ParametroFaltanteError.
"""

import re

from .entidad import EntidadBase
from .excepciones import ClienteInvalidoError, DatoInvalidoError, ParametroFaltanteError

# Expresiones regulares usadas en las validaciones.
_PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+(?: [A-Za-zÁÉÍÓÚáéíóúÑñÜü]+)+$")
_PATRON_DOCUMENTO = re.compile(r"^\d{6,10}$")
_PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
_PATRON_TELEFONO = re.compile(r"^3\d{9}$")


class Cliente(EntidadBase):
    """Cliente de Software FJ con datos personales encapsulados."""

    PREFIJO = "CLI"

    def __init__(self, nombre=None, documento=None, correo=None, telefono=None):
        # Se reserva el identificador llamando al constructor de la clase base.
        super().__init__(self.PREFIJO)
        try:
            # Cada asignación pasa por el setter, que valida el dato.
            self.nombre = nombre
            self.documento = documento
            self.correo = correo
            self.telefono = telefono
            # Validación final del objeto completo.
            self.validar()
        except (DatoInvalidoError, ParametroFaltanteError):
            # Si algo falla, se libera el identificador y se relanza el error.
            EntidadBase._revertir_contador(self.PREFIJO)
            raise

    # ----- Propiedades con validación (encapsulación) -----

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("nombre", "Cliente")
        valor = " ".join(str(valor).split())  # Elimina espacios repetidos.
        if not _PATRON_NOMBRE.match(valor):
            raise DatoInvalidoError("nombre", valor, "debe tener nombre y apellido, solo letras")
        if len(valor) > 60:
            raise DatoInvalidoError("nombre", valor, "no puede superar 60 caracteres")
        self.__nombre = valor.title()

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("documento", "Cliente")
        valor = str(valor).strip()
        if not _PATRON_DOCUMENTO.match(valor):
            raise DatoInvalidoError("documento", valor, "debe tener entre 6 y 10 dígitos")
        self.__documento = valor

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("correo", "Cliente")
        valor = str(valor).strip().lower()
        if not _PATRON_CORREO.match(valor):
            raise DatoInvalidoError("correo", valor, "no tiene un formato de correo válido")
        self.__correo = valor

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("telefono", "Cliente")
        valor = str(valor).strip().replace(" ", "")
        if not _PATRON_TELEFONO.match(valor):
            raise DatoInvalidoError("telefono", valor, "debe ser un celular de 10 dígitos que inicie en 3")
        self.__telefono = valor

    # ----- Métodos sobrescritos de EntidadBase -----

    def validar(self):
        """Comprueba que el cliente tenga todos sus datos."""
        for campo in ("nombre", "documento", "correo", "telefono"):
            if not getattr(self, campo, None):
                raise ClienteInvalidoError(f"El cliente no tiene '{campo}'")
        return True

    def documento_enmascarado(self):
        """Muestra solo los últimos 4 dígitos del documento (protección de datos)."""
        return "*" * (len(self.__documento) - 4) + self.__documento[-4:]

    def describir(self):
        return f"{self.id} | {self.nombre} | Doc. {self.documento_enmascarado()} | {self.correo}"
