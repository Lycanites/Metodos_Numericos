import sympy as sp

from metodos.base import (MetodoBase, CAMPOS_INTERPOLACION, poli_texto, sub, x)

class lagrange(MetodoBase):
    DESCRIPCION = "Pₙ(x) = Σ f(xₖ)·Lₙ,ₖ(x),   con Lₙ,ₖ(x) = Π (x − xᵢ)/(xₖ − xᵢ) para i ≠ k."
    CAMPOS = CAMPOS_INTERPOLACION
    COLUMNAS = ["k", "xₖ", "f(xₖ)", "Lₙ,ₖ(x)", "Lₙ,ₖ(x*)"]
    TITULO_GRAFICA = "lagrange"

    def ejecutar(self):
        xs, ys, _, f, xe = self.datos_interpolacion()
        n = len(xs) - 1
        poli = 0
        for k in range(n + 1):
            L = sp.Integer(1)
            for i in range(n + 1):
                if i != k:
                    L *= (x - xs[i]) / (xs[k] - xs[i])
            L = sp.expand(L)
            poli += ys[k] * L
            coefs = [float(c) for c in sp.Poly(L, x).all_coeffs()]
            valor = float(L.subs(x, xe)) if xe is not None else None
            self.agregar_fila(k, xs[k], ys[k], poli_texto(coefs), valor)
        self.terminar_interpolacion(poli, xs, f, xe,
                                    lineas=[f"Grado del polinomio: ≤ {n}  (P{sub(n)})"])
