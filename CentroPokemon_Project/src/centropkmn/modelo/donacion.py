from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import uuid4
from centropkmn.modelo.errores import ReglaNegocioError
from centropkmn.modelo.validaciones import exigir_entero, texto_obligatorio

@dataclass(frozen=True)
class ResultadoDonacion:
    exitosa: bool
    referencia: str
    centro_id: str
    tipo: str
    mensaje: str

    def a_diccionario(self) -> dict:
        return {
            "exitosa": self.exitosa, "referencia": self.referencia,
            "centro_id": self.centro_id, "tipo": self.tipo, "mensaje": self.mensaje
        }

class Donacion(ABC):
    def __init__(self, id: str, centro_id: str, donante_nombre: str):
        self._id = texto_obligatorio(id, "Identificador de donación")
        self._centro_id = texto_obligatorio(centro_id, "Centro Pokémon destino")
        self._donante_nombre = texto_obligatorio(donante_nombre, "Nombre del donante")

    @property
    def id(self) -> str: return self._id
    @property
    def centro_id(self) -> str: return self._centro_id
    @property
    def donante_nombre(self) -> str: return self._donante_nombre

    @property
    @abstractmethod
    def tipo(self) -> str: pass

    @abstractmethod
    def procesar(self, centro_gestor) -> ResultadoDonacion: pass

class DonacionMonetaria(Donacion):
    def __init__(self, id: str, centro_id: str, donante_nombre: str, monto: int, medio: str):
        super().__init__(id, centro_id, donante_nombre)
        self._monto = exigir_entero(monto, "Monto en Pokedólares (₽)", minimo=10)
        self._medio = texto_obligatorio(medio, "Medio de aportación")

    @property
    def tipo(self) -> str: return "Monetaria"

    def procesar(self, centro_gestor) -> ResultadoDonacion:
        centro_sede = centro_gestor.obtener_centro(self._centro_id)
        centro_sede.agregar_fondos(self._monto)
        ref = f"DON-MON-{uuid4().hex[:6].upper()}"
        msg = f"Aporte voluntario de ₽{self._monto:,} recibido para {centro_sede.nombre} vía {self._medio}. ¡Gracias {self._donante_nombre}!"
        return ResultadoDonacion(True, ref, self._centro_id, self.tipo, msg)

class DonacionObjetos(Donacion):
    def __init__(self, id: str, centro_id: str, donante_nombre: str, producto_id: str, cantidad: int):
        super().__init__(id, centro_id, donante_nombre)
        self._producto_id = texto_obligatorio(producto_id, "Producto donado")
        self._cantidad = exigir_entero(cantidad, "Cantidad de objetos", minimo=1)

    @property
    def tipo(self) -> str: return "Objetos e Insumos"

    def procesar(self, centro_gestor) -> ResultadoDonacion:
        producto = centro_gestor.obtener_producto(self._producto_id)
        producto.reponer(self._cantidad)
        centro_sede = centro_gestor.obtener_centro(self._centro_id)
        ref = f"DON-OBJ-{uuid4().hex[:6].upper()}"
        msg = f"Ingresadas {self._cantidad} unidades de {producto.nombre} al inventario de {centro_sede.nombre}. Donado por {self._donante_nombre}."
        return ResultadoDonacion(True, ref, self._centro_id, self.tipo, msg)
