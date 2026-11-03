import tkinter as tk
from tkinter import ttk
from centropkmn.vista.comun import Pantalla, crear_tabla, informar, mostrar_error, titulo

class Tratamiento(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        titulo(self, "Atención y Curación Médica (Sede Activa)")
        marco, self.tabla = crear_tabla(self, ("id", "nombre", "especie", "hp", "estado", "sintomas"), ("ID Paciente", "Mote", "Especie", "HP Actual / Max", "Estado Clínico", "Síntomas"), (100, 120, 120, 110, 150, 200))
        marco.pack(fill="both", expand=True, pady=(0, 12))
        f_acc = ttk.LabelFrame(self, text="Procedimientos Médicos", padding=12)
        f_acc.pack(fill="x")

        ttk.Label(f_acc, text="Enfermera Joy (Sede):").grid(row=0, column=0, sticky="w")
        self.combo_joy = ttk.Combobox(f_acc, state="readonly")
        self.combo_joy.grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(f_acc, text="Iniciar Triage / Diagnóstico", command=self.diagnosticar).grid(row=0, column=2, padx=8)

        ttk.Label(f_acc, text="Medicina (Almacén Sede):").grid(row=1, column=0, sticky="w", pady=8)
        self.combo_medicina = ttk.Combobox(f_acc, state="readonly")
        self.combo_medicina.grid(row=1, column=1, sticky="ew", padx=8, pady=8)
        ttk.Button(f_acc, text="Administrar Tratamiento (Gratis)", command=self.tratar).grid(row=1, column=2, padx=8, pady=8)
        f_acc.columnconfigure(1, weight=1)

    def refrescar(self) -> None:
        cid = self.controlador.centro_activo_id
        self.tabla.delete(*self.tabla.get_children())
        for pk in self.controlador.listar_pokemones(cid):
            self.tabla.insert("", "end", iid=pk.id, values=(pk.id, pk.nombre, pk.especie, f"{pk.hp_actual}/{pk.hp_maximo}", pk.estado.etiqueta, pk.sintomas))
        joys = self.controlador.listar_personal(cid)
        self.combo_joy["values"] = [f"{j.id} - {j.nombre}" for j in joys if j.activa]
        if self.combo_joy["values"]: self.combo_joy.current(0)
        else: self.combo_joy.set("")
        prods = self.controlador.listar_productos(cid)
        meds = [p for p in prods if p.categoria == "Medicina" and p.cantidad > 0]
        self.combo_medicina["values"] = [f"{m.id} - {m.nombre} ({m.cantidad} disps)" for m in meds]
        if self.combo_medicina["values"]: self.combo_medicina.current(0)
        else: self.combo_medicina.set("")

    def diagnosticar(self) -> None:
        sel = self.tabla.selection()
        if not sel: mostrar_error(self, "Seleccione un Pokémon paciente."); return
        if not self.combo_joy.get(): mostrar_error(self, "No hay enfermeras disponibles en esta sede."); return
        joy_id = self.combo_joy.get().split(" - ")[0]
        try:
            pk = self.controlador.diagnosticar_pokemon(sel[0], joy_id)
            informar(self, "Diagnóstico Realizado", f"{pk.nombre} en revisión médica por la Enfermera Joy.")
            self.refrescar()
        except Exception as e: mostrar_error(self, str(e))

    def tratar(self) -> None:
        sel = self.tabla.selection()
        if not sel: mostrar_error(self, "Seleccione un Pokémon paciente."); return
        if not self.combo_medicina.get(): mostrar_error(self, "No hay medicinas disponibles en la sede."); return
        med_id = self.combo_medicina.get().split(" - ")[0]
        try:
            pk = self.controlador.aplicar_tratamiento(sel[0], med_id)
            informar(self, "Tratamiento Exitoso", f"{pk.nombre} restauró su salud a {pk.hp_actual}/{pk.hp_maximo} HP.")
            self.refrescar()
        except Exception as e: mostrar_error(self, str(e))
