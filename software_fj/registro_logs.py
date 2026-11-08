# -*- coding: utf-8 -*-
"""
Módulo de registro de eventos y errores (logs).

El sistema no usa bases de datos; el único archivo que escribe es el log,
ubicado en la carpeta "logs" del proyecto. Se emplea el módulo estándar
logging para que cada línea quede con fecha, hora, nivel y mensaje.
"""

import logging
from pathlib import Path

# Carpeta raíz del proyecto (un nivel arriba del paquete software_fj).
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
# Carpeta donde se guardan los logs.
CARPETA_LOGS = RAIZ_PROYECTO / "logs"
# Ruta completa del archivo de logs.
ARCHIVO_LOG = CARPETA_LOGS / "software_fj.log"

# Nombre del logger compartido por todos los módulos.
_NOMBRE_LOGGER = "software_fj"


def obtener_logger():
    """Devuelve el logger del sistema, configurándolo la primera vez."""
    logger = logging.getLogger(_NOMBRE_LOGGER)
    # Si ya tiene manejadores, ya fue configurado: se devuelve tal cual.
    if logger.handlers:
        return logger

    # Nivel mínimo que se registra (DEBUG incluye todo).
    logger.setLevel(logging.DEBUG)
    # No se propagan los mensajes al logger raíz para evitar duplicados.
    logger.propagate = False

    try:
        # Se crea la carpeta de logs si todavía no existe.
        CARPETA_LOGS.mkdir(parents=True, exist_ok=True)
        # Manejador que escribe en el archivo, en UTF-8 y añadiendo al final.
        manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
    except OSError:
        # Si no se puede escribir en disco, el sistema no debe detenerse:
        # se usa la consola como respaldo.
        manejador = logging.StreamHandler()

    # Formato: fecha y hora | nivel | mensaje.
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    manejador.setFormatter(formato)
    logger.addHandler(manejador)
    return logger


def leer_log(ultimas_lineas=None):
    """Lee el archivo de logs y devuelve su contenido como texto."""
    try:
        # Se abre el archivo en modo lectura con la misma codificación.
        with open(ARCHIVO_LOG, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        # Todavía no se ha registrado ningún evento.
        return "(El archivo de logs aún no existe)"
    except OSError as error:
        return f"(No fue posible leer el archivo de logs: {error})"
    else:
        # Solo se ejecuta si la lectura fue exitosa.
        if ultimas_lineas:
            lineas = lineas[-ultimas_lineas:]
        return "".join(lineas)
