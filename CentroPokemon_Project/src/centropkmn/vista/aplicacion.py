import tkinter as tk
from tkinter import ttk, simpledialog
from centropkmn.controladores.controlador import Controlador
from centropkmn.vista.comun import MODULOS, informar, mostrar_error
from centropkmn.vista.inicio import Inicio
from centropkmn.vista.admision import Admision
from centropkmn.vista.tratamiento import Tratamiento
from centropkmn.vista.donaciones import Donaciones
from centropkmn.vista.inventario import Inventario
from centropkmn.vista.personal import PersonalView
from centropkmn.vista.seguimiento import Seguimiento

class Aplicacion(tk.Tk):
    def __init__(self, controlador: Controlador):
        super().__init__()
        self.controlador = controlador
        self.title("Centro Pokémon — Sistema Interno Multi-Sede")
        self.geometry("1100x680")
        self.minsize(920, 580)
        self.configure(background="#f5f5f5")

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)

        self._navegacion = ttk.Frame(cuerpo, padding=(12, 16, 8, 16))
        self._navegacion.pack(side="left", fill="y")
        ttk.Label(self._navegacion, text="Centro Pokémon", font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(0, 8))

        # Selector de Sede Activa
        ttk.Label(self._navegacion, text="Sede Activa:", font=("Helvetica", 9, "bold")).pack(anchor="w", pady=(4, 2))
        self.combo_centro = ttk.Combobox(self._navegacion, state="readonly")
        self.combo_centro.pack(fill="x", pady=(0, 8))
        self.combo_centro.bind("<<ComboboxSelected>>", self._al_cambiar_centro)

        ttk.Button(self._navegacion, text="+ Nueva Sede", command=self._crear_nueva_sede).pack(fill="x", pady=(0, 12))

        ttk.Separator(self._navegacion, orient="horizontal").pack(fill="x", pady=8)

        self._contenido = ttk.Frame(cuerpo)
        self._contenido.pack(side="left", fill="both", expand=True)

        for clave, etiqueta in MODULOS:
            ttk.Button(self._navegacion, text=etiqueta, command=lambda dest=clave: self.mostrar(dest)).pack(fill="x", pady=3)

        self._pantallas = {
            "inicio": Inicio(self._contenido, controlador, self.mostrar),
            "admision": Admision(self._contenido, controlador),
            "tratamiento": Tratamiento(self._contenido, controlador),
            "donaciones": Donaciones(self._contenido, controlador),
            "inventario": Inventario(self._contenido, controlador),
            "personal": PersonalView(self._contenido, controlador),
            "seguimiento": Seguimiento(self._contenido, controlador),
        }
        self._actual = None
        self._actualizar_combo_centros()
        self.mostrar("inicio")

    def _actualizar_combo_centros(self) -> None:
        centros = self.controlador.listar_centros()
        vals = [f"{c.id} - {c.nombre}" for c in centros]
        self.combo_centro["values"] = vals
        cid = self.controlador.centro_activo_id
        if cid:
            for idx, c in enumerate(centros):
                if c.id == cid:
                    self.combo_centro.current(idx)
                    break

    def _al_cambiar_centro(self, event=None) -> None:
        val = self.combo_centro.get()
        if val:
            cid = val.split(" - ")[0]
            self.controlador.centro_activo_id = cid
            if self._actual:
                self._actual.refrescar()

    def _crear_nueva_sede(self) -> None:
        nombre = simpledialog.askstring("Nueva Sede", "Nombre del Centro Pokémon (ej. Centro Ciudad Azulona):", parent=self)
        if not nombre: return
        ubicacion = simpledialog.askstring("Nueva Sede", "Ubicación / Región:", parent=self) or "Región Kanto"
        try:
            c = self.controlador.registrar_centro(nombre, ubicacion, fondos=5000)
            self.controlador.centro_activo_id = c.id
            self._actualizar_combo_centros()
            if self._actual: self._actual.refrescar()
            informar(self, "Sede Creada", f"La sede '{c.nombre}' (ID: {c.id}) ha sido registrada e iniciada con ₽5,000 de fondo.")
        except Exception as e: mostrar_error(self, str(e))

    def mostrar(self, clave: str) -> None:
        if self._actual is not None:
            self._actual.pack_forget()
        pantalla = self._pantallas[clave]
        pantalla.pack(fill="both", expand=True)
        pantalla.refrescar()
        self._actual = pantalla

def iniciar() -> None:
    controlador = Controlador()
    app = Aplicacion(controlador)
    app.mainloop()
