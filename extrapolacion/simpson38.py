from metodos.base import MetodoBase, ErrorMetodo, fmt
from extrapolacion.simpson13 import CAMPOS_INTEGRAL, leer_intervalo


class Simpson38(MetodoBase):
    DESCRIPCION = ("Simpson 3/8 compuesto: ∫ f ≈ (3h/8)[f₀ + 3f₁ + 3f₂ + 2f₃ + … + fₙ], "
                   "h = (b − a)/n con n múltiplo de 3. Con n = 3 es la regla simple.")
    CAMPOS = CAMPOS_INTEGRAL + [
        {"clave": "n", "etiqueta": "Subintervalos n (múltiplo de 3)", "ejemplo": "3"}]
    COLUMNAS = ["i", "xᵢ", "f(xᵢ)", "Coeficiente", "Coef · f(xᵢ)"]
    TITULO_GRAFICA = "Simpson 3/8"

    def ejecutar(self):
        expr, f, a, b = leer_intervalo(self)
        n = self.entero("n", 3, minimo=3)
        if n % 3:
            raise ErrorMetodo("Para Simpson 3/8, n debe ser múltiplo de 3.")
        h = (b - a) / n
        suma, nodos = 0.0, []
        for i in range(n + 1):
            xi = a + i * h
            c = 1 if i in (0, n) else (2 if i % 3 == 0 else 3)
            fx = f(xi)
            suma += c * fx
            nodos.append(xi)
            self.agregar_fila(i, xi, fx, c, c * fx)
        aprox = 3 * h / 8 * suma
        self.terminar_integral(expr, f, a, b, aprox, nodos,
                               lineas=[f"h = {fmt(h)} · Σ = {fmt(suma)}"])
