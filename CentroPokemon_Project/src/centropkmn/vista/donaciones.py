import tkinter as tk
from tkinter import ttk
from centropkmn.vista.comun import Pantalla, crear_tabla, informar, mostrar_error, titulo

class Donaciones(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        titulo(self, "Módulo de Donaciones (Sostenibilidad de la Sede)")

        f_mon = ttk.LabelFrame(self, text="1. Donación Monetaria (Pokedólares ₽)", padding=12)
        f_mon.pack(fill="x", pady=(0, 12))
        self.d_nombre, self.d_monto, self.d_medio = tk.StringVar(), tk.StringVar(value="500"), tk.StringVar(value="Efectivo")
        ttk.Label(f_mon, text="Donante").grid(row=0, column=0)
        ttk.Entry(f_mon, textvariable=self.d_nombre).grid(row=0, column=1, padx=4)
        ttk.Label(f_mon, text="Monto (₽)").grid(row=0, column=2)
        ttk.Entry(f_mon, textvariable=self.d_monto).grid(row=0, column=3, padx=4)
        ttk.Button(f_mon, text="Donar Pokedólares a la Sede", command=self.donar_monetaria).grid(row=0, column=4, padx=4)

        f_obj = ttk.LabelFrame(self, text="2. Donación de Objetos al Almacén de la Sede", padding=12)
        f_obj.pack(fill="x", pady=(0, 12))
        self.do_nombre, self.do_cant = tk.StringVar(), tk.StringVar(value="5")
        self.combo_prod = ttk.Combobox(f_obj, state="readonly")
        ttk.Label(f_obj, text="Donante").grid(row=0, column=0)
        ttk.Entry(f_obj, textvariable=self.do_nombre).grid(row=0, column=1, padx=4)
        ttk.Label(f_obj, text="Insumo Sede").grid(row=0, column=2)
        self.combo_prod.grid(row=0, column=3, padx=4)
        ttk.Label(f_obj, text="Cantidad").grid(row=0, column=4)
        ttk.Entry(f_obj, textvariable=self.do_cant, width=6).grid(row=0, column=5, padx=4)
        ttk.Button(f_obj, text="Donar Objetos a Sede", command=self.donar_objetos).grid(row=0, column=6, padx=4)

        marco, self.tabla = crear_tabla(self, ("ref", "tipo", "mensaje"), ("Referencia", "Tipo", "Detalle de la Donación"), (120, 120, 480))
        marco.pack(fill="both", expand=True)

    def refrescar(self) -> None:
        cid = self.controlador.centro_activo_id
        prods = self.controlador.listar_productos(cid)
        self.combo_prod["values"] = [f"{p.id} - {p.nombre}" for p in prods]
        if self.combo_prod["values"]: self.combo_prod.current(0)
        else: self.combo_prod.set("")
        self.tabla.delete(*self.tabla.get_children())
        for d in self.controlador.listar_donaciones(cid):
            self.tabla.insert("", "end", values=(d.get("referencia", "N/A"), d.get("tipo", "N/A"), d.get("mensaje", "")))

    def donar_monetaria(self) -> None:
        cid = self.controlador.centro_activo_id
        if not cid: mostrar_error(self, "No hay sede seleccionada."); return
        try:
            res = self.controlador.registrar_donacion_monetaria(cid, self.d_nombre.get() or "Donante Anónimo", int(self.d_monto.get()), self.d_medio.get())
            informar(self, "Donación Recibida", res.mensaje); self.refrescar()
        except Exception as e: mostrar_error(self, str(e))

    def donar_objetos(self) -> None:
        cid = self.controlador.centro_activo_id
        if not cid: mostrar_error(self, "No hay sede seleccionada."); return
        if not self.combo_prod.get(): mostrar_error(self, "Seleccione un insumo de la sede."); return
        try:
            p_id = self.combo_prod.get().split(" - ")[0]
            res = self.controlador.registrar_donacion_objetos(cid, self.do_nombre.get() or "Donante Anónimo", p_id, int(self.do_cant.get()))
            informar(self, "Insumos Ingresados", res.mensaje); self.refrescar()
        except Exception as e: mostrar_error(self, str(e))
