from tempfile import TemporaryDirectory
from centropkmn.controladores.controlador import Controlador

def main() -> None:
    with TemporaryDirectory() as carpeta:
        ctl = Controlador(carpeta)
        ctl2 = Controlador()

        c1 = ctl.registrar_centro("Centro Pokémon Ciudad Verde", "Kanto - Ruta 1", fondos=10000)
        c2 = ctl.registrar_centro("Centro Pokémon Ciudad Plateada", "Kanto - Ruta 3", fondos=5000)

        print(f"=== CENTROS REGISTRADOS ===")
        for c in ctl.listar_centros():
            print(f" - [{c.id}] {c.nombre} ({c.ubicacion}) | Fondos: ₽{c.fondos:,}")

        ash = ctl.registrar_entrenador("Ash Ketchum", "+56911111111", "ash@pallet.town", True)
        brock = ctl.registrar_entrenador("Brock Slate", "+56933333333", "brock@pewter.gym", True)

        joy1 = ctl.registrar_personal(c1.id, "Enfermera Joy (Verde)", "+56988888888", "joy.verde@pkmn.center", "Enfermera Jefe")
        joy2 = ctl.registrar_personal(c2.id, "Enfermera Joy (Plateada)", "+56977777777", "joy.plateada@pkmn.center", "Enfermera Jefe")

        med1 = ctl.registrar_producto_medicina(c1.id, "Max Poción", 5, "Restaura HP por completo", 100)
        med2 = ctl.registrar_producto_medicina(c2.id, "Superpoción", 3, "Restaura 50 HP", 50)

        pk1 = ctl.ingresar_pokemon(c1.id, "Pikachu", "Pikachu", "Eléctrico", 25, 0, 80, "Pokébola Standard", "Agotamiento tras combate", ash.id)
        pk2 = ctl.ingresar_pokemon(c2.id, "Onix", "Onix", "Roca", 30, 10, 90, "Superball", "Fisura en roca", brock.id)

        print(f"\n=== ATENCIÓN EN CIUDAD VERDE ({c1.id}) ===")
        print(f"Paciente: {pk1.nombre} en {pk1.centro_id} - Salud: {pk1.hp_actual}/{pk1.hp_maximo} ({pk1.estado.etiqueta})")
        ctl.diagnosticar_pokemon(pk1.id, joy1.id)
        ctl.aplicar_tratamiento(pk1.id, med1.id)
        ctl.dar_alta(pk1.id)
        print(f"Estado Final de {pk1.nombre}: {pk1.estado.etiqueta} (Salud: {pk1.hp_actual}/{pk1.hp_maximo})")

        print(f"\n=== ATENCIÓN EN CIUDAD PLATEADA ({c2.id}) ===")
        print(f"Paciente: {pk2.nombre} en {pk2.centro_id} - Salud: {pk2.hp_actual}/{pk2.hp_maximo} ({pk2.estado.etiqueta})")
        ctl.diagnosticar_pokemon(pk2.id, joy2.id)
        ctl.aplicar_tratamiento(pk2.id, med2.id)
        print(f"Estado de {pk2.nombre} tras tratamiento: {pk2.estado.etiqueta} (Salud: {pk2.hp_actual}/{pk2.hp_maximo})")

        don1 = ctl.registrar_donacion_monetaria(c1.id, "Misty", 2000, "Liga Pokémon")
        don2 = ctl.registrar_donacion_monetaria(c2.id, "Profesor Oak", 5000, "Beca de Investigación")

        print(f"\n=== BALANCES FINALES ===")
        print(f"Sede Ciudad Verde ({c1.id}): ₽{ctl._centro.obtener_centro(c1.id).fondos:,}")
        print(f"Sede Ciudad Plateada ({c2.id}): ₽{ctl._centro.obtener_centro(c2.id).fondos:,}")

        personal_verde = ctl2.listar_personal(centro_id="cp-verde")
        print("personal disponible en sede de ciudad verde ")

        for persona in personal_verde:
         print(
            f"ID: {persona.id} | Nombre: {persona.nombre} | Cargo: {persona.cargo} |"
            f" Activa: {persona.activa}"
        )

        print("\nSimulación del sistema multi-sede ejecutada con éxito.")

if __name__ == "__main__":
    main()
