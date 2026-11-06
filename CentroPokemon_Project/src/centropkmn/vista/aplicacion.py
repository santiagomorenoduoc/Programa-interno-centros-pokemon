import tkinter as tk
from tkinter import ttk, simpledialog
from centropkmn.controladores.controlador import Controlador
from centropkmn.vista.comun import MODULOS, informar, mostrar_error
from centropkmn.vista.estilos import (
    BLANCO,
    FONDO,
    FONDO_APP,
    FONDO_SIDEBAR,
    TINTA,
    TINTA_SUAVE,
    LINEA,
    OSCURO,
    ACENTO,
    ACENTO_ACTIVO,
    PELIGRO,
    PELIGRO_FONDO,
    FUENTE,
    activar_dpi,
    area_de_trabajo,
    dibujar_pokebola,
    registrar_estilos,
    PokeBoton,
)
from centropkmn.vista.inicio import Inicio
from centropkmn.vista.admision import Admision
from centropkmn.vista.tratamiento import Tratamiento
from centropkmn.vista.donaciones import Donaciones
from centropkmn.vista.inventario import Inventario
from centropkmn.vista.personal import PersonalView
from centropkmn.vista.seguimiento import Seguimiento

class Aplicacion(tk.Tk):
    def __init__(self, controlador: Controlador):
        activar_dpi()
        super().__init__()
        self.controlador = controlador
        self.title("Centro Pokémon — Sistema Interno Multi-Sede")
        self._encajar_en_pantalla()
        registrar_estilos(self)
        self.configure(background=FONDO)

        cuerpo = tk.Frame(self, bg=FONDO_APP)
        cuerpo.pack(fill="both", expand=True)

        self._navegacion = tk.Frame(cuerpo, bg=OSCURO, width=208)
        self._navegacion.pack(side="left", fill="y")

        bola = tk.Canvas(self._navegacion, width=48, height=48, highlightthickness=0, bg=OSCURO)
        dibujar_pokebola(bola, 44)
        bola.pack(pady=(16, 0))

        ttk.Label(self._navegacion, text="Centro Pokémon", font=(FUENTE, 18, "bold"), foreground=BLANCO, background=OSCURO).pack(pady=(4, 14))

        ttk.Label(self._navegacion, text="Sede Activa:", font=(FUENTE, 10, "bold"), foreground="#f5f5f4", background=OSCURO).pack(anchor="w", padx=14)
        self.combo_centro = ttk.Combobox(self._navegacion, state="readonly", style="ComboNav.TCombobox")
        self.combo_centro.pack(fill="x", padx=14, pady=(2, 10))
        PokeBoton(self._navegacion, "+ Nueva Sede", self._crear_nueva_sede, estilo="nav", ancho=180, alto=34).pack(fill="x", padx=14, pady=(0, 12))
        ttk.Separator(self._navegacion, orient="horizontal").pack(fill="x", padx=14)

        self._nav_frame = tk.Frame(self._navegacion, bg=OSCURO)
        self._nav_frame.pack(fill="both", expand=True)
        self._botones_modulos = {}
        for clave, etiqueta in MODULOS:
            btn = PokeBoton(self._nav_frame, etiqueta, (lambda c=clave: self.mostrar(c)), estilo="nav", activo=False, ancho=210, alto=36)
            btn.pack(fill="x", pady=2, padx=12)
            self._botones_modulos[clave] = btn

        self._contenido = tk.Frame(cuerpo, bg=FONDO)
        self._contenido.pack(side="left", fill="both", expand=True)

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
        self._modulo_actual = None
        self._actualizar_combo_centros()
        self.mostrar("inicio")

    def _encajar_en_pantalla(self) -> None:
        ancho, alto = area_de_trabajo()
        ancho_ventana = max(640, min(1440, ancho - 16))
        alto_ventana = max(480, min(960, alto - 16))
        self.minsize(min(860, ancho_ventana), min(500, alto_ventana))
        self.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")
        self.resizable(True, True)

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
            if self._actual is not None:
                self._actual.refrescar()

    def _crear_nueva_sede(self) -> None:
        nombre = simpledialog.askstring("Nueva Sede", "Nombre del Centro Pokémon (ej. Centro Ciudad Azulona):", parent=self)
        if not nombre: return
        ubicacion = simpledialog.askstring("Nueva Sede", "Ubicación / Región:", parent=self) or "Región Kanto"
        try:
            c = self.controlador.registrar_centro(nombre, ubicacion, fondos=5000)
            self.controlador.centro_activo_id = c.id
            self._actualizar_combo_centros()
            if self._actual is not None: self._actual.refrescar()
            informar(self, "Sede Creada", f"La sede '{c.nombre}' (ID: {c.id}) ha sido registrada e iniciada con ₽5,000 de fondo.")
        except Exception as e:
            mostrar_error(self, str(e))

    def mostrar(self, clave: str) -> None:
        if self._actual is not None:
            self._actual.pack_forget()
        pantalla = self._pantallas[clave]
        pantalla.pack(fill="both", expand=True)
        pantalla.refrescar()
        self._actual = pantalla
        self._modulo_actual = clave
        for k, b in self._botones_modulos.items():
            b.set_activo(k == clave)

def iniciar() -> None:
    controlador = Controlador()
    app = Aplicacion(controlador)
    app.mainloop()
