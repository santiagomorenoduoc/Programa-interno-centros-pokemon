

CREATE DATABASE IF NOT EXISTS centro_pokemon
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE centro_pokemon;

--centros (CentroSede)--
CREATE TABLE IF NOT EXISTS centros (
  id_centro      VARCHAR(40)  NOT NULL,
  nombre         VARCHAR(100) NOT NULL,
  ubicacion      VARCHAR(150) NOT NULL,
  fondos         BIGINT UNSIGNED NOT NULL DEFAULT 0,
  activo         TINYINT(1)   NOT NULL DEFAULT 1,
  fecha_creacion DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id_centro)
) ENGINE=InnoDB;

--personas (Persona) + sus dos subclases--
CREATE TABLE IF NOT EXISTS personas (
  id_persona     VARCHAR(40)  NOT NULL,
  nombre         VARCHAR(100) NOT NULL,
  telefono       VARCHAR(30)  NOT NULL,
  correo         VARCHAR(120) NOT NULL,
  tipo_persona   ENUM('ENTRENADOR','PERSONAL') NOT NULL,
  fecha_registro DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id_persona)
) ENGINE=InnoDB;

--Entrenador(licencia_oficial)--
CREATE TABLE IF NOT EXISTS entrenadores (
  id_persona       VARCHAR(40) NOT NULL,
  licencia_oficial TINYINT(1)  NOT NULL DEFAULT 1,
  PRIMARY KEY (id_persona),
  CONSTRAINT fk_entrenadores_persona FOREIGN KEY (id_persona)
    REFERENCES personas (id_persona) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Personal(centro_id, cargo, activa)  — las "Enfermeras Joy"
CREATE TABLE IF NOT EXISTS personal (
  id_persona VARCHAR(40) NOT NULL,
  id_centro  VARCHAR(40) NOT NULL,
  cargo      VARCHAR(80) NOT NULL,
  activa     TINYINT(1)  NOT NULL DEFAULT 1,
  PRIMARY KEY (id_persona),
  KEY idx_personal_centro (id_centro),
  CONSTRAINT fk_personal_persona FOREIGN KEY (id_persona)
    REFERENCES personas (id_persona) ON DELETE CASCADE,
  CONSTRAINT fk_personal_centro FOREIGN KEY (id_centro)
    REFERENCES centros (id_centro)
) ENGINE=InnoDB;

--productos (Producto) + Medicina / InsumoCaptura--
CREATE TABLE IF NOT EXISTS productos (
  id_producto    VARCHAR(40)  NOT NULL,
  id_centro      VARCHAR(40)  NOT NULL,
  nombre         VARCHAR(100) NOT NULL,
  cantidad       INT UNSIGNED NOT NULL DEFAULT 0,
  descripcion    VARCHAR(255) NOT NULL,
  categoria      ENUM('Medicina','Pokébola/Captura') NOT NULL,
  fecha_creacion DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id_producto),
  KEY idx_productos_centro (id_centro),
  CONSTRAINT fk_productos_centro FOREIGN KEY (id_centro)
    REFERENCES centros (id_centro)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS medicinas (
  id_producto     VARCHAR(40)  NOT NULL,
  puntos_curacion INT UNSIGNED NOT NULL,
  PRIMARY KEY (id_producto),
  CONSTRAINT fk_medicinas_producto FOREIGN KEY (id_producto)
    REFERENCES productos (id_producto) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS insumos_captura (
  id_producto   VARCHAR(40) NOT NULL,
  ratio_captura DOUBLE      NOT NULL DEFAULT 1,
  PRIMARY KEY (id_producto),
  CONSTRAINT fk_insumos_producto FOREIGN KEY (id_producto)
    REFERENCES productos (id_producto) ON DELETE CASCADE
) ENGINE=InnoDB;

--pokemones (Pokemon)--
CREATE TABLE IF NOT EXISTS pokemones (
  id_pokemon        VARCHAR(40)  NOT NULL,
  id_centro         VARCHAR(40)  NOT NULL,
  id_entrenador     VARCHAR(40)  NOT NULL,
  id_enfermera      VARCHAR(40)  NULL,
  id_medicina_usada VARCHAR(40)  NULL,
  nombre            VARCHAR(80)  NOT NULL,
  especie           VARCHAR(80)  NOT NULL,
  tipo              VARCHAR(60)  NOT NULL,
  nivel             TINYINT UNSIGNED NOT NULL,
  hp_actual         INT UNSIGNED NOT NULL,
  hp_maximo         INT UNSIGNED NOT NULL,
  pokebola          VARCHAR(80)  NOT NULL,
  sintomas          VARCHAR(500) NOT NULL,
  estado            ENUM('ADMITIDO','EN_REVISION','EN_TRATAMIENTO','TRATADO','ALTA','CANCELADO')
                    NOT NULL DEFAULT 'ADMITIDO',
  fecha_ingreso     DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id_pokemon),
  KEY idx_pokemones_centro (id_centro),
  CONSTRAINT chk_pokemones_nivel CHECK (nivel BETWEEN 1 AND 100),
  CONSTRAINT chk_pokemones_hp    CHECK (hp_maximo >= 1 AND hp_actual <= hp_maximo),
  CONSTRAINT fk_pokemones_centro     FOREIGN KEY (id_centro)         REFERENCES centros (id_centro),
  CONSTRAINT fk_pokemones_entrenador FOREIGN KEY (id_entrenador)     REFERENCES entrenadores (id_persona),
  CONSTRAINT fk_pokemones_enfermera  FOREIGN KEY (id_enfermera)      REFERENCES personal (id_persona),
  CONSTRAINT fk_pokemones_medicina   FOREIGN KEY (id_medicina_usada) REFERENCES productos (id_producto)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS historial_estados_pokemon (
  id_historial BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  id_pokemon   VARCHAR(40) NOT NULL,
  estado       ENUM('ADMITIDO','EN_REVISION','EN_TRATAMIENTO','TRATADO','ALTA','CANCELADO') NOT NULL,
  fecha_cambio DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id_historial),
  KEY idx_historial_pokemon (id_pokemon),
  CONSTRAINT fk_historial_pokemon FOREIGN KEY (id_pokemon)
    REFERENCES pokemones (id_pokemon) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS donaciones (
  id_donacion    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  referencia     VARCHAR(40)  NOT NULL,
  id_centro      VARCHAR(40)  NOT NULL,
  donante_nombre VARCHAR(100) NULL,
  tipo           ENUM('Monetaria','Objetos e Insumos') NOT NULL,
  exitosa        TINYINT(1)   NOT NULL DEFAULT 1,
  mensaje        VARCHAR(500) NOT NULL,
  fecha_donacion DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id_donacion),
  UNIQUE KEY uq_donaciones_referencia (referencia),
  KEY idx_donaciones_centro (id_centro),
  CONSTRAINT fk_donaciones_centro FOREIGN KEY (id_centro) REFERENCES centros (id_centro)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS donacion_monetarias (
  id_donacion INT UNSIGNED NOT NULL,
  monto       INT UNSIGNED NOT NULL,
  medio       VARCHAR(80)  NOT NULL,
  PRIMARY KEY (id_donacion),
  CONSTRAINT fk_don_mon_donacion FOREIGN KEY (id_donacion)
    REFERENCES donaciones (id_donacion) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS donacion_objetos (
  id_donacion INT UNSIGNED NOT NULL,
  id_producto VARCHAR(40)  NOT NULL,
  cantidad    INT UNSIGNED NOT NULL,
  PRIMARY KEY (id_donacion),
  CONSTRAINT fk_don_obj_donacion FOREIGN KEY (id_donacion)
    REFERENCES donaciones (id_donacion) ON DELETE CASCADE,
  CONSTRAINT fk_don_obj_producto FOREIGN KEY (id_producto)
    REFERENCES productos (id_producto)
) ENGINE=InnoDB;
