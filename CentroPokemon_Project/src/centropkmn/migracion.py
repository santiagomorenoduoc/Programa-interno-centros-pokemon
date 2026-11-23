"""Copia los datos de data/*.json a MySQL (se usa una sola vez).

Antes: ejecutar database/01_esquema.sql en MySQL Workbench y crear configuracion.ini
con motor = mysql. Se puede repetir sin duplicar datos: lo que ya existe se actualiza.

Uso (igual que la aplicación):  python -m centropkmn.migracion
"""

from centropkmn.modelo.errores import PersistenciaError
from centropkmn.persistencia.configuracion import leer_configuracion
from centropkmn.persistencia.repositorio_json import RepositorioJSON
from centropkmn.persistencia.repositorio_mysql import RepositorioMySQL
from centropkmn.rutas import directorio_datos, ruta_configuracion

# Orden que respeta las llaves foráneas: primero lo que otros necesitan.
COLECCIONES = ("centros", "entrenadores", "personal", "productos", "pokemones", "donaciones")


def main() -> None:
    try:
        configuracion = leer_configuracion(ruta_configuracion())
        destino = RepositorioMySQL(configuracion.mysql)
        origen = RepositorioJSON(directorio_datos())
        print(f"Origen : {origen.descripcion}")
        print(f"Destino: {destino.descripcion} — servidor MySQL {destino.probar()}")
        with destino.transaccion():  # todo o nada
            for nombre in COLECCIONES:
                datos = origen.cargar_lista(nombre)
                destino.cargar_lista(nombre)  # reconoce lo que ya existe para no duplicarlo
                destino.guardar(nombre, datos)
                print(f"  {nombre:<13} {len(datos)} registros")
        print("Migración terminada.")
    except PersistenciaError as error:
        print(f"No se pudo migrar: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
