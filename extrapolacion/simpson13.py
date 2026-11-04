from metodos.base import MetodoBase, ErrorMetodo, fmt

CAMPOS_INTEGRAL = [
    {"clave": "f", "etiqueta": "f(x)", "ejemplo": "x^2*ln(x)", "ancho": True},
    {"clave": "a", "etiqueta": "a", "ejemplo": "1"},
    {"clave": "b", "etiqueta": "b", "ejemplo": "1.5"},
]


def leer_intervalo(pagina):
    expr, f = pagina.funcion("f")
    a, b = pagina.numero("a"), pagina.numero("b")
    if a >= b:
        raise ErrorMetodo("a debe ser menor que b.")
    return expr, f, a, b


class Simpson13(MetodoBase):
    DESCRIPCION = ("Simpson 1/3 compuesto: ∫ f ≈ (h/3)[f₀ + 4f₁ + 2f₂ + 4f₃ + … + fₙ], "
                   "h = (b − a)/n con n par. Con n = 2 es la regla simple.")
    CAMPOS = CAMPOS_INTEGRAL + [
        {"clave": "n", "etiqueta": "Subintervalos n (par)", "ejemplo": "2"}]
    COLUMNAS = ["i", "xᵢ", "f(xᵢ)", "Coeficiente", "Coef · f(xᵢ)"]
    TITULO_GRAFICA = "Simpson 1/3"

    def ejecutar(self):
        expr, f, a, b = leer_intervalo(self)
        n = self.entero("n", 2, minimo=2)
        if n % 2:
            raise ErrorMetodo("Para Simpson 1/3, n debe ser par.")
        h = (b - a) / n
        suma, nodos = 0.0, []
        for i in range(n + 1):
            xi = a + i * h
            c = 1 if i in (0, n) else (4 if i % 2 else 2)
            fx = f(xi)
            suma += c * fx
            nodos.append(xi)
            self.agregar_fila(i, xi, fx, c, c * fx)
        aprox = h / 3 * suma
        self.terminar_integral(expr, f, a, b, aprox, nodos,
                               lineas=[f"h = {fmt(h)} · Σ = {fmt(suma)}"])
