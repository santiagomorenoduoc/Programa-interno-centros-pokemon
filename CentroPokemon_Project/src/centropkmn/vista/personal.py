import tkinter as tk
from tkinter import ttk
from centropkmn.vista.comun import Pantalla, crear_tabla, informar, mostrar_error, titulo

class PersonalView(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        titulo(self, "Gestión de Personal Médico (Enfermeras Joy / Asistentes)")
        f_p = ttk.LabelFrame(self, text="Registrar Personal en la Sede Activa", padding=12)
        f_p.pack(fill="x", pady=(0, 12))
        self.p_nombre, self.p_tel, self.p_cargo = tk.StringVar(), tk.StringVar(), tk.StringVar(value="Enfermera Jefe")
        ttk.Label(f_p, text="Nombre").grid(row=0, column=0)
        ttk.Entry(f_p, textvariable=self.p_nombre).grid(row=0, column=1, padx=4)
        ttk.Label(f_p, text="Teléfono").grid(row=0, column=2)
        ttk.Entry(f_p, textvariable=self.p_tel).grid(row=0, column=3, padx=4)
        ttk.Label(f_p, text="Cargo").grid(row=0, column=4)
        ttk.Entry(f_p, textvariable=self.p_cargo).grid(row=0, column=5, padx=4)
        ttk.Button(f_p, text="Registrar Personal", command=self.reg_personal).grid(row=0, column=6, padx=8)

        marco, self.tabla = crear_tabla(self, ("id", "nombre", "cargo", "activa"), ("ID", "Nombre", "Cargo", "Estado Disponibilidad"), (100, 200, 160, 140))
        marco.pack(fill="both", expand=True)

    def refrescar(self) -> None:
        cid = self.controlador.centro_activo_id
        self.tabla.delete(*self.tabla.get_children())
        for p in self.controlador.listar_personal(cid):
            self.tabla.insert("", "end", iid=p.id, values=(p.id, p.nombre, p.cargo, "Activa / En Turno" if p.activa else "Inactiva"))

    def reg_personal(self) -> None:
        cid = self.controlador.centro_activo_id
        if not cid: mostrar_error(self, "No hay sede seleccionada."); return
        try:
            p = self.controlador.registrar_personal(cid, self.p_nombre.get(), self.p_tel.get(), "joy@pkmn.center", self.p_cargo.get())
            informar(self, "Personal Registrado", f"Personal {p.nombre} asignado a la sede {cid} con éxito."); self.refrescar()
        except Exception as e: mostrar_error(self, str(e))
