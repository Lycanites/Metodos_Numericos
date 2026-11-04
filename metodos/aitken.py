from metodos.base import MetodoBase, ErrorMetodo, fmt


class Aitken(MetodoBase):
    DESCRIPCION = ("Acelera una sucesión de punto fijo pₙ₊₁ = g(pₙ) con "
                   "p̂ₙ = pₙ − (pₙ₊₁ − pₙ)² / (pₙ₊₂ − 2pₙ₊₁ + pₙ).")
    CAMPOS = [
        {"clave": "g", "etiqueta": "g(x)", "ejemplo": "cos(x)", "ancho": True,
         "ayuda": "Genera la sucesión pₙ₊₁ = g(pₙ)"},
        {"clave": "p0", "etiqueta": "p₀", "ejemplo": "0.5"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-6"},
        {"clave": "max", "etiqueta": "Términos máx.", "ejemplo": "50"},
    ]
    COLUMNAS = ["n", "pₙ", "pₙ₊₁", "pₙ₊₂", "p̂ₙ", "|p̂ₙ − p̂ₙ₋₁|"]
    TITULO_GRAFICA = "Aitken Δ²  (se grafica g(x) − x)"

    def ejecutar(self):
        _, g = self.funcion("g")
        p = [self.numero("p0")]
        tol = self.numero("tol", 1e-6)
        n_max = self.entero("max", 50)

        def termino(k):
            while len(p) <= k:
                siguiente = g(p[-1])
                if abs(siguiente) > 1e15:
                    raise ErrorMetodo("La sucesión pₙ diverge con este g(x) y p₀.")
                p.append(siguiente)
            return p[k]

        anterior, ph, err, ok, n = None, None, None, False, 0
        for n in range(n_max):
            pn, pn1, pn2 = termino(n), termino(n + 1), termino(n + 2)
            den = pn2 - 2 * pn1 + pn
            ph = pn2 if den == 0 else pn - (pn1 - pn) ** 2 / den
            err = None if anterior is None else abs(ph - anterior)
            self.agregar_fila(n, pn, pn1, pn2, ph, err)
            if den == 0 or (err is not None and err < tol):
                ok = True
                break
            anterior = ph

        texto = (f"Límite acelerado  p̂ ≈ {fmt(ph)}\n"
                 f"{n + 1} valores p̂ · error {fmt(err if err is not None else 0)}\n"
                 f"Sin acelerar, pₙ₊₂ = {fmt(p[n + 2])}")
        if not ok:
            texto = "No alcanzó la tolerancia.\n" + texto
        self.mostrar_resultado(texto)
        self.graficar(lambda t: g(t) - t, p[:n + 3] + [ph], puntos_x=p[:n + 3],
                      etiqueta_puntos="pₙ", raiz=ph, etiqueta_raiz=f"p̂ ≈ {fmt(ph, 6)}",
                      etiqueta_curva="g(x) − x")
