from centropkmn.modelo.errores import ReglaNegocioError

def texto_obligatorio(valor: object, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ReglaNegocioError(f"{campo} es obligatorio y no puede estar vacío.")
    return valor.strip()

def booleano(valor: object, campo: str) -> bool:
    if type(valor) is not bool:
        raise ReglaNegocioError(f"{campo} debe ser un valor booleano (Sí/No).")
    return valor

def exigir_entero(valor: object, campo: str, minimo: int = 0) -> int:
    if type(valor) is not int:
        try:
            valor = int(valor)
        except (ValueError, TypeError):
            raise ReglaNegocioError(f"{campo} debe ser un número entero.")
    if valor < minimo:
        raise ReglaNegocioError(f"{campo} debe ser mayor o igual a {minimo}.")
    return valor

def nivel_obligatorio(valor: object, campo: str = "Nivel") -> int:
    num = exigir_entero(valor, campo, minimo=1)
    if num > 100:
        raise ReglaNegocioError(f"{campo} no puede ser mayor a 100.")
    return num
