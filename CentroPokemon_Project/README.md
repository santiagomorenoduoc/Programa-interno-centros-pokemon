# Centro Pokémon — Sistema Multi-Sede de Atención y Gestión

Sistema de gestión para Centros Pokémon en Python con Tkinter, arquitectura MVC, persistencia JSON atómica y gestión de múltiples sedes/centros independientes.

## Características Multi-Sede
- **Centros/Sedes (`centros.json`)**: Registro independiente de sedes (ej. Ciudad Verde, Ciudad Plateada).
- **Inventario por Centro**: Cada insumo o medicina pertenece exclusivamente a un `centro_id`.
- **Personal por Centro**: Asignación de Enfermeras Joy a sedes específicas.
- **Pacientes por Centro**: Admisión, triage y curación focalizados en la sede activa.
- **Donaciones por Sede**: Aportes en ₽ o insumos direccionados al centro seleccionado.

## Ejecución

Requiere Python 3.10 o superior.

```bash
# Ejecutar interfaz gráfica
python -m src.centropkmn

# Ejecutar demo de prueba multi-sede en consola
python -m src.centropkmn.demo
```
