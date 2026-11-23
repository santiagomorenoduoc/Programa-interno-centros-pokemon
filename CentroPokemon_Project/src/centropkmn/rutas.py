from pathlib import Path

def ruta_configuracion() -> Path:
    """configuracion.ini: primero en la carpeta desde donde se ejecuta, luego en la raíz del proyecto."""
    actual = Path.cwd() / "configuracion.ini"
    if actual.exists():
        return actual
    return Path(__file__).resolve().parents[2] / "configuracion.ini"


def directorio_datos() -> Path:
    actual = Path.cwd() / "data"
    if (actual / "pokemones.json").exists():
        return actual
    raiz = Path(__file__).resolve().parents[2]
    empaquetado = raiz / "data"
    if (empaquetado / "pokemones.json").exists():
        return empaquetado
    return actual
