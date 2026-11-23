"""Persistencia en MySQL, con el mismo contrato que RepositorioJSON.

Las tablas se crean con database/01_esquema.sql (MySQL Workbench). Aquí solo hay SQL:
las reglas de negocio viven en el modelo, que sigue recibiendo y entregando los mismos
diccionarios que con JSON.
"""

import copy
from contextlib import contextmanager

from centropkmn.modelo.errores import PersistenciaError
from centropkmn.persistencia.configuracion import ConfiguracionMySQL
from centropkmn.persistencia.repositorio import Repositorio

try:
    import mysql.connector as conector
except ImportError:  # el conector solo hace falta si se usa MySQL
    conector = None

TABLAS = (
    "centros",
    "personas",
    "entrenadores",
    "personal",
    "productos",
    "medicinas",
    "insumos_captura",
    "pokemones",
    "historial_estados_pokemon",
    "donaciones",
    "donacion_monetarias",
    "donacion_objetos",
)
# Campo que identifica cada registro dentro del diccionario de su colección.
_CLAVES = {
    "centros": "id",
    "entrenadores": "id",
    "personal": "id",
    "productos": "id",
    "pokemones": "id",
    "donaciones": "referencia",
}

_SIN_CONEXION = {2002, 2003, 2005, 2006, 2013, 2055}
_ACCESO_DENEGADO = 1045
_SIN_BASE = {1044, 1049}
_SIN_TABLA = 1146
_DUPLICADO = 1062
_REFERENCIA = {1451, 1452}
_DATO_EXCEDIDO = {1264, 1406}


def _valor(valor):
    return int(valor) if isinstance(valor, bool) else valor


def _upsert(cursor, tabla: str, columnas: tuple, valores: tuple) -> None:
    """INSERT que actualiza si la clave primaria (primera columna) ya existe."""
    marcas = ", ".join(["%s"] * len(columnas))
    actualiza = ", ".join(f"{c} = VALUES({c})" for c in columnas[1:])
    cursor.execute(
        f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({marcas}) "
        f"ON DUPLICATE KEY UPDATE {actualiza}",
        tuple(_valor(v) for v in valores),
    )


# --- lectura: fila de MySQL -> diccionario con la forma que espera el modelo ----------------

def _leer_centros(cursor) -> list[dict]:
    cursor.execute(
        "SELECT id_centro, nombre, ubicacion, fondos, activo "
        "FROM centros ORDER BY fecha_creacion, id_centro"
    )
    return [
        {
            "id": f["id_centro"],
            "nombre": f["nombre"],
            "ubicacion": f["ubicacion"],
            "fondos": int(f["fondos"]),
            "activo": bool(f["activo"]),  # el modelo exige bool, MySQL entrega 0/1
        }
        for f in cursor.fetchall()
    ]


def _leer_entrenadores(cursor) -> list[dict]:
    cursor.execute(
        "SELECT p.id_persona, p.nombre, p.telefono, p.correo, e.licencia_oficial "
        "FROM personas p JOIN entrenadores e ON e.id_persona = p.id_persona "
        "ORDER BY p.fecha_registro, p.id_persona"
    )
    return [
        {
            "id": f["id_persona"],
            "nombre": f["nombre"],
            "telefono": f["telefono"],
            "correo": f["correo"],
            "licencia_oficial": bool(f["licencia_oficial"]),
        }
        for f in cursor.fetchall()
    ]


def _leer_personal(cursor) -> list[dict]:
    cursor.execute(
        "SELECT p.id_persona, pe.id_centro, p.nombre, p.telefono, p.correo, pe.cargo, pe.activa "
        "FROM personas p JOIN personal pe ON pe.id_persona = p.id_persona "
        "ORDER BY p.fecha_registro, p.id_persona"
    )
    return [
        {
            "id": f["id_persona"],
            "centro_id": f["id_centro"],
            "nombre": f["nombre"],
            "telefono": f["telefono"],
            "correo": f["correo"],
            "cargo": f["cargo"],
            "activa": bool(f["activa"]),
        }
        for f in cursor.fetchall()
    ]


def _leer_productos(cursor) -> list[dict]:
    cursor.execute(
        "SELECT pr.id_producto, pr.id_centro, pr.categoria, pr.nombre, pr.cantidad, pr.descripcion, "
        "m.puntos_curacion, ic.ratio_captura "
        "FROM productos pr "
        "LEFT JOIN medicinas m ON m.id_producto = pr.id_producto "
        "LEFT JOIN insumos_captura ic ON ic.id_producto = pr.id_producto "
        "ORDER BY pr.fecha_creacion, pr.id_producto"
    )
    productos = []
    for f in cursor.fetchall():
        item = {
            "id": f["id_producto"],
            "centro_id": f["id_centro"],
            "categoria": f["categoria"],
            "nombre": f["nombre"],
            "cantidad": int(f["cantidad"]),
            "descripcion": f["descripcion"],
        }
        # Cada categoría trae solo su dato propio, igual que Producto.a_diccionario().
        if f["categoria"] == "Medicina" and f["puntos_curacion"] is not None:
            item["puntos_curacion"] = int(f["puntos_curacion"])
        elif f["categoria"] == "Pokébola/Captura" and f["ratio_captura"] is not None:
            item["ratio_captura"] = float(f["ratio_captura"])
        productos.append(item)
    return productos


