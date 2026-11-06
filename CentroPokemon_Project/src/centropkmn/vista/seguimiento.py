import tkinter as tk
from tkinter import ttk
from centropkmn.vista.comun import Pantalla, crear_tabla, informar, mostrar_error, titulo
from centropkmn.vista.estilos import PokeBoton

class Seguimiento(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        titulo(self, "Seguimiento Clínico y Altas Médicas (Sede Activa)")
        marco, self.tabla = crear_tabla(self, ("id", "nombre", "especie", "hp", "estado"), ("ID Paciente", "Mote", "Especie", "Salud (HP)", "Estado Clínico"), (110, 140, 140, 120, 200))
        marco.pack(fill="both", expand=True, pady=(0, 12))

        f_acc = ttk.Frame(self)
        f_acc.pack(fill="x")
        PokeBoton(f_acc, "Dar de Alta Médica (Entregar a Entrenador)", self.alta).pack(side="left", padx=4)
        PokeBoton(f_acc, "Cancelar Atención Médica", self.cancelar).pack(side="left", padx=4)

    def refrescar(self) -> None:
        cid = self.controlador.centro_activo_id
        self.tabla.delete(*self.tabla.get_children())
        for pk in self.controlador.listar_pokemones(cid):
            self.tabla.insert("", "end", iid=pk.id, values=(pk.id, pk.nombre, pk.especie, f"{pk.hp_actual}/{pk.hp_maximo}", pk.estado.etiqueta))

    def alta(self) -> None:
        sel = self.tabla.selection()
        if not sel: mostrar_error(self, "Seleccione un Pokémon paciente."); return
        try:
            pk = self.controlador.dar_alta(sel[0])
            informar(self, "Alta Médica Concedida", f"¡{pk.nombre} se ha recuperado por completo y ha sido devuelto a su entrenador!"); self.refrescar()
        except Exception as e: mostrar_error(self, str(e))

    def cancelar(self) -> None:
        sel = self.tabla.selection()
        if not sel: mostrar_error(self, "Seleccione un Pokémon paciente."); return
        try:
            pk = self.controlador.cancelar_atencion(sel[0])
            informar(self, "Atención Cancelada", f"La atención de {pk.nombre} fue cancelada."); self.refrescar()
        except Exception as e: mostrar_error(self, str(e))
