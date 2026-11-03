from centropkmn.modelo.errores import ReglaNegocioError
from centropkmn.modelo.validaciones import booleano, texto_obligatorio

class Persona:
    def __init__(self, id: str, nombre: str, telefono: str, correo: str):
        self._id = texto_obligatorio(id, "Identificador")
        self._nombre = texto_obligatorio(nombre, "Nombre")
        self._telefono = texto_obligatorio(telefono, "Teléfono")
        self._correo = texto_obligatorio(correo, "Correo")

    @property
    def id(self) -> str: return self._id
    @property
    def nombre(self) -> str: return self._nombre
    @property
    def telefono(self) -> str: return self._telefono
    @property
    def correo(self) -> str: return self._correo

class Entrenador(Persona):
    def __init__(self, id: str, nombre: str, telefono: str, correo: str, licencia_oficial: bool = True):
        super().__init__(id, nombre, telefono, correo)
        self._licencia_oficial = booleano(licencia_oficial, "Licencia de Entrenador")

    @property
    def licencia_oficial(self) -> bool: return self._licencia_oficial

    def a_diccionario(self) -> dict:
        return {
            "id": self._id, "nombre": self._nombre, "telefono": self._telefono,
            "correo": self._correo, "licencia_oficial": self._licencia_oficial
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Entrenador":
        return cls(str(datos["id"]), datos["nombre"], datos["telefono"], datos["correo"], datos.get("licencia_oficial", True))

class Personal(Persona):
    def __init__(self, id: str, centro_id: str, nombre: str, telefono: str, correo: str, cargo: str, activa: bool = True):
        super().__init__(id, nombre, telefono, correo)
        self._centro_id = texto_obligatorio(centro_id, "Centro Pokémon asignado")
        self._cargo = texto_obligatorio(cargo, "Cargo")
        self._activa = booleano(activa, "Disponibilidad")

    @property
    def centro_id(self) -> str: return self._centro_id
    @property
    def cargo(self) -> str: return self._cargo
    @property
    def activa(self) -> bool: return self._activa

    def a_diccionario(self) -> dict:
        return {
            "id": self._id, "centro_id": self._centro_id, "nombre": self._nombre,
            "telefono": self._telefono, "correo": self._correo,
            "cargo": self._cargo, "activa": self._activa
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Personal":
        return cls(
            str(datos["id"]), datos["centro_id"], datos["nombre"],
            datos["telefono"], datos["correo"], datos["cargo"], datos.get("activa", True)
        )
