import numpy as np
import sympy as sp
from matplotlib import pyplot as plt


class simplex_revisado:
    def __init__(self, A, b, c, X, Xs):
        self.A = A
        self.b = b
        self.c = c
        self.X = X
        self.Xs = Xs
        self.B = None
        self.CB = None
        self.z_init = 1
        self.CB_init = None
        self.z = None
        self.m = None
        self.iter = 0
        self.map_A = None
        self.map_B = None
        self.map_c = None
        self.map_CB = None
        self.optimo = None
        self.optimo_2 = None
        self.var_entra = None
        self.var_sale = None
        self.var_entra_lugar = None
        self.var_sale_lugar = None
        self.arreglo_z = ["z"]
        self.arreglo_map_A = None
        self.arreglo_fin = ["="]
        self.B_inv = None

    def asociar_variables_matriz(self, matriz, variables):
        num_columnas = len(matriz[0])
        if len(variables) != num_columnas:
            raise ValueError("El número de variables no coincide con el número de columnas en la matriz.")
        column_map = {variables[i]: i for i in range(num_columnas)}
        return column_map

    def asociar_variables_vector(self, vector_fila, variables):
        if len(vector_fila) != len(variables):
            raise ValueError("Los vectores deben tener la misma longitud")
        map_fila = {variables[i]: i for i in range(len(vector_fila))}
        return map_fila

    def obtener_clave_por_valor(self, dict, valor_buscado):
        for clave, valor in dict.items():
            if valor == valor_buscado:
                return clave
        return None  # Retorna None si no se encuentra la clave asociada al valor

    def intercambiar_matrices_diccionarios(self, entra, sale):
        # Obtener los índices de las columnas a intercambiar
        clave2 = self.obtener_clave_por_valor(self.map_B, sale)
        clave1 = self.obtener_clave_por_valor(self.map_A, entra)
        # Verificar que las matrices tienen el mismo número de filas
        if self.A.shape[0] != self.B.shape[0]:
            raise ValueError("Las matrices deben tener el mismo número de filas para intercambiar columnas.")
        # Obtener la columna a intercambiar de matriz1 y la columna de matriz2
        columna_matriz1 = self.A[:, entra]
        # Intercambiar las columnas entre las matrices
        self.B[:, sale] = np.copy(columna_matriz1)
        # Intercambiar las claves y valores directamente en los diccionarios originales
        self.map_B.pop(clave2)
        # Añadir las claves intercambiadas con los nuevos valores
        self.map_B[clave1] = sale

    def intercambiar_vectores_diccionarios(self, entra, sale):
        # Obtener los índices de los elementos a intercambiar
        clave2 = self.obtener_clave_por_valor(self.map_CB, sale)
        clave1 = self.obtener_clave_por_valor(self.map_c, entra)
        # Intercambiar los elementos entre los vectores
        self.CB[sale] = np.copy(self.c[entra])
        # Intercambiar las claves y valores directamente en los diccionarios originales
        self.map_CB.pop(clave2)
        # Añadir las claves intercambiadas con los nuevos índices
        self.map_CB[clave1] = sale

    def encabezados(self):
        diccionario_ordenado = dict(sorted(self.map_B.items(), key=lambda x: x[1]))
        arreglo_map_B = list(diccionario_ordenado.keys())
        arreglo_unido = self.arreglo_z + self.arreglo_map_A + arreglo_map_B + self.arreglo_fin
        arreglo_final = []
        for elemento in arreglo_unido:
            elemento = str(elemento)
            arreglo_final.append(elemento)
        return arreglo_final

    def tabla_organizada(self, arreglo, pos_1, pos_2, pos_3, pos_4, pos_5, pos_6, pos_7, pos_8):
        pos_1 = np.array([pos_1])
        pos_4 = np.array([pos_4])
        matriz = []
        # Primera fila: número 'a' + vector_n + vector_m + número 'b'
        primera_fila = np.concatenate([pos_1, pos_2, pos_3, pos_4])
        matriz.append(primera_fila)
        # Recorremos las filas de las matrices y combinamos los elementos
        for i in range(len(pos_6)):
            fila_combinada = ([pos_5[i]]) + pos_6[i].tolist() + pos_7[i].tolist() + [pos_8[i]]
            matriz.append(fila_combinada)
        matriz_final = np.char.mod('%.2f', matriz)
        matriz_lista = matriz_final.tolist()
        matriz_lista.insert(0 , arreglo)
        return matriz_lista


    def tablatura(self):
        B_inv = np.linalg.inv(self.B)  # Inversa de la matriz base
        self.B_inv = B_inv
        CB = self.CB
        self.optimo = ((CB @ B_inv) @ self.A) - self.c
        self.optimo_2 = CB @ B_inv
        p_uno = self.z_init
        p_dos = ((CB @ B_inv) @ self.A) - self.c
        p_tres = CB @ B_inv
        p_cuatro = (CB @ B_inv) @ self.b
        p_cinco = self.CB_init
        p_seis = B_inv @ self.A
        p_siete = B_inv
        p_ocho = B_inv @ self.b
        # Variable que entra:
        self.var_entra_lugar = np.argmin(p_dos)
        self.var_entra = self.obtener_clave_por_valor(self.map_A, self.var_entra_lugar)
        # var_entrante = p_dos[self.var_entra_lugar]
        # Variable que sale:
        razones = []
        for i in range(self.m):
            if self.A[i, self.var_entra_lugar] > 0:  # Solo consideramos coeficientes positivos
                razon = p_ocho[i] / self.A[i, self.var_entra_lugar]
                razones.append((razon, i))
        try:
            if razones:
                var_salida = min(razones, key=lambda x: x[0])
                self.var_sale_lugar = var_salida[1]
        except ValueError:
            print("No hay variables que salgan.")
        self.var_sale = self.obtener_clave_por_valor(self.map_B, self.var_sale_lugar)
        return p_uno, p_dos, p_tres, p_cuatro, p_cinco, p_seis, p_siete, p_ocho, self.var_entra, self.var_sale, self.optimo, self.optimo_2

    def simplex(self):
        if self.iter == 0:
            try:
                self.m = self.A.shape[0]  # Dimensiones de la matriz
                self.B = np.eye(self.m)  # Base inicial
                self.CB_init = np.zeros(self.m)
                self.CB = np.zeros(self.m)  # Costos de variables básicas
                B_inv = np.linalg.inv(self.B)  # Inversa de la matriz base
                self.map_A = self.asociar_variables_matriz(self.A, self.X)
                self.map_B = self.asociar_variables_matriz(self.B, self.Xs)
                self.map_c = self.asociar_variables_vector(self.c, self.X)
                self.map_CB = self.asociar_variables_vector(self.CB, self.Xs)
                self.arreglo_map_A = list(self.map_A.keys())
                p_uno, p_dos, p_tres, p_cuatro, p_cinco, p_seis, p_siete, p_ocho, self.var_entra, self.var_sale, self.optimo, self.optimo_2 = self.tablatura()
                arreglo_final = self.encabezados()
                matriz_final = self.tabla_organizada(arreglo_final, p_uno, p_dos, p_tres, p_cuatro, p_cinco, p_seis, p_siete, p_ocho)
                self.iter = + 1
                return self.var_entra, self.var_sale, self.optimo, self.optimo_2, matriz_final
            except ValueError:
                print("Error ejecucion inicial")

        if self.iter != 0 and ((self.optimo < 0).any() or (self.optimo_2 < 0).any()):
            try:
                self.intercambiar_matrices_diccionarios(self.var_entra_lugar, self.var_sale_lugar)
                self.intercambiar_vectores_diccionarios(self.var_entra_lugar, self.var_sale_lugar)
                p_uno, p_dos, p_tres, p_cuatro, p_cinco, p_seis, p_siete, p_ocho, self.var_entra, self.var_sale, self.optimo, self.optimo_2 = self.tablatura()
                arreglo_final = self.encabezados()
                matriz_final = self.tabla_organizada(arreglo_final, p_uno, p_dos, p_tres, p_cuatro, p_cinco, p_seis, p_siete, p_ocho)
                self.iter = + 1
                return self.var_entra, self.var_sale, self.optimo, self.optimo_2, matriz_final
            except ValueError:
                print("Ya se encontro la solución optima.")

    def crear_grafica(self, limites):
        b_columna = self.b[:, np.newaxis]
        restricciones = np.hstack((self.A, b_columna))
        # Crear la figura y el eje
        fig, ax = plt.subplots(figsize=(7, 7))
        # Crear el rango para la variable X1
        x1_vals = np.linspace(limites[0], limites[1], 400)
        # Crear una malla para X1 y X2
        x1, x2 = np.meshgrid(np.linspace(limites[0], limites[1], 400),
                             np.linspace(limites[0], limites[1], 400))
        # Inicializar un array para la región factible
        factible = np.ones_like(x1, dtype=bool)
        # Definir colores diferentes para cada ecuación
        colores = ['r', 'g', 'b', 'y', 'm', 'c']
        # Evaluar cada restricción
        for i, restriccion in enumerate(restricciones):
            a1, a2, b = restriccion
            color = colores[i % len(colores)]
            if a2 != 0:
                # Graficar restricción en términos de X2
                x2_restriccion = (b - a1 * x1_vals) / a2
                x2_clipped = np.clip(x2_restriccion, limites[0], limites[1])
                ax.plot(x1_vals, x2_clipped, label=f"Restricción {i + 1}: {a1}X1 + {a2}X2 = {b}", color=color)
                # Evaluar la región factible para la restricción
                factible &= (a1 * x1 + a2 * x2 <= b)
            elif a1 != 0:
                # Graficar restricción vertical cuando a2 = 0
                x1_const = b / a1
                if limites[0] <= x1_const <= limites[1]:  # Verificar si está dentro de los límites
                    ax.axvline(x=x1_const, color=color, label=f"Restricción {i + 1}: X1 = {x1_const}")
                    # Evaluar la región factible para la restricción
                    factible &= (x1 <= x1_const)
        # Graficar la región factible
        ax.contourf(x1, x2, factible, levels=[0.5, 1], colors=['#d3d3d3'], alpha=0.5)
        # Etiquetas y título
        ax.set_xlim(limites)
        ax.set_ylim(limites)
        ax.set_xlabel("X1")
        ax.set_ylabel("X2")
        ax.set_title("Gráfico de Restricciones con Región Factible")
        ax.legend()
        ax.grid(True)
        return fig

    def sensibilidad_recursos(self):
        D = sp.symbols('D')
        B_inv = sp.Matrix(self.B_inv)
        b = sp.Matrix(self.b)
        intervalos_factible = []
        intervalos_sensible = []
        for i in range(len(b)):
            # Crear una copia de b y modificarla
            b_modif = b.copy()
            b_modif[i, 0] = D + b_modif[i, 0]
            # Calcular sombra
            sombra = B_inv * b_modif  # Multiplicamos B_inv por el vector columna modificado
            # Resolver la desigualdad sombra[j] >= 0 para cada elemento
            soluciones = []
            for j in range(sombra.shape[0]):  # Iterar sobre cada fila de la matriz sombra
                expr = sombra[j]  # Obtener la expresión de la sombra
                sol = sp.solve_univariate_inequality(expr >= 0, D, relational=False)  # Resolver la desigualdad
                soluciones.append(sol)
            # Determinar límites del rango común
            lower_bound = -sp.oo
            upper_bound = sp.oo
            for sol in soluciones:
                if sol.inf is not None:  # Verifica si tiene límite inferior
                    lower_bound = max(lower_bound, sol.inf)
                if sol.sup is not None:  # Verifica si tiene límite superior
                    upper_bound = min(upper_bound, sol.sup)
            intervalos_factible.append(
                f"Intervalo para permanecer factible para b[{i}]: [{lower_bound}, {upper_bound}]")
            # Mostrar el rango de sensibilidad
            inferior = lower_bound + b[i, 0]
            superior = upper_bound + b[i, 0]
            # Verificar si el valor es infinito
            if sp.oo == inferior and sp.oo == superior:
                intervalos_sensible.append(f"Intervalo sensibilidad para b[{i}]: [ {inferior}, {superior} ]")
            elif sp.oo != inferior and sp.oo != superior:
                intervalos_sensible.append(f"Intervalo sensibilidad para b[{i}]: [ {inferior:.2f}, {superior:.2f} ]")
            elif sp.oo == inferior and sp.oo != superior:
                intervalos_sensible.append(f"Intervalo sensibilidad para b[{i}]: [ {inferior}, {superior:.2f} ]")
            elif sp.oo != inferior and sp.oo == superior:
                intervalos_sensible.append(f"Intervalo sensibilidad para b[{i}]: [ {inferior:.2f}, {superior} ]")
        return intervalos_sensible

    def sensibilidad_objetivo(self):
        C = sp.symbols('C')
        A = sp.Matrix(self.A)
        B_inv = sp.Matrix(self.B_inv)
        CB = sp.Matrix([self.CB])
        c = sp.Matrix([self.c])
        ajuste = CB * B_inv
        inter = []
        for i in range(len(c)):
            A_colunm = A[:, i]
            sombra = ajuste * A_colunm
            valor = sombra[0]
            expr = valor - C
            sol = sp.solve_univariate_inequality(expr >= 0, C, relational=False)  # Resolver la desigualdad
            inter.append(sol)
        intervalos_sensible = []
        for i in range(len(inter)):
            inferior = inter[i].start
            superior = inter[i].end
            # Verificar si el valor es infinito
            if -sp.oo == inferior and sp.oo == superior:
                intervalos_sensible.append(f"Intervalo sensibilidad para c[{i}]: [ {inferior}, {superior} ]")
            elif -sp.oo != inferior and sp.oo != superior:
                intervalos_sensible.append(f"Intervalo sensibilidad para c[{i}]: [ {inferior:.2f}, {superior:.2f} ]")
            elif -sp.oo == inferior and sp.oo != superior:
                intervalos_sensible.append(f"Intervalo sensibilidad para c[{i}]: [ {inferior} , {superior:.2f} ]")
            elif -sp.oo != inferior and sp.oo == superior:
                intervalos_sensible.append(f"Intervalo sensibilidad para c[{i}]: [ {inferior:.2f}, {superior} ]")
        return intervalos_sensible

    def tabla_sensibilidad(self):
        tabla = []
        tabla.append(f"Intervalos de sensibilidad para recursos (b): ")
        tabla.append(f"                                               ")
        sensible_recursos = self.sensibilidad_recursos()
        for elemento in sensible_recursos:
            elemento = str(elemento)
            tabla.append(elemento)
        tabla.append(f"                                               ")
        tabla.append(f"Intervalos de sensibilidad para función objetivo (c): ")
        tabla.append(f"                                               ")
        dict_cb = self.map_CB
        dict_str = {str(key): value for key, value in dict_cb.items()}
        tabla.append(str(dict_str))
        sensible_objetivo = self.sensibilidad_objetivo()
        for elemento in sensible_objetivo:
            elemento = str(elemento)
            tabla.append(elemento)
        return tabla
