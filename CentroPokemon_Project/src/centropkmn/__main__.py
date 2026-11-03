import tkinter as tk
from tkinter import messagebox
from centropkmn.modelo.errores import PersistenciaError

def main() -> None:
    try:
        from centropkmn.vista.aplicacion import iniciar
        iniciar()
    except PersistenciaError as error:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("Centro Pokémon", str(error))
        raiz.destroy()

if __name__ == "__main__":
    main()
