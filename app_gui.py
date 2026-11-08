# -*- coding: utf-8 -*-
"""
Interfaz gráfica (Tkinter) del Sistema Integral de Gestión de Clientes,
Servicios y Reservas de Software FJ.

Permite registrar clientes, crear servicios, crear / confirmar / cancelar /
procesar reservas, ejecutar la simulación de operaciones y consultar el
archivo de logs. Cualquier error se muestra en la bitácora y se registra en
el log, pero la ventana nunca se cierra por un error.

Uso:
    python app_gui.py
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from software_fj import SistemaSoftwareFJ
from software_fj.registro_logs import ARCHIVO_LOG, leer_log, obtener_logger
from software_fj.simulacion import simular

logger = obtener_logger()

# Colores de la interfaz.
COLOR_PRINCIPAL = "#1F3A5F"
COLOR_OK = "#1B7F3B"
COLOR_ERROR = "#B3261E"


class AplicacionSoftwareFJ(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.title("Software FJ - Gestión de Clientes, Servicios y Reservas")
        self.geometry("1100x700")
        self.minsize(950, 620)

        # Sistema en memoria (sin base de datos).
        self.sistema = SistemaSoftwareFJ()

        # Cualquier excepción no prevista dentro de un evento de Tkinter
        # se captura aquí, se registra y la aplicación sigue abierta.
        self.report_callback_exception = self._error_no_controlado

        self._crear_encabezado()
        self._crear_cuerpo()
        self._actualizar_reloj()
        self._escribir("Sistema iniciado. Toda la información se maneja en memoria.", "info")

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------

    def _crear_encabezado(self):
        barra = tk.Frame(self, bg=COLOR_PRINCIPAL, height=56)
        barra.pack(fill="x")
        tk.Label(barra, text="Software FJ  ·  Sistema Integral de Gestión",
                 bg=COLOR_PRINCIPAL, fg="white", font=("Segoe UI", 15, "bold")
                 ).pack(side="left", padx=14, pady=10)
        # Reloj con la fecha y hora reales del sistema.
        self.lbl_reloj = tk.Label(barra, bg=COLOR_PRINCIPAL, fg="white", font=("Segoe UI", 11))
        self.lbl_reloj.pack(side="right", padx=14)
        ttk.Button(barra, text="Ejecutar simulación (10+ operaciones)",
                   command=self._ejecutar_simulacion).pack(side="right", padx=6)

    def _crear_cuerpo(self):
        cuerpo = ttk.PanedWindow(self, orient="vertical")
        cuerpo.pack(fill="both", expand=True, padx=8, pady=8)

        # Pestañas superiores.
        self.pestanas = ttk.Notebook(cuerpo)
        cuerpo.add(self.pestanas, weight=3)
        self._pestana_clientes()
        self._pestana_servicios()
        self._pestana_reservas()
        self._pestana_logs()

        # Bitácora inferior.
        marco_bitacora = ttk.LabelFrame(cuerpo, text="Bitácora de operaciones")
        cuerpo.add(marco_bitacora, weight=2)
        self.txt_bitacora = tk.Text(marco_bitacora, height=10, font=("Consolas", 10), wrap="word")
        barra = ttk.Scrollbar(marco_bitacora, command=self.txt_bitacora.yview)
        self.txt_bitacora.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.txt_bitacora.pack(fill="both", expand=True)
        self.txt_bitacora.tag_configure("ok", foreground=COLOR_OK)
        self.txt_bitacora.tag_configure("error", foreground=COLOR_ERROR)
        self.txt_bitacora.tag_configure("info", foreground=COLOR_PRINCIPAL)

    @staticmethod
    def _campo(padre, etiqueta, fila, columna=0, ancho=28):
        """Crea una etiqueta y una caja de texto; devuelve la caja."""
        ttk.Label(padre, text=etiqueta).grid(row=fila, column=columna, sticky="w", padx=6, pady=4)
        entrada = ttk.Entry(padre, width=ancho)
        entrada.grid(row=fila, column=columna + 1, sticky="w", padx=6, pady=4)
        return entrada

    @staticmethod
    def _tabla(padre, columnas, anchos):
        """Crea una tabla (Treeview) con las columnas indicadas."""
        tabla = ttk.Treeview(padre, columns=columnas, show="headings", height=8)
        for col, ancho in zip(columnas, anchos):
            tabla.heading(col, text=col)
            tabla.column(col, width=ancho, anchor="w")
        return tabla

    def _pestana_clientes(self):
        marco = ttk.Frame(self.pestanas)
        self.pestanas.add(marco, text="Clientes")
        formulario = ttk.LabelFrame(marco, text="Registrar cliente")
        formulario.pack(side="left", fill="y", padx=6, pady=6)
        self.e_nombre = self._campo(formulario, "Nombre completo:", 0)
        self.e_documento = self._campo(formulario, "Documento:", 1)
        self.e_correo = self._campo(formulario, "Correo:", 2)
        self.e_telefono = self._campo(formulario, "Celular:", 3)
        ttk.Button(formulario, text="Registrar", command=self._registrar_cliente
                   ).grid(row=4, column=1, sticky="e", padx=6, pady=8)
        self.t_clientes = self._tabla(marco, ("ID", "Nombre", "Documento", "Correo", "Celular"),
                                      (70, 180, 110, 200, 110))
        self.t_clientes.pack(side="left", fill="both", expand=True, padx=6, pady=6)

    def _pestana_servicios(self):
        marco = ttk.Frame(self.pestanas)
        self.pestanas.add(marco, text="Servicios")
        formulario = ttk.LabelFrame(marco, text="Crear servicio")
        formulario.pack(side="left", fill="y", padx=6, pady=6)
        ttk.Label(formulario, text="Tipo:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.cb_tipo = ttk.Combobox(formulario, state="readonly", width=25,
                                    values=["sala", "equipo", "asesoria"])
        self.cb_tipo.current(0)
        self.cb_tipo.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        self.cb_tipo.bind("<<ComboboxSelected>>", lambda _e: self._ajustar_campos_servicio())
        self.e_srv_nombre = self._campo(formulario, "Nombre:", 1)
        self.e_srv_tarifa = self._campo(formulario, "Tarifa por hora:", 2)
        self.lbl_extra1 = ttk.Label(formulario)
        self.lbl_extra1.grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.e_extra1 = ttk.Entry(formulario, width=28)
        self.e_extra1.grid(row=3, column=1, sticky="w", padx=6, pady=4)
        self.lbl_extra2 = ttk.Label(formulario)
        self.lbl_extra2.grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.e_extra2 = ttk.Entry(formulario, width=28)
        self.e_extra2.grid(row=4, column=1, sticky="w", padx=6, pady=4)
        ttk.Button(formulario, text="Crear servicio", command=self._crear_servicio
                   ).grid(row=5, column=1, sticky="e", padx=6, pady=8)
        ttk.Button(formulario, text="Cambiar disponibilidad (seleccionado)",
                   command=self._alternar_disponibilidad
                   ).grid(row=6, column=0, columnspan=2, sticky="we", padx=6, pady=4)
        self._ajustar_campos_servicio()
        self.t_servicios = self._tabla(marco, ("ID", "Tipo", "Nombre", "Tarifa/h", "Detalle", "Estado"),
                                       (70, 80, 190, 90, 220, 100))
        self.t_servicios.pack(side="left", fill="both", expand=True, padx=6, pady=6)

    def _pestana_reservas(self):
        marco = ttk.Frame(self.pestanas)
        self.pestanas.add(marco, text="Reservas")
        formulario = ttk.LabelFrame(marco, text="Gestionar reservas")
        formulario.pack(side="left", fill="y", padx=6, pady=6)
        ttk.Label(formulario, text="Cliente:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.cb_cliente = ttk.Combobox(formulario, state="readonly", width=25)
        self.cb_cliente.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(formulario, text="Servicio:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.cb_servicio = ttk.Combobox(formulario, state="readonly", width=25)
        self.cb_servicio.grid(row=1, column=1, sticky="w", padx=6, pady=4)
        self.e_duracion = self._campo(formulario, "Duración (horas):", 2)
        self.e_cantidad = self._campo(formulario, "Personas / cantidad:", 3)
        ttk.Button(formulario, text="Crear reserva", command=self._crear_reserva
                   ).grid(row=4, column=1, sticky="e", padx=6, pady=6)
        ttk.Separator(formulario).grid(row=5, column=0, columnspan=2, sticky="we", pady=6)
        self.e_impuesto = self._campo(formulario, "Impuesto (0 - 0.30):", 6)
        self.e_impuesto.insert(0, "0.19")
        self.e_descuento = self._campo(formulario, "Descuento (0 - 0.50):", 7)
        self.e_descuento.insert(0, "0")
        botones = ttk.Frame(formulario)
        botones.grid(row=8, column=0, columnspan=2, pady=6)
        ttk.Button(botones, text="Confirmar", command=lambda: self._accion_reserva("confirmar")).pack(side="left", padx=3)
        ttk.Button(botones, text="Procesar", command=lambda: self._accion_reserva("procesar")).pack(side="left", padx=3)
        ttk.Button(botones, text="Cancelar", command=lambda: self._accion_reserva("cancelar")).pack(side="left", padx=3)
        ttk.Label(formulario, text="(Seleccione la reserva en la tabla)", foreground="gray"
                  ).grid(row=9, column=0, columnspan=2)
        self.t_reservas = self._tabla(marco, ("ID", "Cliente", "Servicio", "Horas", "Estado", "Costo"),
                                      (70, 160, 200, 60, 110, 110))
        self.t_reservas.pack(side="left", fill="both", expand=True, padx=6, pady=6)

    def _pestana_logs(self):
        marco = ttk.Frame(self.pestanas)
        self.pestanas.add(marco, text="Archivo de logs")
        ttk.Label(marco, text=f"Archivo: {ARCHIVO_LOG}").pack(anchor="w", padx=6, pady=4)
        ttk.Button(marco, text="Actualizar", command=self._mostrar_logs).pack(anchor="w", padx=6)
        self.txt_logs = tk.Text(marco, font=("Consolas", 9), wrap="none")
        self.txt_logs.pack(fill="both", expand=True, padx=6, pady=6)
        self.pestanas.bind("<<NotebookTabChanged>>", lambda _e: self._mostrar_logs())

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def _actualizar_reloj(self):
        self.lbl_reloj.config(text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
        self.after(1000, self._actualizar_reloj)

    def _escribir(self, texto, etiqueta=None):
        hora = datetime.now().strftime("%H:%M:%S")
        self.txt_bitacora.insert("end", f"[{hora}] {texto}\n", etiqueta)
        self.txt_bitacora.see("end")

    def _mostrar_resultado(self, resultado):
        self._escribir(resultado.mensaje, "ok" if resultado.exito else "error")
        self._refrescar_tablas()

    @staticmethod
    def _numero(texto, por_defecto=None):
        """Convierte el texto a número; si está vacío devuelve el valor por defecto."""
        texto = texto.strip().replace(",", ".")
        if texto == "":
            return por_defecto
        try:
            return float(texto)
        except ValueError:
            # Se devuelve el texto tal cual para que la validación del
            # sistema genere el error correspondiente y quede en el log.
            return texto

    def _refrescar_tablas(self):
        for tabla in (self.t_clientes, self.t_servicios, self.t_reservas):
            tabla.delete(*tabla.get_children())
        for c in self.sistema.clientes:
            self.t_clientes.insert("", "end", values=(c.id, c.nombre, c.documento_enmascarado(),
                                                      c.correo, c.telefono))
        for s in self.sistema.servicios:
            tipo = type(s).__name__
            detalle = s.describir().split("|")[-1].strip()
            estado = "Disponible" if s.disponible else "No disponible"
            self.t_servicios.insert("", "end", values=(s.id, tipo, s.nombre,
                                                       f"${s.tarifa_hora:,.0f}".replace(",", "."),
                                                       detalle, estado))
        for r in self.sistema.reservas:
            costo = "-" if r.costo_total is None else f"${r.costo_total:,.0f}".replace(",", ".")
            self.t_reservas.insert("", "end", values=(r.id, r.cliente.nombre, r.servicio.nombre,
                                                      f"{r.duracion:g}", r.estado, costo))
        self.cb_cliente["values"] = [f"{c.id} - {c.nombre}" for c in self.sistema.clientes]
        self.cb_servicio["values"] = [f"{s.id} - {s.nombre}" for s in self.sistema.servicios]

    def _mostrar_logs(self):
        self.txt_logs.delete("1.0", "end")
        self.txt_logs.insert("end", leer_log(ultimas_lineas=300))
        self.txt_logs.see("end")

    def _error_no_controlado(self, tipo, valor, traza):
        """Última barrera de la interfaz: registra el error y no cierra la ventana."""
        logger.critical("Error no controlado en la interfaz: %s", valor, exc_info=(tipo, valor, traza))
        self._escribir(f"Error inesperado controlado: {tipo.__name__}: {valor}", "error")

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _registrar_cliente(self):
        resultado = self.sistema.registrar_cliente(
            self.e_nombre.get(), self.e_documento.get(), self.e_correo.get(), self.e_telefono.get()
        )
        self._mostrar_resultado(resultado)
        if resultado.exito:
            for e in (self.e_nombre, self.e_documento, self.e_correo, self.e_telefono):
                e.delete(0, "end")

    def _ajustar_campos_servicio(self):
        etiquetas = {
            "sala": ("Capacidad (personas):", "(no aplica)"),
            "equipo": ("Tipo de equipo:", "Unidades disponibles:"),
            "asesoria": ("Área:", "Nivel (junior/senior/experto):"),
        }
        e1, e2 = etiquetas[self.cb_tipo.get()]
        self.lbl_extra1.config(text=e1)
        self.lbl_extra2.config(text=e2)
        self.e_extra2.config(state="disabled" if self.cb_tipo.get() == "sala" else "normal")

    def _crear_servicio(self):
        tipo = self.cb_tipo.get()
        datos = {"nombre": self.e_srv_nombre.get(),
                 "tarifa_hora": self._numero(self.e_srv_tarifa.get())}
        if tipo == "sala":
            datos["capacidad"] = self._numero(self.e_extra1.get())
        elif tipo == "equipo":
            datos["tipo_equipo"] = self.e_extra1.get()
            datos["unidades"] = self._numero(self.e_extra2.get())
        else:
            datos["area"] = self.e_extra1.get()
            datos["nivel"] = self.e_extra2.get() or "junior"
        self._mostrar_resultado(self.sistema.crear_servicio(tipo, **datos))

    def _alternar_disponibilidad(self):
        seleccion = self.t_servicios.selection()
        if not seleccion:
            messagebox.showinfo("Software FJ", "Seleccione un servicio en la tabla.")
            return
        id_servicio = self.t_servicios.item(seleccion[0], "values")[0]
        servicio = self.sistema.buscar_servicio(id_servicio)
        self._mostrar_resultado(self.sistema.cambiar_disponibilidad(id_servicio, not servicio.disponible))

    def _crear_reserva(self):
        id_cliente = self.cb_cliente.get().split(" - ")[0]
        id_servicio = self.cb_servicio.get().split(" - ")[0]
        parametros = {}
        cantidad = self._numero(self.e_cantidad.get())
        if cantidad is not None:
            # Se envía el parámetro con el nombre que espera cada servicio.
            parametros = {"personas": cantidad, "cantidad": cantidad}
        resultado = self.sistema.crear_reserva(id_cliente, id_servicio,
                                               self._numero(self.e_duracion.get()), **parametros)
        self._mostrar_resultado(resultado)

    def _accion_reserva(self, accion):
        seleccion = self.t_reservas.selection()
        if not seleccion:
            messagebox.showinfo("Software FJ", "Seleccione una reserva en la tabla.")
            return
        id_reserva = self.t_reservas.item(seleccion[0], "values")[0]
        if accion == "confirmar":
            resultado = self.sistema.confirmar_reserva(id_reserva)
        elif accion == "cancelar":
            resultado = self.sistema.cancelar_reserva(id_reserva)
        else:
            resultado = self.sistema.procesar_reserva(
                id_reserva, self._numero(self.e_impuesto.get()), self._numero(self.e_descuento.get())
            )
        self._mostrar_resultado(resultado)

    def _ejecutar_simulacion(self):
        self._escribir("===== Inicio de la simulación de operaciones =====", "info")

        def imprimir(linea):
            etiqueta = "error" if "[ERROR]" in linea or "-> [SFJ" in linea or "inesperado" in linea else None
            if "[OK" in linea:
                etiqueta = "ok"
            self._escribir(linea, etiqueta)

        simular(self.sistema, imprimir)
        self._refrescar_tablas()
        self._escribir("===== Fin de la simulación =====", "info")


if __name__ == "__main__":
    AplicacionSoftwareFJ().mainloop()
