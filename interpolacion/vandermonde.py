import numpy as np
import sympy as sp

from metodos.base import MetodoBase, CAMPOS_INTERPOLACION, fmt, sub, x


class Vandermonde(MetodoBase):
    DESCRIPCION = ("Resuelve el sistema V·a = f, con Vᵢⱼ = xᵢʲ, para obtener los coeficientes "
                   "del polinomio interpolante en la base 1, x, x², …")
    CAMPOS = CAMPOS_INTERPOLACION
    COLUMNAS = ["i", "xᵢ", "f(xᵢ)", "aᵢ (coef. de xⁱ)"]
    TITULO_GRAFICA = "Vandermonde"

    def ejecutar(self):
        xs, ys, _, f, xe = self.datos_interpolacion()
        V = np.vander(xs, increasing=True)
        a = np.linalg.solve(V, ys)
        for i in range(len(xs)):
            self.agregar_fila(i, xs[i], ys[i], f"a{sub(i)} = {fmt(a[i])}")
        poli = sum(sp.Float(float(ai)) * x ** i for i, ai in enumerate(a))
        self.terminar_interpolacion(
            poli, xs, f, xe,
            lineas=[f"Número de condición de V: {fmt(np.linalg.cond(V), 4)}"
                    "  (si es muy grande, los coeficientes pierden precisión)"])
