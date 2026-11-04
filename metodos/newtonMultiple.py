import sympy as sp

from metodos.base import MetodoBase, ErrorMetodo, envolver_real, x


class NewtonMultiple(MetodoBase):
    DESCRIPCION = ("Newton modificado para raíces múltiples: mantiene la convergencia "
                   "cuadrática cuando f y f′ se anulan en la raíz.")
    CAMPOS = [
        {"clave": "f", "etiqueta": "f(x)", "ejemplo": "exp(x) - x - 1", "ancho": True,
         "ayuda": "f′ y f″ se calculan automáticamente"},
        {"clave": "x0", "etiqueta": "x₀", "ejemplo": "1"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-8"},
        {"clave": "max", "etiqueta": "Iteraciones máx.", "ejemplo": "50"},
    ]
    COLUMNAS = ["i", "xᵢ", "f(xᵢ)", "f′(xᵢ)", "f″(xᵢ)", "xᵢ₊₁", "|xᵢ₊₁ − xᵢ|"]
    TITULO_GRAFICA = "Newton (raíces múltiples)"

    def ejecutar(self):
        expr, f = self.funcion("f")
        xi = self.numero("x0")
        tol = self.numero("tol", 1e-6)
        n_max = self.entero("max", 100)
        d1 = sp.diff(expr, x)
        d2 = sp.diff(d1, x)
        df = envolver_real(sp.lambdify(x, d1, "numpy"), "f′")
        ddf = envolver_real(sp.lambdify(x, d2, "numpy"), "f″")

        puntos, err, ok, n = [xi], float("inf"), False, 0
        for n in range(1, n_max + 1):
            fx, dfx, ddfx = f(xi), df(xi), ddf(xi)
            if fx == 0:
                err, ok = 0.0, True
                self.agregar_fila(n, xi, fx, dfx, ddfx, xi, 0.0)
                break
            den = dfx ** 2 - fx * ddfx
            if abs(den) < 1e-300:
                raise ErrorMetodo(f"[f′]² − f·f″ = 0 en x = {xi}; no se puede continuar.")
            x_nuevo = xi - fx * dfx / den
            err = abs(x_nuevo - xi)
            self.agregar_fila(n, xi, fx, dfx, ddfx, x_nuevo, err)
            xi = x_nuevo
            puntos.append(xi)
            if err < tol:
                ok = True
                break
        self.resultado_raiz(
            xi, n, err, ok,
            f"f′(x) = {str(d1).replace('**', '^')}   ·   f″(x) = {str(d2).replace('**', '^')}")
        self.graficar(f, puntos, puntos_x=puntos, raiz=xi)
