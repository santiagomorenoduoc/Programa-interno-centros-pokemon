import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import sys

FONDO = "#f6f4ef"
TARJETA = "#ffffff"
TINTA = "#1c1917"
TINTA_SUAVE = "#78716c"
LINEA = "#e4dfd6"
OSCURO = "#1c1917"
ACENTO = "#c2410c"
ACENTO_ACTIVO = "#9a3412"
PELIGRO = "#9f1239"
PELIGRO_FONDO = "#fff1f2"
FUENTE = "Segoe UI"

BLANCO = "#ffffff"
FONDO_APP = FONDO
FONDO_SIDEBAR = OSCURO
FONDO_PANEL = TARJETA
FONDO_SUTIL = FONDO
TEXTO = TINTA
COLOR_ROJO = ACENTO
COLOR_ROJO_OSCURO = ACENTO_ACTIVO
COLOR_ROJO_BORDE = LINEA


def dibujar_pokebola(canvas: tk.Canvas, size: int = 40) -> None:
    canvas.delete("all")
    medio = size / 2.0
    canvas.create_oval(1, 1, size - 1, size - 1, fill=ACENTO, outline="#000000", width=1.5)
    canvas.create_line(1, medio, size - 1, medio, width=size * 0.30, fill=BLANCO)
    r_btn = size * 0.14
    canvas.create_oval(medio - r_btn, medio - r_btn, medio + r_btn, medio + r_btn, fill="#111111")


def _poligono_redondeado(x0, y0, x1, y1, r):
    return [
        x0 + r, y0, x1 - r, y0, x1, y0,
        x1, y0 + r, x1, y1 - r, x1, y1,
        x1 - r, y1, x0 + r, y1, x0, y1,
        x0, y1 - r, x0, y0 + r, x0, y0,
    ]


