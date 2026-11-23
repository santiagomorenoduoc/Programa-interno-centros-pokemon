"""Configuración de la persistencia, guardada en configuracion.ini.

El archivo permite cambiar de JSON a MySQL y ajustar la conexión sin tocar el código.
"""

from configparser import ConfigParser, Error as ErrorIni
from dataclasses import dataclass, field
from pathlib import Path

from centropkmn.modelo.errores import PersistenciaError, ReglaNegocioError

MOTORES = ("json", "mysql")


@dataclass(frozen=True)
class ConfiguracionMySQL:
    host: str = "127.0.0.1"
    puerto: int = 3306
    usuario: str = "root"
    contrasena: str = field(default="", repr=False)
    base_datos: str = "centro_pokemon"

    def __post_init__(self):
        for valor, campo in ((self.host, "Servidor"), (self.usuario, "Usuario"), (self.base_datos, "Base de datos")):
            if not isinstance(valor, str) or not valor.strip():
                raise ReglaNegocioError(f"{campo} es obligatorio")
        if type(self.puerto) is not int or not 1 <= self.puerto <= 65535:
            raise ReglaNegocioError("Puerto debe ser un entero entre 1 y 65535")
        if not isinstance(self.contrasena, str):
            raise ReglaNegocioError("Contraseña no válida")


@dataclass(frozen=True)
class Configuracion:
    motor: str = "json"
    mysql: ConfiguracionMySQL = field(default_factory=ConfiguracionMySQL)

    def __post_init__(self):
        if self.motor not in MOTORES:
            raise ReglaNegocioError("La persistencia debe ser json o mysql")


def leer_configuracion(ruta: str | Path) -> Configuracion:
    """Lee el .ini. Si no existe, la aplicación trabaja con JSON."""
    ruta = Path(ruta)
    if not ruta.exists():
        return Configuracion()
    lector = ConfigParser(interpolation=None)
    try:
        lector.read_string(ruta.read_text(encoding="utf-8"))
        base = ConfiguracionMySQL()
        mysql = ConfiguracionMySQL(
            host=lector.get("mysql", "host", fallback=base.host).strip(),
            puerto=lector.getint("mysql", "puerto", fallback=base.puerto),
            usuario=lector.get("mysql", "usuario", fallback=base.usuario).strip(),
            contrasena=lector.get("mysql", "contrasena", fallback=base.contrasena),
            base_datos=lector.get("mysql", "base_datos", fallback=base.base_datos).strip(),
        )
        motor = lector.get("persistencia", "motor", fallback="json").strip().lower()
        return Configuracion(motor, mysql)
    except (OSError, ErrorIni, ValueError) as error:
        raise PersistenciaError(f"No se pudo leer la configuración {ruta.name}: {error}") from error
