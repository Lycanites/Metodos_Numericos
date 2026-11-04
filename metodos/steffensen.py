from metodos.base import MetodoBase, ErrorMetodo, fmt

class steffensen(MetodoBase):
    DESCRIPCION = ("Punto fijo acelerado con Aitken Δ² en cada paso: "
                   "p₁ = g(p₀), p₂ = g(p₁), p = p₀ − (p₁ − p₀)² / (p₂ − 2p₁ + p₀).")
    CAMPOS = [
        {"clave": "g", "etiqueta": "g(x)", "ejemplo": "sqrt(10/(x + 4))", "ancho": True,
         "ayuda": "Despeja f(x) = 0 como x = g(x)"},
        {"clave": "p0", "etiqueta": "p₀", "ejemplo": "1.5"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-8"},
        {"clave": "max", "etiqueta": "Iteraciones máx.", "ejemplo": "50"},
    ]
    COLUMNAS = ["n", "p₀", "p₁ = g(p₀)", "p₂ = g(p₁)", "p", "|p − p₀|"]
    TITULO_GRAFICA = "Steffensen  (se grafica g(x) − x)"

    def ejecutar(self):
        _, g = self.funcion("g")
        p0 = self.numero("p0")
        tol = self.numero("tol", 1e-6)
        n_max = self.entero("max", 100)

        puntos, err, ok, n, p = [p0], float("inf"), False, 0, p0
        for n in range(1, n_max + 1):
            p1 = g(p0)
            p2 = g(p1)
            den = p2 - 2 * p1 + p0
            p = p2 if den == 0 else p0 - (p1 - p0) ** 2 / den
            err = abs(p - p0)
            self.agregar_fila(n, p0, p1, p2, p, err)
            puntos.append(p)
            if den == 0 or err < tol:
                ok = True
                break
            if abs(p) > 1e15:
                raise ErrorMetodo("El método diverge con este p₀.")
            p0 = p
        self.resultado_raiz(p, n, err, ok, f"Comprobación: g(p) = {fmt(g(p))}")
        self.graficar(lambda t: g(t) - t, puntos, puntos_x=puntos, raiz=p,
                      etiqueta_curva="g(x) − x")
