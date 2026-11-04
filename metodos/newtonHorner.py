import numpy as np

from metodos.base import MetodoBase, ErrorMetodo, poli_texto, horner
from metodos.horner import CAMPO_COEFS


def newton_horner(coefs, x0, tol=1e-8, max_iter=100, callback=None):
    """Newton sobre un polinomio evaluando P y P′ con Horner.
    Devuelve (x, iteraciones, error, convergio)."""
    xk, err = x0, float("inf")
    for n in range(1, max_iter + 1):
        b = horner(coefs, xk)
        p = b[-1]
        dp = horner(b[:-1], xk)[-1] if len(b) > 1 else 0.0
        if dp == 0:
            if p == 0:
                return xk, n, 0.0, True
            raise ErrorMetodo(f"P′(x) = 0 en x = {xk}; prueba otro valor inicial.")
        x_nuevo = xk - p / dp
        err = abs(x_nuevo - xk)
        if callback:
            callback(n, xk, p, dp, x_nuevo, err)
        xk = x_nuevo
        if err < tol:
            return xk, n, err, True
    return xk, max_iter, err, False


class NewtonHorner(MetodoBase):
    DESCRIPCION = "Newton-Raphson para polinomios: P(xₖ) y P′(xₖ) se calculan con división sintética."
    CAMPOS = [
        CAMPO_COEFS,
        {"clave": "x0", "etiqueta": "x₀", "ejemplo": "-2"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-8"},
        {"clave": "max", "etiqueta": "Iteraciones máx.", "ejemplo": "50"},
    ]
    COLUMNAS = ["k", "xₖ", "P(xₖ)", "P′(xₖ)", "xₖ₊₁", "|xₖ₊₁ − xₖ|"]
    TITULO_GRAFICA = "Newton-Horner"

    def ejecutar(self):
        coefs = self.coeficientes()
        x0 = self.numero("x0")
        tol = self.numero("tol", 1e-6)
        n_max = self.entero("max", 100)
        puntos = [x0]

        def registro(*fila):
            self.agregar_fila(*fila)
            puntos.append(fila[4])

        r, n, err, ok = newton_horner(coefs, x0, tol, n_max, registro)
        self.resultado_raiz(r, n, err, ok, f"P(x) = {poli_texto(coefs)}")
        self.graficar(lambda t: np.polyval(coefs, t), puntos, puntos_x=puntos,
                      raiz=r, etiqueta_curva="P(x)")
