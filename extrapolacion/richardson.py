import sympy as sp

from metodos.base import MetodoBase, ErrorMetodo, fmt, sub, x


class Richardson(MetodoBase):
    DESCRIPCION = ("Extrapolación de Richardson sobre la diferencia central "
                   "N₁(h) = [f(x₀ + h) − f(x₀ − h)] / 2h para aproximar f′(x₀):  "
                   "Nⱼ(h) = Nⱼ₋₁(h/2) + [Nⱼ₋₁(h/2) − Nⱼ₋₁(h)] / (4ʲ⁻¹ − 1).")
    CAMPOS = [
        {"clave": "f", "etiqueta": "f(x)", "ejemplo": "x*exp(x)", "ancho": True},
        {"clave": "x0", "etiqueta": "x₀", "ejemplo": "2"},
        {"clave": "h", "etiqueta": "h inicial", "ejemplo": "0.2"},
        {"clave": "niveles", "etiqueta": "Niveles", "ejemplo": "3",
         "ayuda": "Número de columnas N₁ … Nₙ (h se divide entre 2 en cada fila)"},
    ]
    COLUMNAS = ["i", "h", "N₁"]
    TITULO_GRAFICA = "Richardson"

    def ejecutar(self):
        expr, f = self.funcion("f")
        x0 = self.numero("x0")
        h = self.numero("h")
        niveles = self.entero("niveles", 3)
        if h <= 0:
            raise ErrorMetodo("h debe ser positivo.")
        if niveles > 15:
            raise ErrorMetodo("Usa a lo más 15 niveles (después domina el redondeo).")
        self.configurar_columnas(["i", "h"] + [f"N{sub(j + 1)}" for j in range(niveles)])

        N = [[None] * niveles for _ in range(niveles)]
        for i in range(niveles):
            hi = h / 2 ** i
            N[i][0] = (f(x0 + hi) - f(x0 - hi)) / (2 * hi)
            for j in range(1, i + 1):
                N[i][j] = N[i][j - 1] + (N[i][j - 1] - N[i - 1][j - 1]) / (4 ** j - 1)
            self.agregar_fila(i, hi, *N[i])

        aprox = N[-1][-1]
        texto = [f"f′({fmt(x0)}) ≈ N{sub(niveles)} = {fmt(aprox, 10)}"]
        try:
            exacta = float(sp.diff(expr, x).subs(x, x0))
            texto.append(f"Derivada exacta = {fmt(exacta, 10)} · error = {fmt(abs(exacta - aprox))}")
        except Exception:
            pass
        self.mostrar_resultado("\n".join(texto))
        self.graficar(f, [x0 - h, x0 + h],
                      puntos_x=[x0 - h, x0 + h], etiqueta_puntos="x₀ ± h",
                      raiz=x0, etiqueta_raiz=f"x₀ = {fmt(x0, 4)}")
