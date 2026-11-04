import numpy as np

from metodos.base import MetodoBase, fmt, poli_texto, horner

CAMPO_COEFS = {"clave": "coefs", "etiqueta": "Coeficientes de P(x)", "ancho": True,
               "ejemplo": "2, 0, -3, 3, -4",
               "ayuda": "Del grado mayor al término independiente, separados por comas.\n"
                        "Incluye ceros: 2x⁴ − 3x² + 3x − 4 → 2, 0, -3, 3, -4"}


class Horner(MetodoBase):
    DESCRIPCION = ("División sintética: evalúa P(x₀) y P′(x₀) y obtiene el cociente Q(x) "
                   "con P(x) = (x − x₀)·Q(x) + b₀.")
    CAMPOS = [CAMPO_COEFS, {"clave": "x0", "etiqueta": "x₀", "ejemplo": "-2"}]
    COLUMNAS = ["k", "aₖ", "bₖ₊₁·x₀", "bₖ", "Q: cₖ"]
    TITULO_GRAFICA = "Horner"

    def ejecutar(self):
        coefs = self.coeficientes()
        x0 = self.numero("x0")
        b = horner(coefs, x0)
        q = b[:-1]
        c = horner(q, x0)
        n = len(coefs) - 1
        for i, a in enumerate(coefs):
            prod = None if i == 0 else b[i - 1] * x0
            ck = c[i] if i < len(c) else None
            self.agregar_fila(n - i, a, prod, b[i], ck)

        self.mostrar_resultado(
            f"P(x) = {poli_texto(coefs)}\n"
            f"P({fmt(x0)}) = b₀ = {fmt(b[-1])}   ·   P′({fmt(x0)}) = Q({fmt(x0)}) = {fmt(c[-1])}\n"
            f"Q(x) = {poli_texto(q)}")
        self.graficar(lambda t: np.polyval(coefs, t), [x0 - 2, x0 + 2],
                      etiqueta_curva="P(x)", raiz=x0,
                      etiqueta_raiz=f"P({fmt(x0, 4)}) = {fmt(b[-1], 4)}")
