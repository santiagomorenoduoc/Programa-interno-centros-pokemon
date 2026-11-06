import tkinter as tk
from tkinter import ttk
from centropkmn.vista.comun import Pantalla, crear_tabla, informar, mostrar_error, titulo
from centropkmn.vista.estilos import PokeBoton

class Inventario(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        titulo(self, "Almacén de Insumos y Medicinas de la Sede")
        f_med = ttk.LabelFrame(self, text="Registrar Nueva Medicina en la Sede Activa", padding=12)
        f_med.pack(fill="x", pady=(0, 12))
        self.m_nombre, self.m_cant = tk.StringVar(), tk.StringVar(value="10")
        self.m_desc, self.m_puntos = tk.StringVar(value="Restaura puntos de salud"), tk.StringVar(value="30")

        ttk.Label(f_med, text="Nombre").grid(row=0, column=0)
        ttk.Entry(f_med, textvariable=self.m_nombre).grid(row=0, column=1, padx=4)
        ttk.Label(f_med, text="Cantidad Inicial").grid(row=0, column=2)
        ttk.Entry(f_med, textvariable=self.m_cant, width=8).grid(row=0, column=3, padx=4)
        ttk.Label(f_med, text="Puntos Curación").grid(row=0, column=4)
        ttk.Entry(f_med, textvariable=self.m_puntos, width=8).grid(row=0, column=5, padx=4)
        PokeBoton(f_med, "Registrar en Sede", self.reg_medicina).grid(row=0, column=6, padx=8)

        marco, self.tabla = crear_tabla(self, ("id", "categoria", "nombre", "cantidad", "descripcion"), ("ID", "Categoría", "Nombre", "Cantidad Dispon.", "Descripción"), (80, 120, 160, 120, 300))
        marco.pack(fill="both", expand=True)

    def refrescar(self) -> None:
        cid = self.controlador.centro_activo_id
        self.tabla.delete(*self.tabla.get_children())
        for p in self.controlador.listar_productos(cid):
            self.tabla.insert("", "end", iid=p.id, values=(p.id, p.categoria, p.nombre, p.cantidad, p.descripcion))

    def reg_medicina(self) -> None:
        cid = self.controlador.centro_activo_id
        if not cid: mostrar_error(self, "No hay sede seleccionada."); return
        try:
            med = self.controlador.registrar_producto_medicina(cid, self.m_nombre.get(), int(self.m_cant.get()), self.m_desc.get(), int(self.m_puntos.get()))
            informar(self, "Medicina Registrada", f"Medicina {med.nombre} añadida al almacén de la sede {cid}."); self.refrescar()
        except Exception as e: mostrar_error(self, str(e))
