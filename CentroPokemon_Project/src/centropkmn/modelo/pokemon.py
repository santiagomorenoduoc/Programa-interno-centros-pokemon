from enum import Enum
from centropkmn.modelo.errores import ReglaNegocioError
from centropkmn.modelo.validaciones import nivel_obligatorio, exigir_entero, texto_obligatorio

class EstadoPokemon(Enum):
    ADMITIDO = "ADMITIDO"
    EN_REVISION = "EN_REVISION"
    EN_TRATAMIENTO = "EN_TRATAMIENTO"
    TRATADO = "TRATADO"
    ALTA = "ALTA"
    CANCELADO = "CANCELADO"

    @property
    def etiqueta(self) -> str:
        return {
            EstadoPokemon.ADMITIDO: "Admitido en Urgencias",
            EstadoPokemon.EN_REVISION: "En Triage / Revisión",
            EstadoPokemon.EN_TRATAMIENTO: "En Tratamiento Clínico",
            EstadoPokemon.TRATADO: "Recuperado / Restablecido",
            EstadoPokemon.ALTA: "Dado de Alta Médica",
            EstadoPokemon.CANCELADO: "Atención Cancelada",
        }[self]

_TRANSICIONES = {
    EstadoPokemon.ADMITIDO: {EstadoPokemon.EN_REVISION, EstadoPokemon.CANCELADO},
    EstadoPokemon.EN_REVISION: {EstadoPokemon.EN_TRATAMIENTO, EstadoPokemon.TRATADO, EstadoPokemon.CANCELADO},
    EstadoPokemon.EN_TRATAMIENTO: {EstadoPokemon.TRATADO, EstadoPokemon.CANCELADO},
    EstadoPokemon.TRATADO: {EstadoPokemon.ALTA,EstadoPokemon.EN_REVISION},
    EstadoPokemon.ALTA: set(),
    EstadoPokemon.CANCELADO: set(),
}

class Pokemon:
    def __init__(self, id: str, centro_id: str, nombre: str, especie: str, tipo: str, nivel: int, hp_actual: int, hp_maximo: int, pokebola: str, sintomas: str, entrenador_id: str):
        self._id = texto_obligatorio(id, "Identificador")
        self._centro_id = texto_obligatorio(centro_id, "Centro Pokémon de atención")
        self._nombre = texto_obligatorio(nombre, "Mote / Nombre")
        self._especie = texto_obligatorio(especie, "Especie Pokémon")
        self._tipo = texto_obligatorio(tipo, "Tipo elemental")
        self._nivel = nivel_obligatorio(nivel, "Nivel")
        self._hp_actual = exigir_entero(hp_actual, "HP Actual", minimo=0)
        self._hp_maximo = exigir_entero(hp_maximo, "HP Máximo", minimo=1)
        if self._hp_actual > self._hp_maximo:
            raise ReglaNegocioError("El HP actual no puede exceder el HP máximo.")
        self._pokebola = texto_obligatorio(pokebola, "Pokébola de transporte")
        self._sintomas = texto_obligatorio(sintomas, "Síntomas")
        self._entrenador_id = texto_obligatorio(entrenador_id, "Entrenador responsable")

        self._estado = EstadoPokemon.ADMITIDO
        self._historial = [EstadoPokemon.ADMITIDO]
        self._enfermera_id = None
        self._medicina_usada_id = None

    @property
    def id(self) -> str: return self._id
    @property
    def centro_id(self) -> str: return self._centro_id
    @property
    def nombre(self) -> str: return self._nombre
    @property
    def especie(self) -> str: return self._especie
    @property
    def tipo(self) -> str: return self._tipo
    @property
    def nivel(self) -> int: return self._nivel
    @property
    def hp_actual(self) -> int: return self._hp_actual
    @property
    def hp_maximo(self) -> int: return self._hp_maximo
    @property
    def pokebola(self) -> str: return self._pokebola
    @property
    def sintomas(self) -> str: return self._sintomas
    @property
    def entrenador_id(self) -> str: return self._entrenador_id
    @property
    def enfermera_id(self) -> str | None: return self._enfermera_id
    @property
    def medicina_usada_id(self) -> str | None: return self._medicina_usada_id
    @property
    def estado(self) -> EstadoPokemon: return self._estado
    @property
    def historial(self) -> tuple[EstadoPokemon, ...]: return tuple(self._historial)

    def diagnosticar(self, enfermera_id: str) -> None:
        self._enfermera_id = texto_obligatorio(enfermera_id, "Enfermera asignada")
        self._transicionar(EstadoPokemon.EN_REVISION)

    def aplicar_tratamiento(self, medicina_id: str, hp_restaurados: int) -> None:
        if self._estado not in {EstadoPokemon.EN_REVISION, EstadoPokemon.EN_TRATAMIENTO}:
            raise ReglaNegocioError("El Pokémon debe estar en revisión o tratamiento para administrar medicinas.")
        self._medicina_usada_id = texto_obligatorio(medicina_id, "Medicina")
        self._hp_actual = min(self._hp_maximo, self._hp_actual + hp_restaurados)
        self._transicionar(EstadoPokemon.TRATADO)

    def dar_alta(self) -> None:
        if self._estado is not EstadoPokemon.TRATADO:
            raise ReglaNegocioError("Solo se puede dar de alta a un Pokémon completamente tratado.")
        self._transicionar(EstadoPokemon.ALTA)

    def cancelar(self) -> None:
        if self._estado in {EstadoPokemon.ALTA, EstadoPokemon.CANCELADO}:
            raise ReglaNegocioError("No se puede cancelar en el estado actual.")
        self._transicionar(EstadoPokemon.CANCELADO)

    def _transicionar(self, nuevo: EstadoPokemon) -> None:
        if nuevo not in _TRANSICIONES[self._estado]:
            raise ReglaNegocioError(f"No se permite cambiar de {self._estado.etiqueta} a {nuevo.etiqueta}.")
        self._estado = nuevo
        self._historial.append(nuevo)

    def a_diccionario(self) -> dict:
        return {
            "id": self._id, "centro_id": self._centro_id, "nombre": self._nombre,
            "especie": self._especie, "tipo": self._tipo, "nivel": self._nivel,
            "hp_actual": self._hp_actual, "hp_maximo": self._hp_maximo,
            "pokebola": self._pokebola, "sintomas": self._sintomas,
            "entrenador_id": self._entrenador_id, "enfermera_id": self._enfermera_id,
            "medicina_usada_id": self._medicina_usada_id, "estado": self._estado.value,
            "historial": [e.value for e in self._historial]
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Pokemon":
        pk = cls(
            datos["id"], datos["centro_id"], datos["nombre"], datos["especie"],
            datos["tipo"], datos["nivel"], datos["hp_actual"], datos["hp_maximo"],
            datos["pokebola"], datos["sintomas"], datos["entrenador_id"]
        )
        pk._enfermera_id = datos.get("enfermera_id")
        pk._medicina_usada_id = datos.get("medicina_usada_id")
        pk._estado = EstadoPokemon(datos["estado"])
        pk._historial = [EstadoPokemon(v) for v in datos["historial"]]
        return pk
