import sympy as sp

from metodos.base import MetodoBase, ErrorMetodo, envolver_real, x


class FrmNewtonRaphson(MetodoBase):
    DESCRIPCION = "Usa la recta tangente: pₙ = pₙ₋₁ − f(pₙ₋₁) / f′(pₙ₋₁). La derivada se calcula sola."
    CAMPOS = [
        {"clave": "f", "etiqueta": "f(x)", "ejemplo": "cos(x) - x", "ancho": True,
         "ayuda": "Usa ^ para potencias. Se permite 2x, sin(x), exp(x), ln(x)…"},
        {"clave": "p0", "etiqueta": "p₀", "ejemplo": "pi/4"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-8"},
        {"clave": "max", "etiqueta": "Iteraciones máx.", "ejemplo": "50"},
    ]
    COLUMNAS = ["n", "pₙ₋₁", "f(pₙ₋₁)", "f′(pₙ₋₁)", "pₙ", "|pₙ − pₙ₋₁|"]
    TITULO_GRAFICA = "Newton-Raphson"

    def ejecutar(self):
        expr, f = self.funcion("f")
        p = self.numero("p0")
        tol = self.numero("tol", 1e-6)
        n_max = self.entero("max", 100)
        dexpr = sp.diff(expr, x)
        df = envolver_real(sp.lambdify(x, dexpr, "numpy"), "f′")

        puntos, err, ok, n = [p], float("inf"), False, 0
        for n in range(1, n_max + 1):
            fp, dfp = f(p), df(p)
            if abs(dfp) < 1e-14:
                raise ErrorMetodo(f"f′(x) ≈ 0 en x = {p}; no se puede dividir entre cero.")
            p_nuevo = p - fp / dfp
            err = abs(p_nuevo - p)
            self.agregar_fila(n, p, fp, dfp, p_nuevo, err)
            p = p_nuevo
            puntos.append(p)
            if err < tol:
                ok = True
                break
        derivada = str(dexpr).replace("**", "^")
        self.resultado_raiz(p, n, err, ok, f"f′(x) = {derivada}")
        self.graficar(f, puntos, puntos_x=puntos, raiz=p)
