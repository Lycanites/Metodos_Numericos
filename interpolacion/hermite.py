import sympy as sp

from metodos.base import MetodoBase, ErrorMetodo, CAMPOS_INTERPOLACION, envolver_real, sub, x
from interpolacion.diferenciasDivididas import forma_newton, polinomio_newton


class Hermite(MetodoBase):
    DESCRIPCION = ("Interpola valores y derivadas: cada nodo se duplica (z₂ᵢ = z₂ᵢ₊₁ = xᵢ) "
                   "y f[z₂ᵢ, z₂ᵢ₊₁] = f′(xᵢ). Da un polinomio de grado ≤ 2n + 1.")
    CAMPOS = [
        {"clave": "xs", "etiqueta": "Nodos xᵢ", "ancho": True, "ejemplo": "1.3, 1.6, 1.9"},
        {"clave": "ys", "etiqueta": "Valores f(xᵢ)", "ancho": True,
         "ejemplo": "0.6200860, 0.4554022, 0.2818186", "ayuda": "Déjalo vacío si escribes f(x)"},
        {"clave": "dys", "etiqueta": "Derivadas f′(xᵢ)", "ancho": True,
         "ejemplo": "-0.5220232, -0.5698959, -0.5811571",
         "ayuda": "Déjalo vacío si escribes f(x); se deriva automáticamente"},
        {"clave": "f", "etiqueta": "f(x) (opcional)", "ejemplo": ""},
        {"clave": "xe", "etiqueta": "Evaluar en x", "ejemplo": "1.5"},
    ]
    COLUMNAS = ["i", "zᵢ", "f[zᵢ]"]
    TITULO_GRAFICA = "Hermite"

    def ejecutar(self):
        xs, ys, expr, f, xe = self.datos_interpolacion()
        dys = self.lista("dys", requerido=False)
        if not dys:
            if expr is None:
                raise ErrorMetodo("Escribe las derivadas f′(xᵢ) o una función f(x).")
            df = envolver_real(sp.lambdify(x, sp.diff(expr, x), "numpy"), "f′")
            dys = [df(v) for v in xs]
        if len(dys) != len(xs):
            raise ErrorMetodo(f"Hay {len(xs)} nodos pero {len(dys)} derivadas.")

        n = len(xs)
        m = 2 * n
        z = [0.0] * m
        Q = [[None] * m for _ in range(m)]
        for i in range(n):
            z[2 * i] = z[2 * i + 1] = xs[i]
            Q[2 * i][0] = Q[2 * i + 1][0] = ys[i]
            Q[2 * i + 1][1] = dys[i]
            if i > 0:
                Q[2 * i][1] = (Q[2 * i][0] - Q[2 * i - 1][0]) / (z[2 * i] - z[2 * i - 1])
        for i in range(2, m):
            for j in range(2, i + 1):
                Q[i][j] = (Q[i][j - 1] - Q[i - 1][j - 1]) / (z[i] - z[i - j])

        self.configurar_columnas(["i", "zᵢ", "f[zᵢ]"] + [f"Orden {j}" for j in range(1, m)])
        for i in range(m):
            self.agregar_fila(i, z[i], *Q[i])

        coef = [Q[k][k] for k in range(m)]
        self.terminar_interpolacion(
            polinomio_newton(coef, z), xs, f, xe,
            lineas=[f"H{sub(m - 1)}(x) = {forma_newton(coef, z)}"])
