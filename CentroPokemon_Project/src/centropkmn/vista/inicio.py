import tkinter as tk
from tkinter import ttk
from centropkmn.vista.comun import MODULOS, Pantalla, titulo
from centropkmn.vista.estilos import Tarjeta, FONDO_APP

class Inicio(Pantalla):
    def __init__(self, master, controlador, navegar):
        super().__init__(master, controlador)
        self._navegar = navegar
        titulo(self, "Centro Pokémon — Sistema de Gestión Multi-Sede")
        ttk.Label(self, text="Atención clínica 100% gratuita para entrenadores. Sostenida por donaciones voluntarias por sede.", wraplength=760).pack(anchor="w", pady=(0, 12))
        f_res = tk.Frame(self, bg=FONDO_APP, highlightbackground="#e4dfd6", highlightcolor="#e4dfd6", highlightthickness=2)
        f_res.pack(fill="x", pady=(0, 16))
        self.resumen = ttk.Label(f_res, justify="left", font=("Helvetica", 11))
        self.resumen.pack(fill="both", padx=14, pady=12)
        acceso = ttk.LabelFrame(self, text="Módulos de Gestión de la Sede")
        acceso.pack(fill="x")
        visibles = [(k, v) for k, v in MODULOS if k != "inicio"]
        for idx, (k, v) in enumerate(visibles):
            tarjeta = Tarjeta(acceso, ancho=180, alto=96, texto=v, icono=True, comando=(lambda d=k: self._navegar(d)))
            tarjeta.grid(row=idx // 3, column=idx % 3, sticky="nsew", padx=4, pady=4)
        for c in range(3):
            acceso.columnconfigure(c, weight=1)
        acceso.rowconfigure(0, weight=1)

    def refrescar(self) -> None:
        datos = self.controlador.resumen()
        lineas = [
            f"Sede Actual Seleccionada: {datos['centro_nombre']} (ID: {datos['centro_id']})",
            f"Fondo Recaudado por Donaciones en Sede: ₽{datos['fondos']:,}",
            f"Pacientes Registrados en Sede: {datos['pacientes_totales']}",
            f"Enfermeras Joys Activas en Sede: {datos['enfermeras_activas']}",
            f"Insumos Médicos en Inventario de Sede: {datos['insumos_disponibles']} unidades",
            "", "Estado Actual de Pacientes en Sede:",
        ]
        for e_lbl, cant in datos["estados"].items():
            lineas.append(f"  • {e_lbl}: {cant}")
        self.resumen.configure(text="\n".join(lineas))
