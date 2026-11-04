import cmath

import numpy as np
import sympy as sp

from metodos.base import MetodoBase, ErrorMetodo, fmt, x


class Muller(MetodoBase):
    DESCRIPCION = ("Ajusta una parábola por x₀, x₁, x₂ y toma su raíz más cercana a x₂. "
                   "Puede encontrar raíces complejas.")
    CAMPOS = [
        {"clave": "f", "etiqueta": "f(x)", "ejemplo": "x^4 - 3x^3 + x^2 + x + 1", "ancho": True},
        {"clave": "x0", "etiqueta": "x₀", "ejemplo": "0.5"},
        {"clave": "x1", "etiqueta": "x₁", "ejemplo": "-0.5"},
        {"clave": "x2", "etiqueta": "x₂", "ejemplo": "0"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-8"},
        {"clave": "max", "etiqueta": "Iteraciones máx.", "ejemplo": "50"},
    ]
    COLUMNAS = ["n", "x₀", "x₁", "x₂", "x₃", "f(x₃)", "|h|"]
    TITULO_GRAFICA = "Müller"

    def ejecutar(self):
        expr, f_real = self.funcion("f")
        f_np = sp.lambdify(x, expr, "numpy")

        def f(z):
            with np.errstate(all="ignore"):
                y = complex(f_np(complex(z)))
            if not (np.isfinite(y.real) and np.isfinite(y.imag)):
                raise ErrorMetodo(f"f({fmt(z)}) no está definida.")
            return y

        x0, x1, x2 = (complex(self.numero(k)) for k in ("x0", "x1", "x2"))
        tol = self.numero("tol", 1e-6)
        n_max = self.entero("max", 100)
        if len({x0, x1, x2}) < 3:
            raise ErrorMetodo("x₀, x₁ y x₂ deben ser distintos.")

        err, ok, n, p = float("inf"), False, 0, x2
        for n in range(1, n_max + 1):
            f0, f1, f2 = f(x0), f(x1), f(x2)
            h1, h2 = x1 - x0, x2 - x1
            d1, d2 = (f1 - f0) / h1, (f2 - f1) / h2
            a = (d2 - d1) / (h2 + h1)
            b = d2 + h2 * a
            D = cmath.sqrt(b * b - 4 * f2 * a)
            E = b + D if abs(b - D) < abs(b + D) else b - D
            if E == 0:
                raise ErrorMetodo("El denominador de Müller se anuló; prueba otros valores iniciales.")
            h = -2 * f2 / E
            p = x2 + h
            err = abs(h)
            self.agregar_fila(n, x0, x1, x2, p, abs(f(p)), err)
            if err < tol:
                ok = True
                break
            x0, x1, x2 = x1, x2, p

        es_real = abs(p.imag) < 1e-10 * max(1.0, abs(p.real))
        extra = "La raíz es real." if es_real else \
            f"Raíz compleja: su conjugada {fmt(p.conjugate())} también es raíz si f tiene coeficientes reales."
        self.resultado_raiz(p, n, err, ok, extra)
        referencia = [v.real for v in (complex(self.numero("x0")), complex(self.numero("x1")), p)]
        self.graficar(f_real, referencia, raiz=p.real if es_real else None)
