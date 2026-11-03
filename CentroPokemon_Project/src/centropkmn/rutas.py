from pathlib import Path

def directorio_datos() -> Path:
    actual = Path.cwd() / "data"
    if (actual / "pokemones.json").exists():
        return actual
    raiz = Path(__file__).resolve().parents[2]
    empaquetado = raiz / "data"
    if (empaquetado / "pokemones.json").exists():
        return empaquetado
    return actual
