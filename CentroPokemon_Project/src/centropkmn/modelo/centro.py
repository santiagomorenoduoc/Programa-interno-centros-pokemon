from uuid import uuid4
from centropkmn.modelo.centro_entidad import CentroSede
from centropkmn.modelo.errores import ReglaNegocioError
from centropkmn.modelo.persona import Entrenador, Personal
from centropkmn.modelo.producto import Medicina, Producto, producto_desde_diccionario
from centropkmn.modelo.donacion import DonacionMonetaria, DonacionObjetos, ResultadoDonacion
from centropkmn.modelo.pokemon import EstadoPokemon, Pokemon
from centropkmn.persistencia.repositorio_json import RepositorioJSON
from centropkmn.modelo.validaciones import *

class CentroPokemon:
    """Sistema gestor central multi-sede para Centros Pokémon."""
    def __init__(self, repositorio: RepositorioJSON):
        self._repositorio = repositorio
        self._centros: dict[str, CentroSede] = {}
        self._pokemones: dict[str, Pokemon] = {}
        self._entrenadores: dict[str, Entrenador] = {}
        self._personal: dict[str, Personal] = {}
        self._productos: dict[str, Producto] = {}
        self._donaciones: list[dict] = []
        self._centro_activo_id: str | None = None
        self.cargar()

    @property
    def centro_activo_id(self) -> str | None: return self._centro_activo_id
    @centro_activo_id.setter
    def centro_activo_id(self, cid: str) -> None:
        if cid not in self._centros:
            raise ReglaNegocioError(f"El centro {cid} no está registrado.")
        self._centro_activo_id = cid

    @property
    def advertencias(self) -> tuple[str, ...]: return tuple(self._repositorio.advertencias)

    def cargar(self) -> None:
        self._centros.clear(); self._pokemones.clear(); self._entrenadores.clear()
        self._personal.clear(); self._productos.clear(); self._donaciones.clear()

        for d in self._repositorio.cargar_lista("centros"):
            c = CentroSede.desde_diccionario(d); self._centros[c.id] = c

        if self._centros and self._centro_activo_id not in self._centros:
            self._centro_activo_id = next(iter(self._centros.keys()))

        for d in self._repositorio.cargar_lista("entrenadores"):
            ent = Entrenador.desde_diccionario(d); self._entrenadores[ent.id] = ent
        for d in self._repositorio.cargar_lista("personal"):
            p = Personal.desde_diccionario(d); self._personal[p.id] = p
        for d in self._repositorio.cargar_lista("productos"):
            prod = producto_desde_diccionario(d); self._productos[prod.id] = prod
        for d in self._repositorio.cargar_lista("pokemones"):
            pk = Pokemon.desde_diccionario(d); self._pokemones[pk.id] = pk
        self._donaciones = self._repositorio.cargar_lista("donaciones")

    def guardar(self) -> None:
        self._repositorio.guardar("centros", [item.a_diccionario() for item in self._centros.values()])
        self._repositorio.guardar("entrenadores", [item.a_diccionario() for item in self._entrenadores.values()])
        self._repositorio.guardar("personal", [item.a_diccionario() for item in self._personal.values()])
        self._repositorio.guardar("productos", [item.a_diccionario() for item in self._productos.values()])
        self._repositorio.guardar("pokemones", [item.a_diccionario() for item in self._pokemones.values()])
        self._repositorio.guardar("donaciones", self._donaciones)

    def registrar_centro(self, nombre: str, ubicacion: str, fondos: int = 0) -> CentroSede:
        cid = f"cp-{uuid4().hex[:6]}"
        c = CentroSede(cid, nombre, ubicacion, fondos, activo=True)
        self._centros[c.id] = c
        if self._centro_activo_id is None:
            self._centro_activo_id = c.id
        self.guardar(); return c

    def listar_centros(self) -> tuple[CentroSede, ...]: return tuple(self._centros.values())
    def obtener_centro(self, id: str) -> CentroSede: return self._centros[id]

    def listar_pokemones(self, centro_id: str | None = None):
        cid = centro_id or self._centro_activo_id
        return tuple(pk for pk in self._pokemones.values() if pk.centro_id == cid)

    def listar_entrenadores(self): return tuple(self._entrenadores.values())

    def listar_personal(self, centro_id: str | None = None):
        cid = centro_id or self._centro_activo_id
        return tuple(p for p in self._personal.values() if p.centro_id == cid)

    def listar_productos(self, centro_id: str | None = None):
        cid = centro_id or self._centro_activo_id
        return tuple(p for p in self._productos.values() if p.centro_id == cid)

    def listar_donaciones(self, centro_id: str | None = None):
        cid = centro_id or self._centro_activo_id
        return tuple(d for d in self._donaciones if d.get("centro_id") == cid)

    def obtener_pokemon(self, id: str) -> Pokemon: return self._pokemones[id]
    def obtener_entrenador(self, id: str) -> Entrenador: return self._entrenadores[id]
    def obtener_personal(self, id: str) -> Personal: return self._personal[id]
    def obtener_producto(self, id: str) -> Producto: return self._productos[id]

    def registrar_entrenador(self, nombre: str, telefono: str, correo: str, licencia: bool) -> Entrenador:
        ent = Entrenador(f"ent-{uuid4().hex[:6]}", nombre, telefono, correo, licencia)
        self._entrenadores[ent.id] = ent; self.guardar(); return ent

    def registrar_personal(self, centro_id: str, nombre: str, telefono: str, correo: str, cargo: str) -> Personal:
        p = Personal(f"joy-{uuid4().hex[:6]}", centro_id, nombre, telefono, correo, cargo, activa=True)
        self._personal[p.id] = p; self.guardar(); return p

    def registrar_producto_medicina(self, centro_id: str, nombre: str, cantidad: int, descripcion: str, puntos_curacion: int) -> Medicina:
        med = Medicina(f"med-{uuid4().hex[:6]}", centro_id, nombre, cantidad, descripcion, puntos_curacion)
        self._productos[med.id] = med; self.guardar(); return med

    def ingresar_pokemon(self, centro_id: str, nombre: str, especie: str, tipo: str, nivel: int, hp_act: int, hp_max: int, pokebola: str, sintomas: str, entrenador_id: str) -> Pokemon:
        pk = Pokemon(f"pkm-{uuid4().hex[:6]}", centro_id, nombre, especie, tipo, nivel, hp_act, hp_max, pokebola, sintomas, entrenador_id)
        self._pokemones[pk.id] = pk; self.guardar(); return pk

    def diagnosticar_pokemon(self, pokemon_id: str, enfermera_id: str) -> Pokemon:
        pk = self.obtener_pokemon(pokemon_id); enf = self.obtener_personal(enfermera_id)
        pk.diagnosticar(enf.id); self.guardar(); return pk

    def aplicar_tratamiento(self, pokemon_id: str, medicina_id: str) -> Pokemon:
        pk = self.obtener_pokemon(pokemon_id); prod = self.obtener_producto(medicina_id)
        if not isinstance(prod, Medicina): raise ReglaNegocioError("El insumo no es medicina.")
        prod.descontar(1); pk.aplicar_tratamiento(prod.id, prod.puntos_curacion); self.guardar(); return pk

    def dar_alta(self, pokemon_id: str) -> Pokemon:
        pk = self.obtener_pokemon(pokemon_id); pk.dar_alta(); self.guardar(); return pk

    def cancelar_atencion(self, pokemon_id: str) -> Pokemon:
        pk = self.obtener_pokemon(pokemon_id); pk.cancelar(); self.guardar(); return pk

    def registrar_donacion_monetaria(self, centro_id: str, donante_nombre: str, monto: int, medio: str) -> ResultadoDonacion:
        don = DonacionMonetaria(f"don-{uuid4().hex[:6]}", centro_id, donante_nombre, monto, medio)
        res = don.procesar(self); self._donaciones.append(res.a_diccionario()); self.guardar(); return res

    def registrar_donacion_objetos(self, centro_id: str, donante_nombre: str, producto_id: str, cantidad: int) -> ResultadoDonacion:
        don = DonacionObjetos(f"don-{uuid4().hex[:6]}", centro_id, donante_nombre, producto_id, cantidad)
        res = don.procesar(self); self._donaciones.append(res.a_diccionario()); self.guardar(); return res

    # En la clase CentroPokemon:


    def agregar_producto(self, producto: Producto) -> Producto:
     """Recibe cualquier objeto derivado de Producto, lo registra en el inventario del centro y guarda el estado en JSON."""
     if not producto.centro_id or producto.centro_id not in self._centros:
       raise ReglaNegocioError(
        f"El producto debe estar asignado a una sede válida ({producto.centro_id})."
     )

     self._productos[producto.id] = producto
     self.guardar()
     return producto


    def actualizar_stock(self, producto_id: str, nueva_cantidad: int) -> Producto:
        """Modifica manualmente el stock de un producto existente por su ID."""
        if producto_id not in self._productos:
            raise ReglaNegocioError(f"El producto con ID '{producto_id}' no existe.")

        prod = self._productos[producto_id]
        cant_validada = exigir_entero(nueva_cantidad, "Nueva cantidad de stock", minimo=0)
        prod._cantidad = cant_validada  # Actualiza la propiedad interna
        self.guardar()
        return prod