def _leer_pokemones(cursor) -> list[dict]:
    cursor.execute(
        "SELECT id_pokemon, estado FROM historial_estados_pokemon ORDER BY id_pokemon, id_historial"
    )
    historial: dict[str, list[str]] = {}
    for f in cursor.fetchall():
        historial.setdefault(f["id_pokemon"], []).append(f["estado"])
    cursor.execute(
        "SELECT id_pokemon, id_centro, id_entrenador, id_enfermera, id_medicina_usada, nombre, "
        "especie, tipo, nivel, hp_actual, hp_maximo, pokebola, sintomas, estado "
        "FROM pokemones ORDER BY fecha_ingreso, id_pokemon"
    )
    return [
        {
            "id": f["id_pokemon"],
            "centro_id": f["id_centro"],
            "nombre": f["nombre"],
            "especie": f["especie"],
            "tipo": f["tipo"],
            "nivel": int(f["nivel"]),
            "hp_actual": int(f["hp_actual"]),
            "hp_maximo": int(f["hp_maximo"]),
            "pokebola": f["pokebola"],
            "sintomas": f["sintomas"],
            "entrenador_id": f["id_entrenador"],
            "enfermera_id": f["id_enfermera"],
            "medicina_usada_id": f["id_medicina_usada"],
            "estado": f["estado"],
            "historial": historial.get(f["id_pokemon"], [f["estado"]]),
        }
        for f in cursor.fetchall()
    ]


def _leer_donaciones(cursor) -> list[dict]:
    cursor.execute(
        "SELECT d.referencia, d.id_centro, d.donante_nombre, d.tipo, d.exitosa, d.mensaje, "
        "dm.monto, dm.medio, dob.id_producto, dob.cantidad "
        "FROM donaciones d "
        "LEFT JOIN donacion_monetarias dm ON dm.id_donacion = d.id_donacion "
        "LEFT JOIN donacion_objetos dob ON dob.id_donacion = d.id_donacion "
        "ORDER BY d.fecha_donacion, d.id_donacion"
    )
    donaciones = []
    for f in cursor.fetchall():
        item = {
            "exitosa": bool(f["exitosa"]),
            "referencia": f["referencia"],
            "centro_id": f["id_centro"],
            "tipo": f["tipo"],
            "mensaje": f["mensaje"],
        }
        # Los datos opcionales solo aparecen si existen (igual que ResultadoDonacion.a_diccionario()).
        if f["donante_nombre"] is not None:
            item["donante_nombre"] = f["donante_nombre"]
        if f["monto"] is not None:
            item["monto"] = int(f["monto"])
            item["medio"] = f["medio"]
        if f["id_producto"] is not None:
            item["producto_id"] = f["id_producto"]
            item["cantidad"] = int(f["cantidad"])
        donaciones.append(item)
    return donaciones


# --- escritura: diccionario del modelo -> filas de MySQL ------------------------------------
# Cada escritor recibe el registro nuevo y el que había guardado antes (None si es nuevo).

def _escribir_centro(cursor, item: dict, anterior) -> None:
    _upsert(
        cursor,
        "centros",
        ("id_centro", "nombre", "ubicacion", "fondos", "activo"),
        (item["id"], item["nombre"], item["ubicacion"], item["fondos"], item["activo"]),
    )


def _escribir_persona(cursor, item: dict, tipo: str) -> None:
    _upsert(
        cursor,
        "personas",
        ("id_persona", "nombre", "telefono", "correo", "tipo_persona"),
        (item["id"], item["nombre"], item["telefono"], item["correo"], tipo),
    )


def _escribir_entrenador(cursor, item: dict, anterior) -> None:
    _escribir_persona(cursor, item, "ENTRENADOR")
    _upsert(
        cursor,
        "entrenadores",
        ("id_persona", "licencia_oficial"),
        (item["id"], item["licencia_oficial"]),
    )


def _escribir_personal(cursor, item: dict, anterior) -> None:
    _escribir_persona(cursor, item, "PERSONAL")
    _upsert(
        cursor,
        "personal",
        ("id_persona", "id_centro", "cargo", "activa"),
        (item["id"], item["centro_id"], item["cargo"], item["activa"]),
    )


