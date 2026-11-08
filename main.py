# -*- coding: utf-8 -*-
"""
Punto de entrada en consola del Sistema Integral de Gestión de Clientes,
Servicios y Reservas de Software FJ.

Ejecuta la simulación de operaciones, muestra el estado final de las
listas internas y las últimas líneas del archivo de logs.

Uso:
    python main.py          -> simulación en consola
    python app_gui.py       -> interfaz gráfica (Tkinter)
"""

from datetime import datetime

from software_fj import SistemaSoftwareFJ
from software_fj.registro_logs import ARCHIVO_LOG, leer_log
from software_fj.simulacion import simular


def main():
    print("=" * 72)
    print(" SOFTWARE FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas")
    print(f" Fecha y hora de ejecución: {datetime.now():%d/%m/%Y %H:%M:%S}")
    print("=" * 72)

    # Se crea el sistema (toda la información vive en listas, sin base de datos).
    sistema = SistemaSoftwareFJ()
    simular(sistema)

    # Estado final de las listas internas.
    print("=" * 72)
    print(" Clientes registrados:")
    for cliente in sistema.clientes:
        print("   ", cliente)
    print(" Servicios:")
    for servicio in sistema.servicios:
        print("   ", servicio)
    print(" Reservas:")
    for reserva in sistema.reservas:
        print("   ", reserva)
    print("=" * 72)
    print(f" Últimas líneas del archivo de logs ({ARCHIVO_LOG}):")
    print(leer_log(ultimas_lineas=10))


if __name__ == "__main__":
    main()
