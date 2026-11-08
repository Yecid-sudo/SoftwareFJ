# -*- coding: utf-8 -*-
"""
Módulo de simulación de operaciones del sistema Software FJ.

Ejecuta más de 10 operaciones completas, combinando registros válidos e
inválidos de clientes, creación correcta e incorrecta de servicios y
reservas exitosas y fallidas, para demostrar que la aplicación continúa
funcionando ante errores. Lo usan main.py (consola) y app_gui.py (Tkinter).
"""

from .gestor import Resultado
from .servicios import formato_pesos


def promedio_facturado(sistema):
    """Promedio facturado por reserva procesada.

    Si se invoca antes de procesar alguna reserva, ocurre una división por
    cero (ZeroDivisionError). Es un error inesperado, no del dominio, que
    se usa para demostrar la barrera final ejecutar_seguro().
    """
    procesadas = [r for r in sistema.reservas if r.costo_total is not None]
    total = sum(r.costo_total for r in procesadas)
    return total / len(procesadas)


def _id(resultado):
    """Devuelve el id del objeto creado o un id inexistente si la operación falló."""
    return resultado.objeto.id if resultado.exito and resultado.objeto else "NO-EXISTE"


def simular(sistema, imprimir=print):
    """Ejecuta la simulación sobre el sistema dado y devuelve los resultados.

    imprimir es la función que recibe cada línea de texto (print en consola
    o un método que escribe en la bitácora de la interfaz gráfica).
    """
    resultados = []

    def op(descripcion, funcion, *args, **kwargs):
        # Cada operación pasa por la barrera ejecutar_seguro() del gestor.
        resultado = sistema.ejecutar_seguro(descripcion, funcion, *args, **kwargs)
        # Si la función devolvió un número (no un Resultado), se adapta.
        if not isinstance(resultado, Resultado):
            resultado = Resultado(True, f"Valor obtenido: {formato_pesos(resultado)}", resultado)
        resultados.append((descripcion, resultado))
        marca = "OK   " if resultado.exito else "ERROR"
        imprimir(f"{len(resultados):>2}. [{marca}] {descripcion}")
        imprimir(f"     -> {resultado.mensaje}")
        return resultado

    # ---------------- Clientes ----------------
    c1 = op("Registrar cliente válido (Ana María Torres)", sistema.registrar_cliente,
            "Ana María Torres", "1002345678", "ana.torres@correo.com", "3104567890")
    c2 = op("Registrar cliente válido (Carlos Pérez)", sistema.registrar_cliente,
            "carlos   pérez", "80123456", "CPEREZ@empresa.co", "3201234567")
    op("Registrar cliente con correo inválido", sistema.registrar_cliente,
       "Luis Gómez", "1098765432", "luis.gomez@", "3157778899")
    op("Registrar cliente sin documento (parámetro faltante)", sistema.registrar_cliente,
       "Marta Ruiz", None, "marta@correo.com", "3001112233")
    op("Registrar cliente con documento duplicado", sistema.registrar_cliente,
       "Pedro Díaz", "1002345678", "pedro@correo.com", "3112223344")

    # ---------------- Servicios ----------------
    s1 = op("Crear servicio válido: Sala de juntas", sistema.crear_servicio, "sala",
            nombre="Sala de juntas", tarifa_hora=45000, capacidad=10)
    s2 = op("Crear servicio válido: Alquiler de portátiles", sistema.crear_servicio, "equipo",
            nombre="Alquiler de portátiles", tarifa_hora=12000, tipo_equipo="Portátil", unidades=5)
    s3 = op("Crear servicio válido: Asesoría en ciberseguridad", sistema.crear_servicio, "asesoria",
            nombre="Asesoría en ciberseguridad", tarifa_hora=80000, area="Ciberseguridad",
            nivel="senior")
    op("Crear servicio con tarifa negativa", sistema.crear_servicio, "sala",
       nombre="Auditorio", tarifa_hora=-20000, capacidad=80)
    op("Crear servicio de un tipo inexistente", sistema.crear_servicio, "transporte",
       nombre="Bus", tarifa_hora=10000)
    op("Crear asesoría con nivel no válido", sistema.crear_servicio, "asesoria",
       nombre="Asesoría en redes", tarifa_hora=60000, area="Redes", nivel="maestro")

    id_c1, id_c2 = _id(c1), _id(c2)
    id_s1, id_s2, id_s3 = _id(s1), _id(s2), _id(s3)

    # Error inesperado (división por cero) controlado por la barrera final.
    op("Calcular promedio facturado sin reservas procesadas (error inesperado)",
       promedio_facturado, sistema)

    # ---------------- Reservas ----------------
    r1 = op("Crear reserva de sala (3 h, 8 personas)", sistema.crear_reserva,
            id_c1, id_s1, 3, personas=8)
    op("Confirmar reserva de sala", sistema.confirmar_reserva, _id(r1))
    op("Procesar reserva de sala con IVA y 10 % de descuento", sistema.procesar_reserva,
       _id(r1), 0.19, 0.10)
    op("Cancelar una reserva ya procesada (no permitido)", sistema.cancelar_reserva, _id(r1))

    r2 = op("Crear reserva de 8 portátiles (solo hay 5)", sistema.crear_reserva,
            id_c2, id_s2, 4, cantidad=8)
    op("Confirmar reserva con cantidad mayor a la disponible", sistema.confirmar_reserva, _id(r2))

    op("Crear reserva con duración inválida (20 h)", sistema.crear_reserva, id_c2, id_s3, 20)
    op("Crear reserva para un cliente inexistente", sistema.crear_reserva, "CLI-999", id_s3, 2)

    r3 = op("Crear reserva de asesoría (2 h)", sistema.crear_reserva, id_c2, id_s3, 2)
    op("Procesar asesoría sin confirmar (no permitido)", sistema.procesar_reserva, _id(r3))
    op("Confirmar reserva de asesoría", sistema.confirmar_reserva, _id(r3))
    op("Procesar asesoría con 70 % de descuento (cálculo inconsistente)",
       sistema.procesar_reserva, _id(r3), 0.19, 0.70)
    op("Procesar asesoría solo con IVA", sistema.procesar_reserva, _id(r3), 0.19)

    op("Marcar alquiler de portátiles como no disponible", sistema.cambiar_disponibilidad,
       id_s2, False)
    r4 = op("Crear reserva de 2 portátiles", sistema.crear_reserva, id_c1, id_s2, 2, cantidad=2)
    op("Confirmar reserva de un servicio no disponible", sistema.confirmar_reserva, _id(r4))
    op("Cancelar reserva pendiente de portátiles", sistema.cancelar_reserva, _id(r4),
       "Servicio en mantenimiento")

    op("Calcular promedio facturado por reserva procesada", promedio_facturado, sistema)

    # ---------------- Resumen ----------------
    exitosas = sum(1 for _, r in resultados if r.exito)
    imprimir("-" * 72)
    imprimir(f" Operaciones ejecutadas: {len(resultados)} | Exitosas: {exitosas} | "
             f"Errores controlados: {len(resultados) - exitosas}")
    imprimir(" La aplicación terminó la simulación sin interrupciones.")
    return resultados
