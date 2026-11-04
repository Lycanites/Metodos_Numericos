import cmath

import numpy as np

from metodos.base import MetodoBase, ErrorMetodo, fmt, poli_texto
from metodos.horner import CAMPO_COEFS


def _cuadratica(a2, a1, a0):
    d = cmath.sqrt(a1 * a1 - 4 * a2 * a0)
    return [(-a1 + d) / (2 * a2), (-a1 - d) / (2 * a2)]


class Bairstow(MetodoBase):
    DESCRIPCION = ("Extrae factores cuadráticos x² − r·x − s con Newton en dos variables. "
                   "Encuentra raíces reales y complejas con aritmética real.")
    CAMPOS = [
        dict(CAMPO_COEFS, ejemplo="1, -3.5, 2.75, 2.125, -3.875, 1.25"),
        {"clave": "r0", "etiqueta": "r₀", "ejemplo": "-1"},
        {"clave": "s0", "etiqueta": "s₀", "ejemplo": "-1"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-10"},
        {"clave": "max", "etiqueta": "Iteraciones máx.", "ejemplo": "100"},
    ]
    COLUMNAS = ["Factor", "Iter", "r", "s", "Δr", "Δs"]
    TITULO_GRAFICA = "Bairstow"

    def ejecutar(self):
        coefs = self.coeficientes()
        r, s = self.numero("r0"), self.numero("s0")
        tol = self.numero("tol", 1e-10)
        n_max = self.entero("max", 100)

        a = list(reversed(coefs))         # a[i] = coeficiente de x^i
        raices, factores, factor = [], [], 1
        while len(a) - 1 >= 3:
            n = len(a) - 1
            ok = False
            for it in range(1, n_max + 1):
                b = self._dividir(a, r, s)
                c = [0.0] * (n + 1)
                c[n] = b[n]
                c[n - 1] = b[n - 1] + r * c[n]
                for i in range(n - 2, 0, -1):
                    c[i] = b[i] + r * c[i + 1] + s * c[i + 2]
                det = c[2] * c[2] - c[3] * c[1]
                if abs(det) < 1e-14:
                    r, s = r + 1, s + 1       # perturbación para salir del punto singular
                    continue
                dr = (-b[1] * c[2] + b[0] * c[3]) / det
                ds = (-b[0] * c[2] + b[1] * c[1]) / det
                r, s = r + dr, s + ds
                self.agregar_fila(factor, it, r, s, dr, ds)
                if abs(dr) < tol and abs(ds) < tol:
                    ok = True
                    break
            if not ok:
                raise ErrorMetodo(
                    f"El factor {factor} no convergió en {n_max} iteraciones. "
                    "Prueba otros r₀, s₀." +
                    (f"\nRaíces halladas: {', '.join(fmt(z) for z in raices)}" if raices else ""))
            raices += _cuadratica(1.0, -r, -s)
            factores.append(f"x² {'−' if r >= 0 else '+'} {fmt(abs(r))}x "
                            f"{'−' if s >= 0 else '+'} {fmt(abs(s))}")
            a = self._dividir(a, r, s)[2:]
            factor += 1

        if len(a) - 1 == 2:
            raices += _cuadratica(a[2], a[1], a[0])
            factores.append(poli_texto(list(reversed(a))))
        elif len(a) - 1 == 1:
            raices.append(complex(-a[0] / a[1]))
            factores.append(poli_texto(list(reversed(a))))

        self.mostrar_resultado(
            "Factores: " + "  ·  ".join(f"({t})" for t in factores) + "\n"
            "Raíces: " + ",   ".join(fmt(z, 7) for z in raices))
        reales = [z.real for z in raices if abs(z.imag) < 1e-9]
        self.graficar(lambda t: np.polyval(coefs, t),
                      reales or [z.real for z in raices],
                      puntos_x=reales or None, etiqueta_puntos="Raíces reales",
                      etiqueta_curva="P(x)")

    @staticmethod
    def _dividir(a, r, s):
        n = len(a) - 1
        b = [0.0] * (n + 1)
        b[n] = a[n]
        b[n - 1] = a[n - 1] + r * b[n]
        for i in range(n - 2, -1, -1):
            b[i] = a[i] + r * b[i + 1] + s * b[i + 2]
        return b
