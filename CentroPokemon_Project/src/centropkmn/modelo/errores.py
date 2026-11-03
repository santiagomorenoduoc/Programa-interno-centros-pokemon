class ReglaNegocioError(ValueError):
    """Una operación viola las reglas del Centro Pokémon."""

class PersistenciaError(RuntimeError):
    """No se pudo leer o escribir los datos locales."""
