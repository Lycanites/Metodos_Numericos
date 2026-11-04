import numpy as np

from metodos.base import MetodoBase, ErrorMetodo, fmt, poli_texto, horner
from metodos.horner import CAMPO_COEFS
from metodos.newtonHorner import newton_horner


class Deflacion(MetodoBase):
    DESCRIPCION = ("Encuentra una raíz con Newton-Horner, divide P(x) ≈ (x − x₁)·Q₁(x) "
                   "y repite sobre Q. Cada raíz se pule sobre el polinomio original.")
    CAMPOS = [
        CAMPO_COEFS,
        {"clave": "x0", "etiqueta": "Aproximación inicial", "ejemplo": "1",
         "ayuda": "Se usa para la primera raíz; las siguientes parten de la anterior"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-10"},
        {"clave": "max", "etiqueta": "Iteraciones máx.", "ejemplo": "100"},
    ]
    COLUMNAS = ["#", "Raíz xᵢ", "Iteraciones", "P(xᵢ) original", "Q(x) tras deflación"]
    TITULO_GRAFICA = "Deflación"

    def ejecutar(self):
        coefs = self.coeficientes()
        guess = self.numero("x0")
        tol = self.numero("tol", 1e-10)
        n_max = self.entero("max", 100)
        P = lambda t: np.polyval(coefs, t)

        actual, raices, nota = coefs[:], [], ""
        while len(actual) > 2:
            ok = False
            cota = 1 + max(abs(c / actual[0]) for c in actual[1:])
            # Si Newton no converge desde la aproximación, se prueban otros arranques
            for inicio in (guess, -guess, 0.0, 1.0, -1.0, cota / 2, -cota / 2, cota, -cota):
                try:
                    r, it, _, ok = newton_horner(actual, inicio, tol, n_max)
                except ErrorMetodo:
                    ok = False
                if ok:
                    break
            if not ok:
                restantes = np.roots(actual)
                nota = (f"No hay más raíces reales alcanzables. Factor restante: "
                        f"{poli_texto(actual)}  →  raíces: "
                        + ", ".join(fmt(complex(z), 6) for z in restantes))
                break
            try:   # pulir sobre el polinomio original
                rp, _, _, okp = newton_horner(coefs, r, tol, n_max)
                if okp and abs(rp - r) < 1e-3 * max(1.0, abs(r)):
                    r = rp
            except ErrorMetodo:
                pass
            actual = horner(actual, r)[:-1]
            raices.append(r)
            self.agregar_fila(len(raices), r, it, P(r), poli_texto(actual))
            guess = r

        if len(actual) == 2:
            r = -actual[1] / actual[0]
            raices.append(r)
            self.agregar_fila(len(raices), r, "directa", P(r), "—")

        if not raices:
            raise ErrorMetodo("No se encontró ninguna raíz real con esa aproximación inicial.")
        texto = "Raíces reales: " + ", ".join(fmt(r) for r in raices)
        if nota:
            texto += "\n" + nota
        self.mostrar_resultado(texto)
        self.graficar(P, raices + [guess], puntos_x=raices, etiqueta_puntos="Raíces",
                      etiqueta_curva="P(x)")
