import json
from pathlib import Path
from centropkmn.modelo.errores import PersistenciaError

class RepositorioJSON:
    def __init__(self, directorio: str | Path):
        self.directorio = Path(directorio)
        self.advertencias: list[str] = []
        try:
            self.directorio.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise PersistenciaError(f"No se pudo preparar la carpeta de datos: {error}") from error

    def cargar_lista(self, nombre: str) -> list:
        datos = self._leer(nombre)
        return datos if isinstance(datos, list) else []

    def cargar_objeto(self, nombre: str) -> dict:
        datos = self._leer(nombre)
        return datos if isinstance(datos, dict) else {}

    def guardar(self, nombre: str, datos: list | dict) -> None:
        ruta = self.directorio / f"{nombre}.json"
        temporal = self.directorio / f"{nombre}.json.tmp"
        try:
            contenido = json.dumps(datos, ensure_ascii=False, indent=2) + "\n"
            temporal.write_text(contenido, encoding="utf-8")
            temporal.replace(ruta)
        except OSError as error:
            raise PersistenciaError(f"No se pudo guardar {nombre}.json: {error}") from error

    def _leer(self, nombre: str):
        ruta = self.directorio / f"{nombre}.json"
        if not ruta.exists(): return None
        try:
            return json.loads(ruta.read_text(encoding="utf-8"))
        except Exception: return None
