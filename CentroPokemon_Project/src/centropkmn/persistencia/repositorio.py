"""Contrato común de los repositorios. El modelo no sabe si guarda en JSON o en MySQL."""

from abc import ABC, abstractmethod
from contextlib import contextmanager


class Repositorio(ABC):
    """Guarda y recupera colecciones por nombre: centros, entrenadores, personal,
    productos, pokemones y donaciones. Cada colección es una lista de diccionarios."""

    def __init__(self):
        self.advertencias: list[str] = []

    @property
    @abstractmethod
    def descripcion(self) -> str:
        """Texto visible del origen de los datos."""

    @abstractmethod
    def cargar_lista(self, nombre: str) -> list:
        """Devuelve los registros de una colección como diccionarios."""

    @abstractmethod
    def cargar_objeto(self, nombre: str) -> dict:
        """Devuelve un objeto único (no se usa hoy en Centro Pokémon)."""

    @abstractmethod
    def guardar(self, nombre: str, datos: list | dict) -> None:
        """Deja la colección guardada tal como viene en `datos`."""

    @contextmanager
    def transaccion(self):
        """Agrupa varias lecturas o escrituras. Por defecto no hace nada especial."""
        yield self