def _escribir_producto(cursor, item: dict, anterior) -> None:
    _upsert(
        cursor,
        "productos",
        ("id_producto", "id_centro", "nombre", "cantidad", "descripcion", "categoria"),
        (item["id"], item["centro_id"], item["nombre"], item["cantidad"], item["descripcion"], item["categoria"]),
    )
    if item["categoria"] == "Medicina":
        _upsert(cursor, "medicinas", ("id_producto", "puntos_curacion"), (item["id"], item["puntos_curacion"]))
    elif item["categoria"] == "Pokébola/Captura":
        _upsert(cursor, "insumos_captura", ("id_producto", "ratio_captura"), (item["id"], item["ratio_captura"]))
    else:
        raise PersistenciaError(f"Categoría de producto desconocida: {item['categoria']}")


def _escribir_pokemon(cursor, item: dict, anterior) -> None:
    _upsert(
        cursor,
        "pokemones",
        (
            "id_pokemon", "id_centro", "id_entrenador", "id_enfermera", "id_medicina_usada",
            "nombre", "especie", "tipo", "nivel", "hp_actual", "hp_maximo", "pokebola",
            "sintomas", "estado",
        ),
        (
            item["id"], item["centro_id"], item["entrenador_id"], item["enfermera_id"],
            item["medicina_usada_id"], item["nombre"], item["especie"], item["tipo"],
            item["nivel"], item["hp_actual"], item["hp_maximo"], item["pokebola"],
            item["sintomas"], item["estado"],
        ),
    )
    # El historial solo crece: se agregan los estados nuevos y se conservan las fechas ya guardadas.
    previo = list(anterior["historial"]) if anterior else []
    nuevo = list(item["historial"])
    if nuevo[: len(previo)] != previo:  # el historial cambió por dentro: se reescribe completo
        cursor.execute("DELETE FROM historial_estados_pokemon WHERE id_pokemon = %s", (item["id"],))
        previo = []
    for estado in nuevo[len(previo):]:
        cursor.execute(
            "INSERT INTO historial_estados_pokemon (id_pokemon, estado) VALUES (%s, %s)",
            (item["id"], estado),
        )


def _escribir_donacion(cursor, item: dict, anterior) -> None:
    if anterior is not None:  # una donación registrada no se modifica
        return
    cursor.execute(
        "INSERT INTO donaciones (referencia, id_centro, donante_nombre, tipo, exitosa, mensaje) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (
            item["referencia"], item["centro_id"], item.get("donante_nombre"),
            item["tipo"], int(item["exitosa"]), item["mensaje"],
        ),
    )
    id_donacion = cursor.lastrowid
    if item.get("monto") is not None:
        cursor.execute(
            "INSERT INTO donacion_monetarias (id_donacion, monto, medio) VALUES (%s, %s, %s)",
            (id_donacion, item["monto"], item["medio"]),
        )
    if item.get("producto_id") is not None:
        cursor.execute(
            "INSERT INTO donacion_objetos (id_donacion, id_producto, cantidad) VALUES (%s, %s, %s)",
            (id_donacion, item["producto_id"], item["cantidad"]),
        )


_LECTORES = {
    "centros": _leer_centros,
    "entrenadores": _leer_entrenadores,
    "personal": _leer_personal,
    "productos": _leer_productos,
    "pokemones": _leer_pokemones,
    "donaciones": _leer_donaciones,
}
_ESCRITORES = {
    "centros": _escribir_centro,
    "entrenadores": _escribir_entrenador,
    "personal": _escribir_personal,
    "productos": _escribir_producto,
    "pokemones": _escribir_pokemon,
    "donaciones": _escribir_donacion,
}


