# Base de datos MySQL
1. En MySQL Workbench abre y ejecuta `db_centropkmn` (crea la base `centro_pokemon` y sus tablas).
2. Abre `configuracion.ini` y escribe tu usuario y contraseña de MySQL
3. `python -m pip install mysql-connector-python`
4. Una sola vez, para pasar los datos de `data/*.json` a MySQL: `python migrar_a_mysql.py`

Con `motor = json` (o sin `configuracion.ini`) el sistema sigue guardando en `data/*.json`.

## Ejecución

# Ejecutar interfaz gráfica
python -m src.centropkmn

# Ejecutar demo de prueba multi-sede en consola
python -m src.centropkmn.demo
```
