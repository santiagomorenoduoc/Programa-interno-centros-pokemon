from centropkmn.controladores.controlador import Controlador
from centropkmn.modelo.producto import InsumoCaptura, Medicina

ctl = Controlador()

sede_id = ctl.centro_activo_id

nueva_medicina = Medicina(
    id="med-maxpocion-01",
    centro_id=sede_id,
    nombre="Max Poción Cítrica",
    cantidad=40,
    descripcion="Restablece 200 PS de salud",
    puntos_curacion=200,
)

ctl.agregar_producto(nueva_medicina)
print(
    f"Producto guardado: {nueva_medicina.nombre} ({nueva_medicina.cantidad}"
    " unids)"
)

nueva_pokebola = InsumoCaptura(
    id="ball-ultraball-01",
    centro_id=sede_id,
    nombre="Ultraball de Lujo",
    cantidad=15,
    descripcion="Dispositivo de captura con alto ratio de éxito",
    ratio_captura=2.0,
)

ctl.agregar_producto(nueva_pokebola)

ctl.actualizar_stock("med-maxpocion-01", nueva_cantidad=75)
print("Stock actualizado a 75 unidades de forma manual.")