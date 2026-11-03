import tkinter as tk
from tkinter import messagebox, ttk

MODULOS = (
    ("inicio", "Inicio / Tablero"),
    ("admision", "Admisión de Pacientes"),
    ("tratamiento", "Atención / Curación"),
    ("donaciones", "Módulo de Donaciones"),
    ("inventario", "Almacén de Insumos"),
    ("personal", "Enfermeras / Personal"),
    ("seguimiento", "Seguimiento Clínico"),
)

def informar(parent: tk.Misc, titulo: str, mensaje: str) -> None: messagebox.showinfo(titulo, mensaje, parent=parent)
def mostrar_error(parent: tk.Misc, mensaje: str) -> None: messagebox.showerror("Atención", mensaje, parent=parent)
def pedir_confirmacion(parent: tk.Misc, titulo: str, mensaje: str) -> bool: return bool(messagebox.askyesno(titulo, mensaje, parent=parent))

def titulo(parent: tk.Misc, texto: str) -> ttk.Label:
    lbl = ttk.Label(parent, text=texto, style="Titulo.TLabel", font=("Helvetica", 12, "bold"))
    lbl.pack(anchor="w", pady=(0, 12))
    return lbl

def crear_tabla(parent, columnas, encabezados, anchos, altura=8):
    marco = ttk.Frame(parent)
    tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=altura, selectmode="browse")
    scroll = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    for col, enc, anc in zip(columnas, encabezados, anchos):
        tabla.heading(col, text=enc)
        tabla.column(col, width=anc, anchor="w")
    tabla.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="ns")
    marco.rowconfigure(0, weight=1); marco.columnconfigure(0, weight=1)
    return marco, tabla

class Pantalla(ttk.Frame):
    def __init__(self, master, controlador):
        super().__init__(master, padding=16)
        self.controlador = controlador
    def refrescar(self) -> None: pass
