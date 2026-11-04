from metodos.base import (MetodoBase, CAMPOS_INTERPOLACION, fmt, sub,
                          factor_texto, x)


_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _producto_texto(nodos):
    """(x − a)(x − a)(x − b) → (x − a)²(x − b)"""
    texto, i = "", 0
    while i < len(nodos):
        j = i
        while j + 1 < len(nodos) and nodos[j + 1] == nodos[i]:
            j += 1
        veces = j - i + 1
        texto += factor_texto(nodos[i]) + (str(veces).translate(_SUP) if veces > 1 else "")
        i = j + 1
    return texto


def forma_newton(coef, nodos):
    """Texto de c₀ + c₁(x − x₀) + c₂(x − x₀)(x − x₁) + …"""
    texto = fmt(coef[0])
    for k in range(1, len(coef)):
        c = coef[k]
        if c == 0:
            continue
        producto = _producto_texto(nodos[:k])
        texto += f" {'−' if c < 0 else '+'} {fmt(abs(c))}{producto}"
    return texto


def polinomio_newton(coef, nodos):
    poli, producto = 0, 1
    for k, c in enumerate(coef):
        poli += c * producto
        producto *= (x - nodos[k])
    return poli


class DiferenciasDivididas(MetodoBase):
    DESCRIPCION = ("Forma de Newton: Fᵢ,ⱼ = (Fᵢ,ⱼ₋₁ − Fᵢ₋₁,ⱼ₋₁) / (xᵢ − xᵢ₋ⱼ), "
                   "Pₙ(x) = Σ Fₖ,ₖ · Π(x − xᵢ). La diagonal da los coeficientes.")
    CAMPOS = CAMPOS_INTERPOLACION
    COLUMNAS = ["i", "xᵢ", "f[xᵢ]"]
    TITULO_GRAFICA = "Diferencias divididas"

    def ejecutar(self):
        xs, ys, _, f, xe = self.datos_interpolacion()
        n = len(xs) - 1
        self.configurar_columnas(["i", "xᵢ", "f[xᵢ]"] + [f"Orden {j}" for j in range(1, n + 1)])

        F = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            F[i][0] = ys[i]
        for i in range(1, n + 1):
            for j in range(1, i + 1):
                F[i][j] = (F[i][j - 1] - F[i - 1][j - 1]) / (xs[i] - xs[i - j])
        for i in range(n + 1):
            self.agregar_fila(i, xs[i], *F[i])

        coef = [F[k][k] for k in range(n + 1)]
        self.terminar_interpolacion(
            polinomio_newton(coef, xs), xs, f, xe,
            lineas=[f"Forma de Newton: P{sub(n)}(x) = {forma_newton(coef, xs)}"])
