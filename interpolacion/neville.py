import sympy as sp

from metodos.base import MetodoBase, CAMPOS_INTERPOLACION, fmt, sub, x


class Neville(MetodoBase):
    DESCRIPCION = ("Evalúa el polinomio interpolante en un punto sin construirlo: "
                   "Qᵢ,ⱼ = [(x − xᵢ₋ⱼ)Qᵢ,ⱼ₋₁ − (x − xᵢ)Qᵢ₋₁,ⱼ₋₁] / (xᵢ − xᵢ₋ⱼ).")
    CAMPOS = [dict(c, etiqueta="Evaluar en x (obligatorio)") if c["clave"] == "xe" else c
              for c in CAMPOS_INTERPOLACION]
    COLUMNAS = ["i", "xᵢ", "Qᵢ,₀"]
    TITULO_GRAFICA = "Neville"

    def ejecutar(self):
        xs, ys, _, f, xe = self.datos_interpolacion(requiere_xe=True)
        n = len(xs) - 1
        self.configurar_columnas(["i", "xᵢ"] + [f"Qᵢ,{sub(j)}" for j in range(n + 1)])

        Q = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            Q[i][0] = ys[i]
        for i in range(1, n + 1):
            for j in range(1, i + 1):
                Q[i][j] = ((xe - xs[i - j]) * Q[i][j - 1] - (xe - xs[i]) * Q[i - 1][j - 1]) \
                          / (xs[i] - xs[i - j])
        for i in range(n + 1):
            self.agregar_fila(i, xs[i], *Q[i])

        poli = sp.interpolate(list(zip(xs, ys)), x)
        self.terminar_interpolacion(
            poli, xs, f, xe, valor_xe=Q[n][n],
            lineas=[f"Q{sub(n)},{sub(n)} = {fmt(Q[n][n])}  (valor final de la tabla)"])
