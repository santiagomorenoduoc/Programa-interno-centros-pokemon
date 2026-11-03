import tkinter as tk
from tkinter import ttk
from centropkmn.vista.comun import Pantalla, informar, mostrar_error, titulo

class Admision(Pantalla):
    def __init__(self, master, controlador):
        super().__init__(master, controlador)
        titulo(self, "Admisión de Pacientes Pokémon")
        f_ent = ttk.LabelFrame(self, text="1. Registrar / Seleccionar Entrenador", padding=12)
        f_ent.pack(fill="x", pady=(0, 12))
        self.ent_id = tk.StringVar()
        self.combo_entrenador = ttk.Combobox(f_ent, textvariable=self.ent_id, state="readonly")
        self.combo_entrenador.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.ent_nombre, self.ent_tel, self.ent_correo = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.ent_licencia = tk.BooleanVar(value=True)

        ttk.Label(f_ent, text="Nombre").grid(row=1, column=0, sticky="w")
        ttk.Entry(f_ent, textvariable=self.ent_nombre).grid(row=1, column=1, sticky="ew", padx=4)
        ttk.Label(f_ent, text="Teléfono").grid(row=1, column=2, sticky="w")
        ttk.Entry(f_ent, textvariable=self.ent_tel).grid(row=1, column=3, sticky="ew", padx=4)
        ttk.Button(f_ent, text="Registrar Entrenador", command=self.reg_entrenador).grid(row=1, column=4, padx=4)

        f_pk = ttk.LabelFrame(self, text="2. Ficha Médica de Admisión del Pokémon (Sede Activa)", padding=12)
        f_pk.pack(fill="x")
        self.pk_nombre, self.pk_especie, self.pk_tipo = tk.StringVar(), tk.StringVar(), tk.StringVar(value="Eléctrico")
        self.pk_nivel, self.pk_hp_act, self.pk_hp_max = tk.StringVar(value="5"), tk.StringVar(value="0"), tk.StringVar(value="20")
        self.pk_pokebola, self.pk_sintomas = tk.StringVar(value="Pokébola Standard"), tk.StringVar(value="Debilitado tras batalla")

        fields = [
            ("Mote / Nombre", self.pk_nombre, 0, 0), ("Especie", self.pk_especie, 0, 2),
            ("Tipo Elemental", self.pk_tipo, 1, 0), ("Nivel", self.pk_nivel, 1, 2),
            ("HP Actual", self.pk_hp_act, 2, 0), ("HP Máximo", self.pk_hp_max, 2, 2),
            ("Pokébola", self.pk_pokebola, 3, 0), ("Síntomas", self.pk_sintomas, 3, 2),
        ]
        for lbl, var, r, c in fields:
            ttk.Label(f_pk, text=lbl).grid(row=r, column=c, sticky="w", pady=2)
            ttk.Entry(f_pk, textvariable=var).grid(row=r, column=c+1, sticky="ew", padx=4, pady=2)

        ttk.Button(self, text="Admitir Pokémon en Centro Activo (Gratis)", command=self.admitir).pack(anchor="e", pady=12)

    def refrescar(self) -> None:
        ents = self.controlador.listar_entrenadores()
        vals = [f"{e.id} - {e.nombre}" for e in ents]
        self.combo_entrenador["values"] = vals
        if vals and not self.ent_id.get(): self.combo_entrenador.current(0)

    def reg_entrenador(self) -> None:
        try:
            ent = self.controlador.registrar_entrenador(self.ent_nombre.get(), self.ent_tel.get(), "entrenador@pokedex.com", self.ent_licencia.get())
            informar(self, "Entrenador Registrado", f"Entrenador {ent.nombre} registrado con ID: {ent.id}")
            self.refrescar(); self.ent_id.set(f"{ent.id} - {ent.nombre}")
        except Exception as e: mostrar_error(self, str(e))

    def admitir(self) -> None:
        try:
            val_ent = self.ent_id.get()
            if not val_ent: mostrar_error(self, "Seleccione o registre un entrenador primero."); return
            ent_id = val_ent.split(" - ")[0]
            cid = self.controlador.centro_activo_id
            if not cid: mostrar_error(self, "No hay una sede activa seleccionada."); return

            pk = self.controlador.ingresar_pokemon(
                cid, self.pk_nombre.get(), self.pk_especie.get(), self.pk_tipo.get(),
                int(self.pk_nivel.get()), int(self.pk_hp_act.get()), int(self.pk_hp_max.get()),
                self.pk_pokebola.get(), self.pk_sintomas.get(), ent_id
            )
            informar(self, "Pokémon Admitido", f"El Pokémon {pk.nombre} ({pk.especie}) ha sido ingresado en Urgencias en la sede {cid} sin costo alguno.")
            self.pk_nombre.set(""); self.pk_especie.set("")
        except Exception as e: mostrar_error(self, str(e))
