import ast
import tkinter as tk
from tkinter import ttk, messagebox
from src.servicio.simplex import simplex_revisado
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

iter = 0

class App:
    def __init__(self, root):
        self.costos = None
        self.recursos = None
        self.tecnologicos = None
        self.nobasica = None
        self.basica = None
        self.simplex_inicio = None
        self.optimo = None
        self.optimo_2 = None
        self.var_entra = None
        self.var_sale = None
        self.encabezados = None
        self.limites = None


        self.root = root
        self.root.title("Simplex Revisado")
        # Configurar el tamaño de la ventana
        self.root.geometry("750x600")

        # Crear el Notebook para gestionar pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Lista para mantener un registro de los frames de las pestañas
        self.frames = []

        style = ttk.Style()
        style.configure("TNotebook", font=("Arial", 12), background="lightblue")
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), background="lightgrey")
        style.configure("TFrame", background="lightyellow")

        # Frame de entrada de datos
        self.frame_datos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_datos, text="Entrada de Datos")

        # Etiquetas para vectores
        tk.Label(self.frame_datos, text="Coeficientes de Costos:", font=("Helvetic", 11, "bold")).grid(row=0, column=0, padx=10, pady=20,sticky='w')
        tk.Label(self.frame_datos, text="Variables No Basicas:", font=("Helvetic", 11, "bold")).grid(row=1,column=0,padx=10,pady=20, sticky='w')
        tk.Label(self.frame_datos, text="Variables Basicas:", font=("Helvetic", 11, "bold")).grid(row=2,column=0,padx=10,pady=20, sticky='w')
        tk.Label(self.frame_datos, text="Vector recursos:", font=("Helvetic", 11, "bold")).grid(row=3, column=0, padx=10, pady=20, sticky='w')
        tk.Label(root, text="Limites de gráfica:", font=("Helvetic", 11, "bold")).grid(row=1, column=0,padx=10, pady=20, sticky='e')

        # Entrada para vectores
        self.costos_entry = tk.Entry(self.frame_datos, width=50)
        self.costos_entry.grid(row=0, column=1, padx=10, pady=5)
        self.costos_entry.insert(0, "     (a, b, c)")
        self.costos_entry.bind("<FocusIn>", self.clear_costos_placeholder)
        self.costos_entry.bind("<FocusOut>", self.add_costos_placeholder)
        self.nobasica_entry = tk.Entry(self.frame_datos, width=50)
        self.nobasica_entry.grid(row=1, column=1, padx=10, pady=5)
        self.nobasica_entry.insert(0, "     (x1, x2, x3)")
        self.nobasica_entry.bind("<FocusIn>", self.clear_nobasica_placeholder)
        self.nobasica_entry.bind("<FocusOut>", self.add_nobasica_placeholder)
        self.basica_entry = tk.Entry(self.frame_datos, width=50)
        self.basica_entry.grid(row=2, column=1, padx=10, pady=5)
        self.basica_entry.insert(0, "     (s1, s2, s3)")
        self.basica_entry.bind("<FocusIn>", self.clear_basica_placeholder)
        self.basica_entry.bind("<FocusOut>", self.add_basica_placeholder)
        self.recursos_entry = tk.Entry(self.frame_datos, width=50)
        self.recursos_entry.grid(row=3, column=1, padx=10, pady=5)
        self.recursos_entry.insert(0, "     (a, b, c)")
        self.recursos_entry.bind("<FocusIn>", self.clear_recursos_placeholder)
        self.recursos_entry.bind("<FocusOut>", self.add_recursos_placeholder)
        self.limites_entry = tk.Entry(root, width=10)
        self.limites_entry.grid(row=1, column=1, padx=10, pady=5, sticky='e')
        self.limites_entry.insert(0, "(a, b)")
        self.limites_entry.bind("<FocusIn>", self.clear_limites_placeholder)
        self.limites_entry.bind("<FocusOut>", self.add_limites_placeholder)

        # Etiquetas para matrices
        tk.Label(self.frame_datos, text="Coeficientes Tecnológicos:", font=("Helvetic", 11, "bold")).grid(row=4, column=0, padx=10,pady=20, sticky='w')

        # Entrada para matrices (ajustar el ancho)
        self.tecnologicos_entry = tk.Entry(self.frame_datos, width=50)
        self.tecnologicos_entry.grid(row=4, column=1, padx=10, pady=5)
        self.tecnologicos_entry.insert(0, "   a, b, c; d, e, f; g, h, i;")
        self.tecnologicos_entry.bind("<FocusIn>", self.clear_tecnologicos_placeholder)
        self.tecnologicos_entry.bind("<FocusOut>", self.add_tecnologicos_placeholder)

        # botónes Notebook
        iterar_button = tk.Button(root, text="Iterar", font=("Helvetic", 11, "bold"), foreground="black", command=self.iterar)
        iterar_button.grid(row=2, column=1, padx=10, pady=10, sticky='e')
        grafica_button = tk.Button(root, text="Graficar", font=("Helvetic", 11, "bold"), foreground="black",command=self.graficar)
        grafica_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        sensibilidad_button = tk.Button(root, text="Sensibilidad", font=("Helvetic", 11, "bold"), foreground="black",command=self.sensibilidad)
        sensibilidad_button.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        reiniciar_button = tk.Button(root, text="Reiniciar", font=("Helvetic", 11, "bold"), foreground="black",command=self.reiniciar)
        reiniciar_button.grid(row=3, column=0, padx=10, pady=10, sticky='w')

    def clear_costos_placeholder(self, event):
        """Elimina el placeholder del vector cuando se hace foco en el Entry"""
        if self.costos_entry.get() == "     (a, b, c)":
            self.costos_entry.delete(0, tk.END)

    def add_costos_placeholder(self, event):
        """Agrega el placeholder del vector si el Entry está vacío al perder foco"""
        if self.costos_entry.get() == "":
            self.costos_entry.insert(0, "     (a, b, c)")

    def clear_nobasica_placeholder(self, event):
        """Elimina el placeholder del vector cuando se hace foco en el Entry"""
        if self.nobasica_entry.get() == "     (x1, x2, x3)":
            self.nobasica_entry.delete(0, tk.END)

    def add_nobasica_placeholder(self, event):
        """Agrega el placeholder del vector si el Entry está vacío al perder foco"""
        if self.nobasica_entry.get() == "":
            self.nobasica_entry.insert(0, "     (x1, x2, x3)")

    def clear_basica_placeholder(self, event):
        """Elimina el placeholder del vector cuando se hace foco en el Entry"""
        if self.basica_entry.get() == "     (s1, s2, s3)":
            self.basica_entry.delete(0, tk.END)

    def add_basica_placeholder(self, event):
        """Agrega el placeholder del vector si el Entry está vacío al perder foco"""
        if self.basica_entry.get() == "":
            self.basica_entry.insert(0, "     (s1, s2, s3)")

    def clear_recursos_placeholder(self, event):
        """Elimina el placeholder del vector cuando se hace foco en el Entry"""
        if self.recursos_entry.get() == "     (a, b, c)":
            self.recursos_entry.delete(0, tk.END)

    def add_recursos_placeholder(self, event):
        """Agrega el placeholder del vector si el Entry está vacío al perder foco"""
        if self.recursos_entry.get() == "":
            self.recursos_entry.insert(0, "     (a, b, c)")

    def clear_tecnologicos_placeholder(self, event):
        """Elimina el placeholder del vector cuando se hace foco en el Entry"""
        if self.tecnologicos_entry.get() == "   a, b, c; d, e, f; g, h, i;":
            self.tecnologicos_entry.delete(0, tk.END)

    def add_tecnologicos_placeholder(self, event):
        """Agrega el placeholder del vector si el Entry está vacío al perder foco"""
        if self.tecnologicos_entry.get() == "":
            self.tecnologicos_entry.insert(0, "   a, b, c; d, e, f; g, h, i;")

    def clear_limites_placeholder(self, event):
        """Elimina el placeholder del vector cuando se hace foco en el Entry"""
        if self.limites_entry.get() == "(a, b)":
            self.limites_entry.delete(0, tk.END)

    def add_limites_placeholder(self, event):
        """Agrega el placeholder del vector si el Entry está vacío al perder foco"""
        if self.limites_entry.get() == "":
            self.limites_entry.insert(0, "(a, b)")

    def reiniciar(self):
        global iter
        iter = 0
        self.optimo = None
        self.optimo_2 = None
        self.simplex_inicio = None
        self.var_entrada = None
        self.var_sale = None
        self.costos_entry.delete(0, tk.END)
        self.nobasica_entry.delete(0, tk.END)
        self.basica_entry.delete(0, tk.END)
        self.recursos_entry.delete(0, tk.END)
        self.tecnologicos_entry.delete(0, tk.END)
        self.limites_entry.delete(0, tk.END)
        # Cerrar todas las pestañas
        for frame in self.frames:
            self.notebook.forget(frame)  # Olvidar la pestaña
            frame.destroy()  # Destruir el Frame
        # Limpiar la lista de frames
        self.frames.clear()

    def graficar(self):
        try:
            if  self.optimo is None:
                messagebox.showerror("Error", "Al final de iterar se calcula la grafica ")
                return
            if  self.optimo_2 is None:
                messagebox.showerror("Error", "Al final de iterar se calcula la grafica ")
                return
            if not self.validar_variables():
                messagebox.showerror("Error", "El problema tiene más de 2 variables")
                return
            limites = self.obtener_limites()
            if not limites:
                messagebox.showerror("Error", "Debe ingresar límites válidos en el formato correcto")
                return
            self.limites = limites
            self.agregar_plot()

        except (TypeError, ValueError) as e:
            messagebox.showerror("Error", f"Error : {str(e)}")

    def validar_variables(self):
        return 2 >= len(self.tecnologicos[0]) > 0

    def obtener_limites(self):
        try:
            limites_texto = self.limites_entry.get().strip()
            limites = ast.literal_eval(limites_texto)
            if self.es_tupla(limites):
                return limites
        except (ValueError, SyntaxError):
            return None
        return None

    def agregar_plot(self):
        # Crear un Frame que contendrá el gráfico
        frame_grafica = ttk.Frame(self.notebook, width=600, height=400)
        self.notebook.add(frame_grafica, text=f"Gráfica")
        frame_grafica.pack_propagate(False)  # Evitar que el tamaño del frame dependa del contenido
        # Agregar el nuevo Frame a la lista
        self.frames.append(frame_grafica)
        # Obtener la figura con el gráfico
        fig = self.simplex_inicio.crear_grafica(self.limites)
        # Añadir la figura a un Canvas en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def iterar(self):
        global iter
        if  iter == 0:
            try:
                self.costos = self.costos_entry.get().strip()  # Elimina espacios alrededor
                self.costos = self.leer_vector(self.costos)
                if self.es_vector(self.costos):
                    self.costos = np.array(self.costos)
                else:
                    messagebox.showerror("Error", "No se ha ingresado un vector costos.")
                    return
                self.nobasica = self.nobasica_entry.get().strip()  # Elimina espacios alrededor
                self.nobasica = self.leer_vector_letra(self.nobasica)
                if self.es_vector_letras(self.nobasica):
                    self.nobasica = self.convertir_a_numpy(self.nobasica)
                else:
                    messagebox.showerror("Error", "No se ha ingresado un vector nobasica valido.")
                    return
                self.basica = self.basica_entry.get().strip()  # Elimina espacios alrededor
                self.basica = self.leer_vector_letra(self.basica)
                if self.es_vector_letras(self.basica):
                    self.basica = self.convertir_a_numpy(self.basica)
                else:
                    messagebox.showerror("Error", "No se ha ingresado un vector basica válido.")
                    return
                self.recursos = self.recursos_entry.get().strip()  # Elimina espacios alrededor
                self.recursos = self.leer_vector(self.recursos)
                if  self.es_vector(self.recursos):
                    self.recursos = np.array(self.recursos)
                else:
                    messagebox.showerror("Error", "No se ha ingresado un vector recursos.")
                    return
                self.tecnologicos = self.tecnologicos_entry.get().strip()  # Elimina espacios alrededor
                filas = self.tecnologicos.split(';')  # Divide las filas por el delimitador ';'
                self.tecnologicos = [list(map(float, fila.split(','))) for fila in filas]  # Convierte cada fila a una lista de floats
                if self.es_matriz(self.tecnologicos):
                    self.tecnologicos = np.array(self.tecnologicos)
                else:
                    messagebox.showerror("Error", "No se ha ingresado una matriz valida.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Asegúrate de ingresar datos en el formato correcto.")

            A, b, c, X, Xs = self.tecnologicos, self.recursos, self.costos, self.nobasica, self.basica
            self.simplex_inicio = simplex_revisado( A, b, c, X, Xs)
            self.var_entra, self.var_sale, self.optimo, self.optimo_2, matriz = self.simplex_inicio.simplex()
            self.abrir_pestana(matriz)
            iter += 1
        else:
            try:
                if (self.optimo < 0).any() or (self.optimo_2 < 0).any():
                    self.var_entra, self.var_sale, self.optimo, self.optimo_2, matriz = self.simplex_inicio.simplex()
                    self.abrir_pestana(matriz)
                    iter += 1
                else:
                    messagebox.showerror("Error", "Se alcanzo la solución optima.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Se alcanzo la solución optima.")

    def abrir_pestana(self, matriz):
        # Crear un nuevo Frame para los resultados
        frame_iteracion = ttk.Frame(self.notebook)
        # Agregar el nuevo Frame a la lista
        self.frames.append(frame_iteracion)
        # Crear una nueva pestaña en el notebook
        self.notebook.add(frame_iteracion, text=f"Iter: {iter}")
        if (self.optimo < 0).any() or (self.optimo_2 < 0).any():
            tk.Label(frame_iteracion, text="Variable que sale:", font=("Helvetic", 11, "bold")).grid(row=2, column=0,padx=10, pady=10,sticky='w')
            tk.Label(frame_iteracion, text="Variables que entra:", font=("Helvetic", 11, "bold")).grid(row=1, column=0,padx=10, pady=10,sticky='w')
            info_label = tk.Label(frame_iteracion, text=f"{self.var_entra}", font=("Helvetica", 11, "bold"))
            info_label.grid(row=1, column=1, padx=10, pady=10, sticky='w')
            info_label = tk.Label(frame_iteracion, text=f"{self.var_sale}", font=("Helvetica", 11, "bold"))
            info_label.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        # Crear el Treeview con el número correcto de columnas
        columnas = [f"{i}" for i in range(len(matriz[0]))]  # m columnas
        tree = ttk.Treeview(frame_iteracion, columns=columnas, show="headings")
        # Configurar encabezados
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=20, anchor=tk.CENTER)
            # Insertar filas de la matriz en el Treeview
        for fila in matriz:
            tree.insert("", tk.END, values=fila)
        # Colocar el Treeview utilizando grid
        tree.grid(row=0, column=0, columnspan=2, sticky="nsew")
        # Configurar expansión del Treeview para ocupar espacio adicional
        frame_iteracion.grid_rowconfigure(3, weight=1)
        frame_iteracion.grid_columnconfigure(0, weight=1)
        frame_iteracion.grid_columnconfigure(1, weight=1)
        # Seleccionar la nueva pestaña
        self.notebook.select(frame_iteracion)  # Activa la nueva pestaña

    def sensibilidad(self):
        try:
            if (self.optimo >= 0).all() and (self.optimo_2 >= 0).all():
                # Crear un Frame que contendrá el gráfico
                frame_sensibilidad = ttk.Frame(self.notebook, width=600, height=400)
                self.notebook.add(frame_sensibilidad, text=f"Sensibilidad")
                # Agregar el nuevo Frame a la lista
                self.frames.append(frame_sensibilidad)
                lista_texto = self.simplex_inicio.tabla_sensibilidad()
                # Crear un widget Text en el frame
                text_widget = tk.Text(frame_sensibilidad, wrap="word", height=10, width=50)
                text_widget.pack(fill="both", expand=True, pady=10, padx=10)
                # Agregar cada elemento de la lista en el Text
                for linea in lista_texto:
                    text_widget.insert("end", linea + "\n")
                # Hacer que el Text sea de solo lectura
                text_widget.config(state="disabled")
            else:
                messagebox.showerror("Error", "Al final de iterar se calcula la sensibilidad ")
                return
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Al final de iterar se calcula la sensibilidad")

    def leer_vector(self, vector):
        vector = vector.replace('(', '').replace(')', '')  # Elimina los paréntesis
        vector = list(map(float, vector.split(',')))  # Divide por comas y convierte a float
        return vector

    def leer_vector_letra(self, cadena):
        cadena = cadena.strip("()")
        return [letra.strip() for letra in cadena.split(",")]

    def es_vector_letras(self, objeto):
        return isinstance(objeto, list) and all(isinstance(i, str) for i in objeto)

    def es_vector(self, objeto):
        return isinstance(objeto, list) and all(isinstance(i, (int, float)) for i in objeto) and all(not isinstance(i, list) for i in objeto)

    def es_matriz(self, objeto):
        if isinstance(objeto, list) and all(isinstance(i, list) for i in objeto):
            longitud_filas = len(objeto[0])
            return all(len(fila) == longitud_filas and all(isinstance(elem, (int, float)) for elem in fila) for fila in objeto)
        return False

    def es_tupla(self, objeto):
        if isinstance(objeto, tuple) and len(objeto) == 2:
            return True
        else:
            return False

    def convertir_a_numpy(self, vector_letras):
        return np.array(vector_letras, dtype=str)