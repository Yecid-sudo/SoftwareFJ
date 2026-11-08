# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto de la **Fase 4 – Componente práctico: Prácticas simuladas** del curso
**Programación (213023)** de la Universidad Nacional Abierta y a Distancia – UNAD.

- **Estudiante:** Yecid Leonardo Quijano Hernández
- **Grupo:** 213023_641
- **Ejercicio:** 1 – Sistema Integral de Gestión de Clientes, Servicios y Reservas (Anexo 3)

## Descripción

Aplicación orientada a objetos en Python, **sin base de datos**, que gestiona los
clientes, servicios y reservas de la empresa *Software FJ*. La empresa ofrece reservas
de salas, alquiler de equipos y asesorías especializadas. Toda la información se maneja con
objetos y listas en memoria. El único archivo que se escribe es el de **logs**
(`logs/software_fj.log`), donde quedan registrados todos los eventos y errores.

El sistema aplica abstracción, herencia, polimorfismo, encapsulación y **manejo avanzado de
excepciones**. Los errores se controlan sin que la aplicación se detenga.

## Estructura del proyecto

```
SoftwareFJ/
├── main.py                    # Simulación en consola (30 operaciones)
├── app_gui.py                 # Interfaz gráfica con Tkinter
├── software_fj/
│   ├── __init__.py
│   ├── excepciones.py         # Excepciones personalizadas (SoftwareFJError y derivadas)
│   ├── registro_logs.py       # Configuración y lectura del archivo de logs
│   ├── entidad.py             # Clase abstracta EntidadBase
│   ├── cliente.py             # Clase Cliente (encapsulación y validaciones)
│   ├── servicios.py           # Clase abstracta Servicio + 3 servicios especializados
│   ├── reserva.py             # Clase Reserva (confirmar, cancelar, procesar)
│   ├── gestor.py              # SistemaSoftwareFJ: listas internas y operaciones
│   └── simulacion.py          # Escenario de operaciones válidas e inválidas
└── logs/                      # Se crea al ejecutar (software_fj.log)
```

## Diseño orientado a objetos

| Requisito del Anexo 3 | Implementación |
|---|---|
| Clase abstracta para entidades generales | `EntidadBase` (ABC): id único, fecha de creación, `describir()` y `validar()` abstractos |
| Cliente con validaciones y encapsulación | `Cliente`: atributos privados (`__nombre`, `__documento`…) con propiedades que validan; documento enmascarado |
| Clase abstracta Servicio + 3 servicios | `Servicio` → `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| Polimorfismo y métodos sobrescritos | `calcular_costo_base()`, `describir()`, `validar()` y `validar_parametros()` en cada servicio |
| Clase Reserva | `Reserva`: cliente, servicio, duración y estado; `confirmar()`, `cancelar()`, `procesar()` |
| Métodos sobrecargados | `calcular_costo(duracion[, impuesto[, descuento]])` con parámetros opcionales |
| Archivo de logs | `logs/software_fj.log` con fecha, hora, nivel (INFO, WARNING, ERROR, CRITICAL) y mensaje |

## Manejo de excepciones

- **Excepciones personalizadas:** `SoftwareFJError` (base), `DatoInvalidoError`,
  `ParametroFaltanteError`, `ClienteInvalidoError`, `ServicioInvalidoError`,
  `ServicioNoDisponibleError`, `ReservaInvalidaError`, `OperacionNoPermitidaError`,
  `CalculoInconsistenteError`.
- **try/except:** en todas las operaciones del gestor.
- **try/except/else:** `Reserva.confirmar()`, `SistemaSoftwareFJ.registrar_cliente()`, `leer_log()`.
- **try/except/finally:** `Reserva.procesar()` registra siempre el intento de procesamiento.
- **Encadenamiento (`raise ... from ...`):** los errores de datos se convierten en errores de
  cliente, servicio o reserva sin perder la causa original, y el log muestra esa causa.
- **Barrera final:** `ejecutar_seguro()` captura también errores inesperados (por ejemplo,
  `ZeroDivisionError`) y los registra con su traza completa. En la interfaz,
  `report_callback_exception` cumple la misma función.

## Ejecución

Requiere Python 3.8 o superior. No necesita librerías externas.

```bash
# Simulación en consola
python main.py

# Interfaz gráfica
python app_gui.py
```

La simulación ejecuta **30 operaciones**: registros válidos e inválidos de clientes,
creación correcta e incorrecta de servicios, reservas exitosas y fallidas, operaciones no
permitidas, cálculos inconsistentes y un error inesperado. Al final informa que la aplicación
terminó sin interrupciones.
