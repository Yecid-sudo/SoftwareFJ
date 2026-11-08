# -*- coding: utf-8 -*-
"""
Módulo con el gestor central del sistema (SistemaSoftwareFJ).

Mantiene en listas internas los clientes, servicios y reservas (no se usa
base de datos). Cada operación se ejecuta dentro de bloques try/except
para que ningún error detenga la aplicación: los errores se registran en
el archivo de logs y se devuelven como un objeto Resultado.
"""

from dataclasses import dataclass
from typing import Any, Optional

from .cliente import Cliente
from .excepciones import (
    ClienteInvalidoError,
    DatoInvalidoError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    SoftwareFJError,
)
from .registro_logs import obtener_logger
from .reserva import Reserva
from .servicios import TIPOS_SERVICIO, formato_pesos

logger = obtener_logger()


@dataclass
class Resultado:
    """Resultado de una operación del sistema."""

    exito: bool
    mensaje: str
    objeto: Optional[Any] = None


class SistemaSoftwareFJ:
    """Gestiona clientes, servicios y reservas mediante listas internas."""

    def __init__(self):
        # Listas internas (la información vive solo en memoria).
        self._clientes = []
        self._servicios = []
        self._reservas = []
        logger.info("=== Sistema Software FJ iniciado ===")

    # ----- Consultas -----

    @property
    def clientes(self):
        # Se devuelve una copia para que nadie modifique la lista interna.
        return list(self._clientes)

    @property
    def servicios(self):
        return list(self._servicios)

    @property
    def reservas(self):
        return list(self._reservas)

    def buscar_cliente(self, id_cliente):
        for cliente in self._clientes:
            if cliente.id == id_cliente:
                return cliente
        raise ClienteInvalidoError(f"No existe un cliente con id '{id_cliente}'")

    def buscar_servicio(self, id_servicio):
        for servicio in self._servicios:
            if servicio.id == id_servicio:
                return servicio
        raise ServicioInvalidoError(f"No existe un servicio con id '{id_servicio}'")

    def buscar_reserva(self, id_reserva):
        for reserva in self._reservas:
            if reserva.id == id_reserva:
                return reserva
        raise ReservaInvalidaError(f"No existe una reserva con id '{id_reserva}'")

    # ----- Utilidad interna para registrar fallos -----

    @staticmethod
    def _registrar_fallo(operacion, error):
        """Escribe el error en el log, incluida su causa si fue encadenado."""
        causa = error.__cause__
        if causa is not None:
            logger.error("%s -> %s | Causa original: %s: %s",
                         operacion, error, type(causa).__name__, causa)
        else:
            logger.error("%s -> %s", operacion, error)
        return Resultado(False, str(error))

    # ----- Operaciones con clientes -----

    def registrar_cliente(self, nombre=None, documento=None, correo=None, telefono=None):
        operacion = "Registrar cliente"
        try:
            # No se admiten dos clientes con el mismo documento.
            if documento and any(c.documento == str(documento).strip() for c in self._clientes):
                raise ClienteInvalidoError(f"Ya existe un cliente con documento {documento}")
            cliente = Cliente(nombre, documento, correo, telefono)
        except (DatoInvalidoError, ParametroFaltanteError) as error:
            # Encadenamiento: el error de dato se envuelve en un error de cliente.
            try:
                raise ClienteInvalidoError(f"Registro rechazado: {error.mensaje}") from error
            except ClienteInvalidoError as envuelto:
                return self._registrar_fallo(operacion, envuelto)
        except SoftwareFJError as error:
            return self._registrar_fallo(operacion, error)
        else:
            self._clientes.append(cliente)
            logger.info("Cliente registrado: %s", cliente.describir())
            return Resultado(True, f"Cliente registrado: {cliente.id} - {cliente.nombre}", cliente)

    # ----- Operaciones con servicios -----

    def crear_servicio(self, tipo, **datos):
        operacion = f"Crear servicio '{tipo}'"
        try:
            clase = TIPOS_SERVICIO.get(str(tipo).lower())
            if clase is None:
                raise ServicioInvalidoError(
                    f"Tipo de servicio desconocido: '{tipo}'. Opciones: {list(TIPOS_SERVICIO)}"
                )
            try:
                servicio = clase(**datos)
            except TypeError as error:
                # Parámetros faltantes o sobrantes en el constructor.
                raise ServicioInvalidoError(f"Parámetros incorrectos para '{tipo}'") from error
        except SoftwareFJError as error:
            return self._registrar_fallo(operacion, error)
        else:
            self._servicios.append(servicio)
            logger.info("Servicio creado: %s", servicio.describir())
            return Resultado(True, f"Servicio creado: {servicio.id} - {servicio.nombre}", servicio)

    def cambiar_disponibilidad(self, id_servicio, disponible):
        try:
            servicio = self.buscar_servicio(id_servicio)
        except SoftwareFJError as error:
            return self._registrar_fallo("Cambiar disponibilidad", error)
        servicio.cambiar_disponibilidad(disponible)
        estado = "disponible" if disponible else "no disponible"
        logger.warning("Servicio %s marcado como %s", servicio.id, estado)
        return Resultado(True, f"{servicio.nombre} ahora está {estado}", servicio)

    # ----- Operaciones con reservas -----

    def crear_reserva(self, id_cliente, id_servicio, duracion, **parametros):
        operacion = "Crear reserva"
        try:
            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(id_servicio)
            reserva = Reserva(cliente, servicio, duracion, **parametros)
        except SoftwareFJError as error:
            return self._registrar_fallo(operacion, error)
        else:
            self._reservas.append(reserva)
            logger.info("Reserva creada: %s", reserva.describir())
            return Resultado(True, f"Reserva creada: {reserva.id} (pendiente)", reserva)

    def confirmar_reserva(self, id_reserva):
        try:
            reserva = self.buscar_reserva(id_reserva)
            reserva.confirmar()
        except SoftwareFJError as error:
            return self._registrar_fallo(f"Confirmar {id_reserva}", error)
        return Resultado(True, f"Reserva {reserva.id} confirmada", reserva)

    def cancelar_reserva(self, id_reserva, motivo="Solicitud del cliente"):
        try:
            reserva = self.buscar_reserva(id_reserva)
            reserva.cancelar(motivo)
        except SoftwareFJError as error:
            return self._registrar_fallo(f"Cancelar {id_reserva}", error)
        return Resultado(True, f"Reserva {reserva.id} cancelada", reserva)

    def procesar_reserva(self, id_reserva, impuesto=None, descuento=None):
        try:
            reserva = self.buscar_reserva(id_reserva)
            costo = reserva.procesar(impuesto, descuento)
        except SoftwareFJError as error:
            return self._registrar_fallo(f"Procesar {id_reserva}", error)
        logger.info("Reserva %s procesada. Total: %s", reserva.id, formato_pesos(costo))
        return Resultado(True, f"Reserva {reserva.id} procesada. Total: {formato_pesos(costo)}", reserva)

    def ejecutar_seguro(self, descripcion, funcion, *args, **kwargs):
        """Ejecuta cualquier función capturando también errores inesperados.

        Es la última barrera: si ocurre un error que no es del dominio
        (por ejemplo, un fallo de programación), se registra con su traza
        completa y la aplicación sigue funcionando.
        """
        try:
            return funcion(*args, **kwargs)
        except SoftwareFJError as error:
            return self._registrar_fallo(descripcion, error)
        except Exception as error:  # noqa: BLE001 - barrera final intencional
            logger.critical("Error inesperado en '%s': %s", descripcion, error, exc_info=True)
            return Resultado(False, f"Error inesperado controlado: {type(error).__name__}: {error}")
