# -*- coding: utf-8 -*-
"""
Módulo de servicios de Software FJ.

Contiene la clase abstracta Servicio y tres servicios especializados:
ReservaSala, AlquilerEquipo y AsesoriaEspecializada. Cada uno sobrescribe
los métodos para calcular el costo base, describirse y validar los
parámetros de una reserva (polimorfismo).

El método calcular_costo() está "sobrecargado": Python no permite varias
definiciones con el mismo nombre, así que se simula con parámetros
opcionales, lo que da varias formas de invocarlo:
    calcular_costo(duracion)                        -> costo base
    calcular_costo(duracion, impuesto)              -> costo con impuesto
    calcular_costo(duracion, impuesto, descuento)   -> con impuesto y descuento
    calcular_costo(duracion, descuento=0.1)         -> solo descuento
"""

import math
from abc import abstractmethod

from .entidad import EntidadBase
from .excepciones import (
    CalculoInconsistenteError,
    DatoInvalidoError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)


def formato_pesos(valor):
    """Da formato de pesos colombianos: 1234567 -> $1.234.567."""
    return "$" + f"{valor:,.0f}".replace(",", ".")


class Servicio(EntidadBase):
    """Clase abstracta que representa un servicio ofrecido por Software FJ."""

    PREFIJO = "SRV"
    IVA = 0.19              # Impuesto por defecto (IVA en Colombia).
    DESCUENTO_MAXIMO = 0.5  # No se permiten descuentos mayores al 50 %.
    DURACION_MAXIMA = 12    # Horas máximas de una reserva.

    def __init__(self, nombre, tarifa_hora, disponible=True):
        super().__init__(self.PREFIJO)
        try:
            # Validación de datos comunes a todos los servicios.
            if not nombre or not str(nombre).strip():
                raise ParametroFaltanteError("nombre", type(self).__name__)
            self._nombre = str(nombre).strip()
            self._tarifa_hora = self._validar_numero_positivo("tarifa_hora", tarifa_hora)
            self._disponible = bool(disponible)
            # Validación propia de cada subclase (polimorfismo).
            self.validar()
        except (DatoInvalidoError, ParametroFaltanteError, ValueError, TypeError) as error:
            EntidadBase._revertir_contador(self.PREFIJO)
            # Encadenamiento de excepciones: el error original queda en __cause__.
            raise ServicioInvalidoError(
                f"No se pudo crear el servicio {type(self).__name__}: {error}"
            ) from error

    # ----- Propiedades -----

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, disponible):
        """Activa o desactiva el servicio."""
        self._disponible = bool(disponible)

    # ----- Utilidades de validación -----

    @staticmethod
    def _validar_numero_positivo(campo, valor):
        """Convierte a número y verifica que sea mayor que cero."""
        if valor is None:
            raise ParametroFaltanteError(campo)
        try:
            numero = float(valor)
        except (TypeError, ValueError) as error:
            raise DatoInvalidoError(campo, valor, "debe ser numérico") from error
        if not math.isfinite(numero) or numero <= 0:
            raise DatoInvalidoError(campo, valor, "debe ser mayor que cero")
        return numero

    def validar_duracion(self, duracion):
        """Valida la duración (en horas) de una reserva."""
        horas = self._validar_numero_positivo("duracion", duracion)
        if horas > self.DURACION_MAXIMA:
            raise DatoInvalidoError("duracion", duracion, f"no puede superar {self.DURACION_MAXIMA} horas")
        return horas

    # ----- Métodos abstractos (cada servicio los implementa) -----

    @abstractmethod
    def calcular_costo_base(self, duracion, **parametros):
        """Costo del servicio sin impuestos ni descuentos."""

    @abstractmethod
    def validar_parametros(self, duracion, **parametros):
        """Valida los parámetros específicos de una reserva de este servicio."""

    # ----- Método "sobrecargado" -----

    def calcular_costo(self, duracion, impuesto=None, descuento=None, **parametros):
        """Calcula el costo total con distintas variantes (ver docstring del módulo)."""
        base = self.calcular_costo_base(duracion, **parametros)

        # Variante 1: sin impuesto ni descuento -> solo el costo base.
        tasa_impuesto = 0.0 if impuesto is None else impuesto
        tasa_descuento = 0.0 if descuento is None else descuento

        # Validación de las tasas recibidas.
        try:
            tasa_impuesto = float(tasa_impuesto)
            tasa_descuento = float(tasa_descuento)
        except (TypeError, ValueError) as error:
            raise CalculoInconsistenteError("El impuesto y el descuento deben ser numéricos") from error
        if not 0 <= tasa_impuesto <= 0.3:
            raise CalculoInconsistenteError(f"Impuesto fuera de rango (0 a 30 %): {tasa_impuesto:.0%}")
        if not 0 <= tasa_descuento <= self.DESCUENTO_MAXIMO:
            raise CalculoInconsistenteError(
                f"Descuento fuera de rango (0 a {self.DESCUENTO_MAXIMO:.0%}): {tasa_descuento:.0%}"
            )

        # Variantes 2 a 4: se aplica primero el descuento y luego el impuesto.
        total = base * (1 - tasa_descuento) * (1 + tasa_impuesto)

        # Control final: el resultado debe ser un número finito y positivo.
        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError(f"Costo calculado no válido: {total}")
        return round(total, 2)

    def describir(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"{self.id} | {self.nombre} | {formato_pesos(self.tarifa_hora)}/hora | {estado}"


class ReservaSala(Servicio):
    """Reserva de salas de reuniones o capacitación."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        # La capacidad se asigna antes de llamar a super() porque validar() la usa.
        self._capacidad = capacidad
        super().__init__(nombre, tarifa_hora, disponible)

    @property
    def capacidad(self):
        return self._capacidad

    def validar(self):
        try:
            capacidad = int(self._capacidad)
        except (TypeError, ValueError) as error:
            raise DatoInvalidoError("capacidad", self._capacidad, "debe ser un número entero") from error
        if capacidad < 2 or capacidad > 200:
            raise DatoInvalidoError("capacidad", self._capacidad, "debe estar entre 2 y 200 personas")
        self._capacidad = capacidad
        return True

    def validar_parametros(self, duracion, **parametros):
        self.validar_duracion(duracion)
        personas = parametros.get("personas")
        if personas is None:
            raise ParametroFaltanteError("personas", "reserva de sala")
        personas = int(self._validar_numero_positivo("personas", personas))
        if personas > self._capacidad:
            raise DatoInvalidoError(
                "personas", personas, f"supera la capacidad de la sala ({self._capacidad})"
            )
        return True

    def calcular_costo_base(self, duracion, **parametros):
        horas = self.validar_duracion(duracion)
        # Recargo del 10 % si la sala se ocupa más del 80 % de su capacidad.
        personas = parametros.get("personas", 0) or 0
        recargo = 1.10 if personas > self._capacidad * 0.8 else 1.0
        return self._tarifa_hora * horas * recargo

    def describir(self):
        return f"[Sala] {super().describir()} | Capacidad: {self._capacidad} personas"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos (portátiles, proyectores, etc.)."""

    def __init__(self, nombre, tarifa_hora, tipo_equipo, unidades, disponible=True):
        self._tipo_equipo = tipo_equipo
        self._unidades = unidades
        super().__init__(nombre, tarifa_hora, disponible)

    @property
    def unidades(self):
        return self._unidades

    def validar(self):
        if not self._tipo_equipo or not str(self._tipo_equipo).strip():
            raise ParametroFaltanteError("tipo_equipo", "AlquilerEquipo")
        try:
            unidades = int(self._unidades)
        except (TypeError, ValueError) as error:
            raise DatoInvalidoError("unidades", self._unidades, "debe ser un número entero") from error
        if unidades < 1:
            raise DatoInvalidoError("unidades", self._unidades, "debe haber al menos una unidad")
        self._unidades = unidades
        self._tipo_equipo = str(self._tipo_equipo).strip()
        return True

    def validar_parametros(self, duracion, **parametros):
        self.validar_duracion(duracion)
        cantidad = parametros.get("cantidad")
        if cantidad is None:
            raise ParametroFaltanteError("cantidad", "alquiler de equipo")
        cantidad = int(self._validar_numero_positivo("cantidad", cantidad))
        if cantidad > self._unidades:
            raise DatoInvalidoError(
                "cantidad", cantidad, f"solo hay {self._unidades} unidades de {self._tipo_equipo}"
            )
        return True

    def calcular_costo_base(self, duracion, **parametros):
        horas = self.validar_duracion(duracion)
        cantidad = parametros.get("cantidad", 1) or 1
        # Seguro fijo de $5.000 por equipo alquilado.
        return self._tarifa_hora * horas * cantidad + 5000 * cantidad

    def describir(self):
        return f"[Equipo] {super().describir()} | {self._tipo_equipo}: {self._unidades} unid."


class AsesoriaEspecializada(Servicio):
    """Asesorías especializadas con un profesional según su nivel."""

    # Factor que multiplica la tarifa según el nivel del asesor.
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, area, nivel="junior", disponible=True):
        self._area = area
        self._nivel = nivel
        super().__init__(nombre, tarifa_hora, disponible)

    def validar(self):
        if not self._area or not str(self._area).strip():
            raise ParametroFaltanteError("area", "AsesoriaEspecializada")
        nivel = str(self._nivel).strip().lower()
        if nivel not in self.NIVELES:
            raise DatoInvalidoError("nivel", self._nivel, f"debe ser uno de {list(self.NIVELES)}")
        self._nivel = nivel
        self._area = str(self._area).strip()
        return True

    def validar_parametros(self, duracion, **parametros):
        horas = self.validar_duracion(duracion)
        # Una asesoría dura mínimo una hora.
        if horas < 1:
            raise DatoInvalidoError("duracion", duracion, "una asesoría dura mínimo 1 hora")
        return True

    def calcular_costo_base(self, duracion, **parametros):
        horas = self.validar_duracion(duracion)
        return self._tarifa_hora * horas * self.NIVELES[self._nivel]

    def describir(self):
        return f"[Asesoría] {super().describir()} | Área: {self._area} | Nivel: {self._nivel}"


# Registro de tipos de servicio: permite crear servicios por nombre y
# añadir nuevos tipos sin modificar el resto del sistema (extensibilidad).
TIPOS_SERVICIO = {
    "sala": ReservaSala,
    "equipo": AlquilerEquipo,
    "asesoria": AsesoriaEspecializada,
}
