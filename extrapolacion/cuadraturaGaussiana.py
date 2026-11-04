import numpy as np

from metodos.base import MetodoBase, ErrorMetodo, fmt
from extrapolacion.simpson13 import CAMPOS_INTEGRAL, leer_intervalo


class CuadraturaGaussiana(MetodoBase):
    DESCRIPCION = ("Gauss-Legendre: ∫₋₁¹ f ≈ Σ cᵢ·f(tᵢ), con tᵢ raíces del polinomio de "
                   "Legendre Pₙ. Para [a, b] se usa x = [(b − a)t + (a + b)]/2. "
                   "Es exacta para polinomios de grado ≤ 2n − 1.")
    CAMPOS = CAMPOS_INTEGRAL + [
        {"clave": "n", "etiqueta": "Puntos n", "ejemplo": "3", "ayuda": "Entre 1 y 50"}]
    COLUMNAS = ["i", "tᵢ", "cᵢ", "xᵢ", "f(xᵢ)", "cᵢ · f(xᵢ)"]
    TITULO_GRAFICA = "Cuadratura gaussiana"

    def ejecutar(self):
        expr, f, a, b = leer_intervalo(self)
        n = self.entero("n", 3)
        if n > 50:
            raise ErrorMetodo("Usa a lo más 50 puntos.")
        t, c = np.polynomial.legendre.leggauss(n)
        suma, nodos = 0.0, []
        for i in range(n):
            xi = ((b - a) * t[i] + (a + b)) / 2
            fx = f(xi)
            suma += c[i] * fx
            nodos.append(xi)
            self.agregar_fila(i + 1, t[i], c[i], xi, fx, c[i] * fx)
        aprox = (b - a) / 2 * suma
        self.terminar_integral(expr, f, a, b, aprox, nodos,
                               lineas=[f"Factor (b − a)/2 = {fmt((b - a) / 2)} · Σ = {fmt(suma)}"])
