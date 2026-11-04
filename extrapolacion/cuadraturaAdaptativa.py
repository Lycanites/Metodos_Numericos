from metodos.base import MetodoBase, ErrorMetodo, fmt
from extrapolacion.simpson13 import leer_intervalo


class CuadraturaAdaptativa(MetodoBase):
    DESCRIPCION = ("Aplica Simpson en [a, b] y en sus dos mitades. Si "
                   "|S(a,b) − S(a,m) − S(m,b)| < 15·tol acepta; si no, subdivide cada mitad "
                   "con tolerancia tol/2.")
    CAMPOS = [
        {"clave": "f", "etiqueta": "f(x)", "ejemplo": "(100/x^2)*sin(10/x)", "ancho": True},
        {"clave": "a", "etiqueta": "a", "ejemplo": "1"},
        {"clave": "b", "etiqueta": "b", "ejemplo": "3"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-4"},
        {"clave": "nivel", "etiqueta": "Nivel máx.", "ejemplo": "10",
         "ayuda": "Profundidad máxima de subdivisión"},
    ]
    COLUMNAS = ["Nivel", "aᵢ", "bᵢ", "S(aᵢ, bᵢ)", "S(a, m) + S(m, b)",
                "|Diferencia|", "15·tolᵢ", "Estado"]
    TITULO_GRAFICA = "Cuadratura adaptativa"

    def ejecutar(self):
        expr, f, a, b = leer_intervalo(self)
        tol = self.numero("tol", 1e-5)
        nivel_max = self.entero("nivel", 10)
        if nivel_max > 20:
            raise ErrorMetodo("Usa un nivel máximo de 20 o menos.")

        def simpson(p, q, fp, fm, fq):
            return (q - p) / 6 * (fp + 4 * fm + fq)

        fa, fb, fm = f(a), f(b), f((a + b) / 2)
        pila = [(a, b, fa, fm, fb, tol, 1, simpson(a, b, fa, fm, fb))]
        total, cortes, evaluaciones, al_limite = 0.0, {a, b}, 3, False

        while pila:
            p, q, fp, fm, fq, tol_i, nivel, s_pq = pila.pop()
            m = (p + q) / 2
            fl, fr = f((p + m) / 2), f((m + q) / 2)
            evaluaciones += 2
            s_l, s_r = simpson(p, m, fp, fl, fm), simpson(m, q, fm, fr, fq)
            dif = abs(s_pq - s_l - s_r)
            if dif < 15 * tol_i or nivel >= nivel_max:
                estado = "Aceptado" if dif < 15 * tol_i else "Nivel máx."
                al_limite |= estado != "Aceptado"
                total += s_l + s_r
                cortes.add(m)
                self.agregar_fila(nivel, p, q, s_pq, s_l + s_r, dif, 15 * tol_i, estado)
            else:
                self.agregar_fila(nivel, p, q, s_pq, s_l + s_r, dif, 15 * tol_i, "Subdividir")
                cortes.add(m)
                pila.append((m, q, fm, fr, fq, tol_i / 2, nivel + 1, s_r))
                pila.append((p, m, fp, fl, fm, tol_i / 2, nivel + 1, s_l))

        lineas = [f"{evaluaciones} evaluaciones de f · {len(cortes) - 1} subintervalos finales"]
        if al_limite:
            lineas.append("⚠ Algunos subintervalos llegaron al nivel máximo sin cumplir la tolerancia.")
        nodos = sorted(cortes)
        self.terminar_integral(expr, f, a, b, total, lineas=lineas, verticales=nodos)