class PokeBoton(tk.Canvas):
    

    def __init__(self, master, texto, comando=None, estilo="primario",
                 activo=False, ancho=150, alto=34):

        fnt = tkfont.Font(font=(FUENTE, 10, "bold"), master=master)
        ancho = max(ancho, fnt.measure(texto) + 32)

        self._estilo = estilo
        self._fondo_canvas = (
            OSCURO if estilo == "nav"
            else TARJETA if estilo == "secundario"
            else FONDO
        )

        super().__init__(
            master,
            width=ancho,
            height=alto,
            highlightthickness=0,
            bd=0,
            bg=self._fondo_canvas,
            cursor="hand2"
        )

        self._texto = texto
        self._comando = comando
        self._activo = activo
        self._hover = False
        self._ultimo_tamano = (0, 0)

        
        self.bind("<Configure>", self._al_redimensionar)
        self.bind("<Button-1>", lambda e: self._ejecutar())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))

    def _config(self):
        if self._activo:
            return {
                "fondo": ACENTO,
                "borde": ACENTO_ACTIVO,
                "texto": BLANCO,
                "hover": ACENTO_ACTIVO
            }

        if self._estilo == "nav":
            return {
                "fondo": OSCURO,
                "borde": OSCURO,
                "texto": "#f5f5f4",
                "hover": "#44403c"
            }

        if self._estilo == "secundario":
            return {
                "fondo": TARJETA,
                "borde": LINEA,
                "texto": TINTA,
                "hover": "#f5f5f4"
            }

        return {
            "fondo": ACENTO,
            "borde": ACENTO_ACTIVO,
            "texto": BLANCO,
            "hover": ACENTO_ACTIVO
        }

    def _al_redimensionar(self, event):
        tamano = (event.width, event.height)

        if tamano != self._ultimo_tamano:
            self._ultimo_tamano = tamano
            self._redibujar(event.width, event.height)

    def _set_hover(self, valor):
        self._hover = valor
        self._redibujar()

    def _ejecutar(self):
        if callable(self._comando):
            self._comando()

    def set_activo(self, valor):
        self._activo = valor
        self._redibujar()

    def _redibujar(self, ancho=None, alto=None):
        self.delete("all")

        w = ancho if ancho is not None else self.winfo_width()
        h = alto if alto is not None else self.winfo_height()

        
        if w <= 1 or h <= 1:
            return

        cfg = self._config()
        fondo = cfg["hover"] if self._hover and not self._activo else cfg["fondo"]

        r = min(max(3, int((h - 2) / 2)), w // 2)

        self.create_polygon(
            _poligono_redondeado(1, 1, w - 1, h - 1, r),
            fill=fondo,
            outline=cfg["borde"],
            width=1
        )

        fuente = (FUENTE, 10 if self._estilo == "nav" else 11, "bold")

        self.create_text(
            w / 2,
            h / 2,
            text=self._texto,
            font=fuente,
            fill=cfg["texto"],
            anchor="center"
        )


class Tarjeta(tk.Canvas):
    

    def __init__(self, master, ancho=300, alto=100,
                 texto=None, icono=False, comando=None):

        super().__init__(
            master,
            width=ancho,
            height=alto,
            highlightthickness=0,
            bd=0,
            bg=TARJETA,
            cursor="hand2" if comando else "arrow"
        )

        self._texto = texto
        self._icono = icono
        self._comando = comando
        self._ultimo_tamano = (0, 0)

        self.bind("<Configure>", self._al_redimensionar)
        self.bind("<Button-1>", lambda e: self._ejecutar())

    def _al_redimensionar(self, event):
        tamano = (event.width, event.height)

        if tamano != self._ultimo_tamano:
            self._ultimo_tamano = tamano
            self._redibujar(event.width, event.height)

    def _redibujar(self, ancho=None, alto=None):
        self.delete("all")

        w = ancho if ancho is not None else self.winfo_width()
        h = alto if alto is not None else self.winfo_height()

        if w <= 1 or h <= 1:
            return

        r = min(max(6, int((h - 6) / 2)), w // 2)

        self.create_polygon(
            _poligono_redondeado(2, 2, w - 2, h - 2, r),
            fill=TARJETA,
            outline=ACENTO,
            width=2
        )

        if self._icono and self._texto:
            size = int(min(w, h) * 0.34)
            cx = w / 2
            cy = h * 0.35
            radio = size / 2

        
            self.create_oval(
                cx - radio, cy - radio,
                cx + radio, cy + radio,
                fill=ACENTO,
                outline="#000000",
                width=1
            )

            self.create_line(
                cx - radio, cy,
                cx + radio, cy,
                fill=BLANCO,
                width=max(2, int(size * 0.30))
            )

            rb = size * 0.14

            self.create_oval(
                cx - rb, cy - rb,
                cx + rb, cy + rb,
                fill="#111111"
            )

            self.create_text(
                cx,
                cy + radio + 12,
                text=self._texto,
                font=(FUENTE, 10, "bold"),
                fill=ACENTO,
                anchor="center"
            )

    def _ejecutar(self):
        if callable(self._comando):
            self._comando()



def registrar_estilos(root) -> ttk.Style:
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=FONDO, borderwidth=0)
    style.configure("TLabel", background=FONDO, foreground=TINTA, font=(FUENTE, 10))
    style.configure("TLabelframe", background=FONDO, bordercolor=LINEA, relief="solid", borderwidth=1)
    style.configure("TLabelframe.Label", background=FONDO, foreground=TINTA, font=(FUENTE, 11, "bold"))
    style.configure("TCheckbutton", background=FONDO, foreground=TINTA, font=(FUENTE, 10))
    style.map("TCheckbutton", background=[("active", FONDO)])
    style.configure("Titulo.TLabel", font=(FUENTE, 22, "bold"), background=FONDO, foreground=TINTA)
    style.configure("Ayuda.TLabel", font=(FUENTE, 10), background=FONDO, foreground=TINTA_SUAVE)
    style.configure("Ceja.TLabel", font=(FUENTE, 9, "bold"), background=FONDO, foreground=ACENTO)
    style.configure("Total.TLabel", font=(FUENTE, 20, "bold"), background=FONDO, foreground=ACENTO)
    style.configure("TEntry", padding=6)
    style.configure("TCombobox", padding=5)
    style.configure(
        "TButton",
        background=TARJETA,
        foreground=TINTA,
        padding=(12, 8),
        font=(FUENTE, 10),
        borderwidth=1,
        relief="solid",
    )
    style.map(
        "TButton",
        background=[("pressed", "#f5f5f4"), ("active", "#fafaf9"), ("disabled", "#f5f5f4")],
        foreground=[("disabled", "#a8a29e")],
    )
    style.configure(
        "Primario.TButton",
        background=ACENTO,
        foreground=BLANCO,
        padding=(14, 8),
        font=(FUENTE, 10, "bold"),
        borderwidth=0,
    )
    style.map(
        "Primario.TButton",
        background=[("pressed", ACENTO_ACTIVO), ("active", "#ea580c"), ("disabled", "#fdba74")],
        foreground=[("disabled", "#fff7ed")],
    )
    style.configure(
        "Peligro.TButton",
        background=PELIGRO_FONDO,
        foreground=PELIGRO,
        padding=(12, 8),
        font=(FUENTE, 10, "bold"),
        borderwidth=0,
    )
    style.map(
        "Peligro.TButton",
        background=[("pressed", "#ffe4e6"), ("active", "#ffe4e6"), ("disabled", "#f5f5f4")],
        foreground=[("disabled", "#a8a29e")],
    )
    style.configure(
        "Nav.TButton",
        background=OSCURO,
        foreground="#f5f5f4",
        padding=(12, 8),
        anchor="w",
        font=(FUENTE, 10),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Nav.TButton",
        background=[("pressed", "#44403c"), ("active", "#292524")],
        foreground=[("pressed", "#ffffff"), ("active", "#ffffff")],
        relief=[("pressed", "flat"), ("active", "flat")],
    )
    style.configure("NavActivo.TButton", background=ACENTO, foreground=BLANCO, padding=(12, 8), anchor="w", font=(FUENTE, 10, "bold"), borderwidth=0, relief="flat")
    style.map(
        "NavActivo.TButton",
        background=[("pressed", ACENTO_ACTIVO), ("active", "#ea580c")],
        foreground=[("pressed", "#ffffff"), ("active", "#ffffff")],
        relief=[("pressed", "flat"), ("active", "flat")],
    )
    style.configure(
        "ComboNav.TCombobox",
        fieldbackground="#1c1917",
        background="#1c1917",
        foreground="#ffffff",
        arrowcolor="#ffffff",
        bordercolor="#44403c",
        lightcolor="#1c1917",
        darkcolor="#1c1917",
        padding=5,
    )
    style.map(
        "ComboNav.TCombobox",
        fieldbackground=[("readonly", "#1c1917")],
        background=[("readonly", OSCURO), ("active", OSCURO)],
        foreground=[("readonly", "#f5f5f4"), ("active", "#f5f5f4")],
        selectbackground=[("readonly", "#1c1917")],
        selectforeground=[("readonly", "#ffffff")]

    )
    style.configure(
        "Treeview",
        font=(FUENTE, 10),
        rowheight=32,
        background=TARJETA,
        fieldbackground=TARJETA,
        foreground=TINTA,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        font=(FUENTE, 10, "bold"),
        background="#f3f1ec",
        foreground="#44403c",
        relief="flat",
        padding=8,
    )
    style.map("Treeview", background=[("selected", "#fed7aa")], foreground=[("selected", TINTA)])
    style.configure("Kpi.TFrame", background=TARJETA)
    style.configure("KpiEtiqueta.TLabel", background=TARJETA, foreground=TINTA_SUAVE, font=(FUENTE, 9))
    style.configure("KpiValor.TLabel", background=TARJETA, foreground=TINTA, font=(FUENTE, 20, "bold"))
    return style


def activar_dpi() -> None:
    if sys.platform != "win32":
         return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            return


def area_de_trabajo() -> tuple[int, int]:
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            rect = wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0):
                return max(rect.right - rect.left, 640), max(rect.bottom - rect.top, 480)
        except Exception:
            pass
    return 1280, 720