class RepositorioMySQL(Repositorio):
    def __init__(self, configuracion: ConfiguracionMySQL):
        super().__init__()
        if conector is None:
            raise PersistenciaError(
                "Falta el conector de MySQL. Instálalo con: python -m pip install mysql-connector-python"
            )
        self._configuracion = configuracion
        self._conexion = None
        # Último estado conocido de cada colección: permite escribir solo lo que cambió.
        self._guardado: dict[str, dict[str, dict]] = {}
        self._pendiente: dict[str, dict[str, dict]] = {}

    @property
    def descripcion(self) -> str:
        c = self._configuracion
        return f"MySQL ({c.usuario}@{c.host}:{c.puerto}/{c.base_datos})"

    def probar(self) -> str:
        """Comprueba la conexión y que existan las tablas. Devuelve la versión del servidor."""
        with self.transaccion():
            with self._cursor() as cursor:
                for tabla in TABLAS:
                    cursor.execute(f"SELECT 1 FROM {tabla} LIMIT 1")
                    cursor.fetchall()
                cursor.execute("SELECT VERSION() AS version")
                return str(cursor.fetchone()["version"])

    @contextmanager
    def transaccion(self):
        """Una sola conexión para todo el bloque: se confirma completo o no se guarda nada."""
        if self._conexion is not None:
            yield self
            return
        conexion = self._conectar()
        self._conexion = conexion
        self._pendiente = {}
        try:
            yield self
            conexion.commit()
            self._guardado.update(self._pendiente)
        except conector.Error as error:
            self._deshacer(conexion)
            raise self._traducir(error) from error
        except BaseException:
            self._deshacer(conexion)
            raise
        finally:
            self._conexion = None
            self._pendiente = {}
            self._cerrar(conexion)

    def cargar_lista(self, nombre: str) -> list:
        lector = _LECTORES.get(nombre)
        if lector is None:
            raise PersistenciaError(f"MySQL no tiene una colección llamada {nombre}")
        with self.transaccion():
            with self._cursor() as cursor:
                datos = lector(cursor)
            self._pendiente[nombre] = {item[_CLAVES[nombre]]: copy.deepcopy(item) for item in datos}
        return datos

    def cargar_objeto(self, nombre: str) -> dict:
        raise PersistenciaError(f"MySQL no tiene un objeto llamado {nombre}")

    def guardar(self, nombre: str, datos: list | dict) -> None:
        escritor = _ESCRITORES.get(nombre)
        if escritor is None:
            raise PersistenciaError(f"MySQL no tiene una colección llamada {nombre}")
        clave = _CLAVES[nombre]
        actual = {item[clave]: copy.deepcopy(item) for item in datos}
        with self.transaccion():
            previo = self._pendiente.get(nombre, self._guardado.get(nombre, {}))
            cambiados = [(item, previo.get(k)) for k, item in actual.items() if previo.get(k) != item]
            if cambiados:
                with self._cursor() as cursor:
                    for item, anterior in cambiados:
                        escritor(cursor, item, anterior)
            self._pendiente[nombre] = actual

    # --- conexión ------------------------------------------------------------

    @contextmanager
    def _cursor(self):
        """Cursor de la transacción en curso (siempre se usa dentro de `transaccion`)."""
        cursor = self._conexion.cursor(dictionary=True)
        try:
            yield cursor
        finally:
            try:
                cursor.close()
            except conector.Error:
                pass

    def _conectar(self):
        c = self._configuracion
        try:
            return conector.connect(
                host=c.host,
                port=c.puerto,
                user=c.usuario,
                password=c.contrasena,
                database=c.base_datos,
                charset="utf8mb4",
                collation="utf8mb4_unicode_ci",
                connection_timeout=5,
                autocommit=False,
            )
        except conector.Error as error:
            raise self._traducir(error) from error

    def _traducir(self, error) -> PersistenciaError:
        c = self._configuracion
        codigo = getattr(error, "errno", None)
        if codigo in _SIN_CONEXION:
            mensaje = (
                f"No se pudo conectar a MySQL en {c.host}:{c.puerto}. "
                "Revisa que el servidor esté encendido y los datos de configuracion.ini."
            )
        elif codigo == _ACCESO_DENEGADO:
            mensaje = f"MySQL rechazó al usuario {c.usuario}. Revisa el usuario y la contraseña."
        elif codigo in _SIN_BASE:
            mensaje = (
                f"La base de datos {c.base_datos} no existe o el usuario {c.usuario} no tiene acceso. "
                "Créala ejecutando database/01_esquema.sql en MySQL Workbench."
            )
        elif codigo == _SIN_TABLA:
            mensaje = (
                f"A la base de datos {c.base_datos} le faltan tablas. "
                f"Ejecuta database/01_esquema.sql. Detalle: {getattr(error, 'msg', None) or error}"
            )
        elif codigo == _DUPLICADO:
            mensaje = "MySQL rechazó el dato porque ya existe un registro con ese identificador."
        elif codigo in _DATO_EXCEDIDO:
            mensaje = (
                "MySQL rechazó el dato porque supera el largo o el valor máximo de su columna. "
                f"Detalle: {getattr(error, 'msg', None) or error}"
            )
        elif codigo in _REFERENCIA:
            mensaje = "MySQL rechazó el cambio: el registro está relacionado con otros datos."
        else:
            mensaje = f"Error de MySQL: {getattr(error, 'msg', None) or error}"
        return PersistenciaError(mensaje)

    @staticmethod
    def _deshacer(conexion) -> None:
        try:
            conexion.rollback()
        except Exception:
            pass

    @staticmethod
    def _cerrar(conexion) -> None:
        try:
            conexion.close()
        except Exception:
            pass
