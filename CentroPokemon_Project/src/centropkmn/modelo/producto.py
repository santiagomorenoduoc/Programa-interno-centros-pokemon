from abc import ABC, abstractmethod
from centropkmn.modelo.errores import ReglaNegocioError
from centropkmn.modelo.validaciones import exigir_entero, texto_obligatorio

class Producto(ABC):
    def __init__(self, id: str, centro_id: str, nombre: str, cantidad: int, descripcion: str):
        self._id = texto_obligatorio(id, "Identificador")
        self._centro_id = texto_obligatorio(centro_id, "Centro Pokémon asignado")
        self._nombre = texto_obligatorio(nombre, "Nombre del producto")
        self._cantidad = exigir_entero(cantidad, "Cantidad", minimo=0)
        self._descripcion = texto_obligatorio(descripcion, "Descripción")

    @property
    def id(self) -> str: return self._id
    @property
    def centro_id(self) -> str: return self._centro_id
    @property
    def nombre(self) -> str: return self._nombre
    @property
    def cantidad(self) -> int: return self._cantidad
    @property
    def descripcion(self) -> str: return self._descripcion

    @property
    @abstractmethod
    def categoria(self) -> str: pass

    def descontar(self, n: int = 1) -> None:
        n_val = exigir_entero(n, "Cantidad a usar", minimo=1)
        if n_val > self._cantidad:
            raise ReglaNegocioError(f"Inventario insuficiente de {self._nombre}. Disponible: {self._cantidad}")
        self._cantidad -= n_val

    def reponer(self, n: int = 1) -> None:
        self._cantidad += exigir_entero(n, "Cantidad a ingresar", minimo=1)

    def a_diccionario(self) -> dict:
        d = {
            "id": self._id, "centro_id": self._centro_id, "categoria": self.categoria,
            "nombre": self._nombre, "cantidad": self._cantidad, "descripcion": self._descripcion
        }
        d.update(self._extras())
        return d

    @abstractmethod
    def _extras(self) -> dict: pass

class Medicina(Producto):
    def __init__(self, id: str, centro_id: str, nombre: str, cantidad: int, descripcion: str, puntos_curacion: int):
        super().__init__(id, centro_id, nombre, cantidad, descripcion)
        self._puntos_curacion = exigir_entero(puntos_curacion, "Puntos de curación", minimo=1)

    @property
    def categoria(self) -> str: return "Medicina"
    @property
    def puntos_curacion(self) -> int: return self._puntos_curacion
    def _extras(self) -> dict: return {"puntos_curacion": self._puntos_curacion}

class InsumoCaptura(Producto):
    def __init__(self, id: str, centro_id: str, nombre: str, cantidad: int, descripcion: str, ratio_captura: float):
        super().__init__(id, centro_id, nombre, cantidad, descripcion)
        self._ratio_captura = ratio_captura

    @property
    def categoria(self) -> str: return "Pokébola/Captura"
    @property
    def ratio_captura(self) -> float: return self._ratio_captura
    def _extras(self) -> dict: return {"ratio_captura": self._ratio_captura}

def producto_desde_diccionario(datos: dict) -> Producto:
    cat = datos["categoria"]
    if cat == "Medicina":
        return Medicina(str(datos["id"]), datos["centro_id"], datos["nombre"], datos["cantidad"], datos["descripcion"], datos.get("puntos_curacion", 20))
    elif cat == "Pokébola/Captura":
        return InsumoCaptura(str(datos["id"]), datos["centro_id"], datos["nombre"], datos["cantidad"], datos["descripcion"], datos.get("ratio_captura", 1.0))
    raise ReglaNegocioError("Categoría de producto desconocida")
