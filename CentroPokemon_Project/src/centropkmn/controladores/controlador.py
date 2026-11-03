from pathlib import Path
from centropkmn.modelo.centro import CentroPokemon
from centropkmn.modelo.pokemon import EstadoPokemon
from centropkmn.persistencia.repositorio_json import RepositorioJSON
from centropkmn.rutas import directorio_datos
from centropkmn.modelo.producto import Producto


class Controlador:

  def __init__(self, directorio: str | Path | None = None):
    self._directorio = (
        Path(directorio) if directorio is not None else directorio_datos()
    )
    self._centro = CentroPokemon(RepositorioJSON(self._directorio))

  @property
  def directorio(self) -> Path:
    return self._directorio

  @property
  def centro_activo_id(self) -> str | None:
    return self._centro.centro_activo_id

  @centro_activo_id.setter
  def centro_activo_id(self, cid: str) -> None:
    self._centro.centro_activo_id = cid

  def resumen(self) -> dict:
    cid = self._centro.centro_activo_id
    centro = self._centro.obtener_centro(cid) if cid else None
    pks = self._centro.listar_pokemones(cid)
    prods = self._centro.listar_productos(cid)
    pers = self._centro.listar_personal(cid)
    return {
        "centro_nombre": centro.nombre if centro else "Sin Centro",
        "centro_id": cid,
        "fondos": centro.fondos if centro else 0,
        "pacientes_totales": len(pks),
        "enfermeras_activas": sum(1 for p in pers if p.activa),
        "insumos_disponibles": sum(p.cantidad for p in prods),
        "estados": {
            estado.etiqueta: sum(1 for p in pks if p.estado is estado)
            for estado in EstadoPokemon
        },
    }

  def listar_centros(self):
    return self._centro.listar_centros()

  def registrar_centro(self, nombre, ubicacion, fondos=0):
    return self._centro.registrar_centro(nombre, ubicacion, fondos)

  def listar_entrenadores(self):
    return self._centro.listar_entrenadores()

  def registrar_entrenador(self, nombre, telefono, correo, licencia):
    return self._centro.registrar_entrenador(
        nombre, telefono, correo, licencia
    )

  def listar_personal(self, centro_id=None):
    return self._centro.listar_personal(centro_id)

  def registrar_personal(self, centro_id, nombre, telefono, correo, cargo):
    return self._centro.registrar_personal(
        centro_id, nombre, telefono, correo, cargo
    )

  def listar_productos(self, centro_id=None):
    return self._centro.listar_productos(centro_id)

  def registrar_producto_medicina(
      self, centro_id, nombre, cantidad, descripcion, puntos_curacion
  ):
    return self._centro.registrar_producto_medicina(
        centro_id, nombre, cantidad, descripcion, puntos_curacion
    )

  def listar_pokemones(self, centro_id=None):
    return self._centro.listar_pokemones(centro_id)

  def obtener_pokemon(self, id):
    return self._centro.obtener_pokemon(id)

  def ingresar_pokemon(
      self,
      centro_id,
      nombre,
      especie,
      tipo,
      nivel,
      hp_actual,
      hp_maximo,
      pokebola,
      sintomas,
      entrenador_id,
  ):
    return self._centro.ingresar_pokemon(
        centro_id,
        nombre,
        especie,
        tipo,
        nivel,
        hp_actual,
        hp_maximo,
        pokebola,
        sintomas,
        entrenador_id,
    )

  def diagnosticar_pokemon(self, pokemon_id, enfermera_id):
    return self._centro.diagnosticar_pokemon(pokemon_id, enfermera_id)

  def aplicar_tratamiento(self, pokemon_id, medicina_id):
    return self._centro.aplicar_tratamiento(pokemon_id, medicina_id)

  def dar_alta(self, pokemon_id):
    return self._centro.dar_alta(pokemon_id)

  def cancelar_atencion(self, pokemon_id):
    return self._centro.cancelar_atencion(pokemon_id)

  def registrar_donacion_monetaria(self, centro_id, donante_nombre, monto, medio):
    return self._centro.registrar_donacion_monetaria(
        centro_id, donante_nombre, monto, medio
    )

  def registrar_donacion_objetos(
      self, centro_id, donante_nombre, producto_id, cantidad
  ):
    return self._centro.registrar_donacion_objetos(
        centro_id, donante_nombre, producto_id, cantidad
    )

  def listar_donaciones(self, centro_id=None):
    return self._centro.listar_donaciones(centro_id)

  def agregar_producto(self, producto: Producto) -> Producto:
   """Pasa el objeto Producto al modelo para su registro y persistencia."""
   return self._centro.agregar_producto(producto)


  def actualizar_stock(self, producto_id: str, nueva_cantidad: int) -> Producto:
   """Actualiza la cantidad de stock de un producto específico."""
   return self._centro.actualizar_stock(producto_id, nueva_cantidad)