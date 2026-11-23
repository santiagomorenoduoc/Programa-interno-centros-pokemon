"""Pasa los datos de data/*.json a MySQL (se ejecuta una sola vez):  python migrar_a_mysql.py
Antes: ejecutar db_centropkmn.sql en MySQL Workbench y poner tu contraseña en configuracion.ini.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from centropkmn.migracion import main

if __name__ == "__main__":
    main()
