from tkinter import ttk
from centropkmn.vista.comun import MODULOS, Pantalla, titulo

class Inicio(Pantalla):
    def __init__(self, master, controlador, navegar):
        super().__init__(master, controlador)
        self._navegar = navegar
        titulo(self, "Centro Pokémon — Sistema de Gestión Multi-Sede")
        ttk.Label(self, text="Atención clínica 100% gratuita para entrenadores. Sostenida por donaciones voluntarias por sede.", wraplength=760).pack(anchor="w", pady=(0, 12))
        self.resumen = ttk.Label(self, justify="left", font=("Helvetica", 11))
        self.resumen.pack(anchor="w", pady=(0, 16))
        acceso = ttk.LabelFrame(self, text="Módulos de Gestión de la Sede", padding=12)
        acceso.pack(fill="x")
        visibles = [(k, v) for k, v in MODULOS if k != "inicio"]
        for idx, (k, v) in enumerate(visibles):
            ttk.Button(acceso, text=v, command=lambda d=k: self._navegar(d)).grid(row=idx // 3, column=idx % 3, sticky="ew", padx=4, pady=4)
        for c in range(3): acceso.columnconfigure(c, weight=1)

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
