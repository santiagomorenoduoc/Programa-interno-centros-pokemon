from centropkmn.modelo.errores import ReglaNegocioError
from centropkmn.modelo.validaciones import booleano, exigir_entero, texto_obligatorio

class CentroSede:
    """Representa una sede física de un Centro Pokémon."""
    def __init__(self, id: str, nombre: str, ubicacion: str, fondos: int = 0, activo: bool = True):
        self._id = texto_obligatorio(id, "Identificador del Centro")
        self._nombre = texto_obligatorio(nombre, "Nombre del Centro")
        self._ubicacion = texto_obligatorio(ubicacion, "Ubicación del Centro")
        self._fondos = exigir_entero(fondos, "Fondos del Centro", minimo=0)
        self._activo = booleano(activo, "Estado activo")

    @property
    def id(self) -> str: return self._id
    @property
    def nombre(self) -> str: return self._nombre
    @property
    def ubicacion(self) -> str: return self._ubicacion
    @property
    def fondos(self) -> int: return self._fondos
    @property
    def activo(self) -> bool: return self._activo

    def agregar_fondos(self, monto: int) -> None:
        self._fondos += exigir_entero(monto, "Monto a agregar", minimo=1)

    def a_diccionario(self) -> dict:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "ubicacion": self._ubicacion,
            "fondos": self._fondos,
            "activo": self._activo
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "CentroSede":
        return cls(
            str(datos["id"]),
            datos["nombre"],
            datos["ubicacion"],
            datos.get("fondos", 0),
            datos.get("activo", True)
        )
