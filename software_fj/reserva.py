# -*- coding: utf-8 -*-
"""
Módulo con la clase Reserva.

Una reserva integra un cliente, un servicio, una duración y un estado.
Su ciclo de vida es:

    PENDIENTE --confirmar()--> CONFIRMADA --procesar()--> PROCESADA
        \\                          \\
         +------cancelar()----------+--> CANCELADA

Cada transición valida el estado actual y lanza OperacionNoPermitidaError
si la operación no corresponde.
"""

from .cliente import Cliente
from .entidad import EntidadBase
from .excepciones import (
    CalculoInconsistenteError,
    DatoInvalidoError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from .registro_logs import obtener_logger
from .servicios import Servicio, formato_pesos

logger = obtener_logger()


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    PREFIJO = "RES"
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"

    def __init__(self, cliente, servicio, duracion, **parametros):
        super().__init__(self.PREFIJO)
        try:
            # Se comprueba el tipo de los objetos recibidos.
            if not isinstance(cliente, Cliente):
                raise ReservaInvalidaError("La reserva requiere un cliente registrado válido")
            if not isinstance(servicio, Servicio):
                raise ReservaInvalidaError("La reserva requiere un servicio válido")
            self.__cliente = cliente
            self.__servicio = servicio
            # La duración la valida el propio servicio (polimorfismo).
            self.__duracion = servicio.validar_duracion(duracion)
            self.__parametros = dict(parametros)
            self.__estado = self.PENDIENTE
            self.__costo_total = None
        except (DatoInvalidoError, ParametroFaltanteError) as error:
            EntidadBase._revertir_contador(self.PREFIJO)
            # Encadenamiento: se informa un error de reserva causado por el dato.
            raise ReservaInvalidaError(f"No se pudo crear la reserva: {error}") from error
        except ReservaInvalidaError:
            EntidadBase._revertir_contador(self.PREFIJO)
            raise

    # ----- Propiedades de solo lectura -----

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def estado(self):
        return self.__estado

    @property
    def costo_total(self):
        return self.__costo_total

    # ----- Operaciones del ciclo de vida -----

    def confirmar(self):
        """Confirma la reserva si el servicio está disponible y los datos son válidos."""
        if self.__estado != self.PENDIENTE:
            raise OperacionNoPermitidaError("confirmar", self.__estado)
        try:
            # Primero se verifica la disponibilidad del servicio.
            if not self.__servicio.disponible:
                raise ServicioNoDisponibleError(self.__servicio.nombre)
            # Luego, los parámetros propios del servicio (personas, cantidad...).
            self.__servicio.validar_parametros(self.__duracion, **self.__parametros)
        except (DatoInvalidoError, ParametroFaltanteError) as error:
            # Encadenamiento de excepciones.
            raise ReservaInvalidaError(f"No se pudo confirmar {self.id}: {error}") from error
        else:
            # try/except/else: el bloque else solo corre si no hubo errores.
            self.__estado = self.CONFIRMADA
            logger.info("Reserva %s confirmada para %s", self.id, self.__cliente.nombre)
            return True

    def cancelar(self, motivo="Sin motivo"):
        """Cancela la reserva; no se puede cancelar una reserva ya procesada."""
        if self.__estado in (self.PROCESADA, self.CANCELADA):
            raise OperacionNoPermitidaError("cancelar", self.__estado)
        self.__estado = self.CANCELADA
        logger.info("Reserva %s cancelada. Motivo: %s", self.id, motivo)
        return True

    def procesar(self, impuesto=None, descuento=None):
        """Calcula el costo final y marca la reserva como procesada."""
        if self.__estado != self.CONFIRMADA:
            raise OperacionNoPermitidaError("procesar", self.__estado)
        exito = False
        try:
            # Se usa la variante "sobrecargada" de calcular_costo que corresponda.
            costo = self.__servicio.calcular_costo(
                self.__duracion, impuesto, descuento, **self.__parametros
            )
        except CalculoInconsistenteError as error:
            raise ReservaInvalidaError(f"No se pudo procesar {self.id}: {error}") from error
        else:
            self.__costo_total = costo
            self.__estado = self.PROCESADA
            exito = True
            return costo
        finally:
            # try/except/finally: el bloque finally se ejecuta siempre,
            # haya o no error, y deja constancia del intento en el log.
            logger.debug(
                "Intento de procesamiento de %s (impuesto=%s, descuento=%s) -> %s",
                self.id, impuesto, descuento, "exitoso" if exito else "fallido",
            )

    # ----- Métodos sobrescritos de EntidadBase -----

    def validar(self):
        if self.__duracion <= 0:
            raise ReservaInvalidaError("La duración de la reserva debe ser positiva")
        return True

    def describir(self):
        costo = formato_pesos(self.__costo_total) if self.__costo_total is not None else "por calcular"
        return (
            f"{self.id} | {self.__cliente.nombre} | {self.__servicio.nombre} | "
            f"{self.__duracion:g} h | {self.__estado} | Costo: {costo}"
        )
