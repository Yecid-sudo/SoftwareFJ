# -*- coding: utf-8 -*-
"""
Módulo de excepciones personalizadas del sistema Software FJ.

Todas las excepciones del dominio heredan de SoftwareFJError, de modo que
el código cliente puede capturar cualquier error propio del sistema con un
único bloque except, o bien capturar un tipo específico cuando necesita
reaccionar de forma distinta según el problema.
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema Software FJ."""

    def __init__(self, mensaje, codigo="SFJ-000"):
        # Se llama al constructor de Exception para conservar el mensaje.
        super().__init__(mensaje)
        # Código corto que identifica el tipo de error en el archivo de logs.
        self.codigo = codigo
        # Se guarda el mensaje como atributo para mostrarlo en la interfaz.
        self.mensaje = mensaje

    def __str__(self):
        # Representación legible: "[código] mensaje".
        return f"[{self.codigo}] {self.mensaje}"


class DatoInvalidoError(SoftwareFJError):
    """Se lanza cuando un dato no cumple el formato o el rango esperado."""

    def __init__(self, campo, valor, motivo):
        # Se guarda el campo que falló para facilitar la depuración.
        self.campo = campo
        self.valor = valor
        super().__init__(f"Dato inválido en '{campo}' ({valor!r}): {motivo}", "SFJ-100")


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio."""

    def __init__(self, parametro, contexto=""):
        self.parametro = parametro
        detalle = f" en {contexto}" if contexto else ""
        super().__init__(f"Falta el parámetro obligatorio '{parametro}'{detalle}", "SFJ-110")


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando no es posible registrar o usar un cliente."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "SFJ-200")


class ServicioInvalidoError(SoftwareFJError):
    """Se lanza cuando un servicio se crea con datos incorrectos."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "SFJ-300")


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio que no está disponible."""

    def __init__(self, nombre_servicio):
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible", "SFJ-310")


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva no se puede crear, confirmar o procesar."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "SFJ-400")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando una operación no es válida para el estado actual."""

    def __init__(self, operacion, estado):
        self.operacion = operacion
        self.estado = estado
        super().__init__(
            f"La operación '{operacion}' no está permitida en estado '{estado}'", "SFJ-410"
        )


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos produce un resultado incoherente."""

    def __init__(self, mensaje):
        super().__init__(mensaje, "SFJ-500")
