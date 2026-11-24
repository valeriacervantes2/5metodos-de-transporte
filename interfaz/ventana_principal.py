
import tkinter as tk
from tkinter import ttk


class VentanaPrincipal:

    def __init__(self, root):
        self.root = root

        self.root.title("5 Métodos de Transporte")
        self.root.geometry("1000x650")
        self.root.minsize(800, 550)
        self.root.configure(bg="#F3F4F6")

        self.crear_interfaz()

    def crear_interfaz(self):

        titulo = tk.Label(
            self.root,
            text="SISTEMA DE TRANSPORTE",
            font=("Arial", 24, "bold"),
            bg="#F3F4F6",
            fg="#243B53"
        )
        titulo.pack(pady=(35, 5))

        subtitulo = tk.Label(
            self.root,
            text="Solución de problemas de transporte",
            font=("Arial", 12),
            bg="#F3F4F6",
            fg="#627D98"
        )
        subtitulo.pack(pady=5)

        contenedor = ttk.LabelFrame(
            self.root,
            text=" Selecciona un método "
        )
        contenedor.pack(padx=60, pady=35, fill="both", expand=True)

        metodos = [
            "Esquina Noroeste",
            "Costo Mínimo",
            "Método de Miguel",
            "Método del Banquillo",
            "DIMO"
        ]

        for metodo in metodos:
            boton = ttk.Button(
                contenedor,
                text=metodo,
                command=lambda nombre=metodo: self.seleccionar_metodo(nombre)
            )
            boton.pack(fill="x", padx=80, pady=10, ipady=8)

        self.resultado = tk.Label(
            self.root,
            text="Selecciona un método para comenzar",
            font=("Arial", 11),
            bg="#F3F4F6",
            fg="#243B53"
        )
        self.resultado.pack(pady=20)

    def seleccionar_metodo(self, metodo):
        self.resultado.config(
            text=f"Has seleccionado: {metodo}"
        )
