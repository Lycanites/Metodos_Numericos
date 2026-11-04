import math

from metodos.base import MetodoBase, ErrorMetodo, fmt


def biseccion(f, a, b, tol=1e-6, max_iter=100, log_callback=None):
    """Devuelve (p, n, error, convergio). f debe ser una función numérica."""
    fa = f(a)
    p, err = a, b - a
    for n in range(1, max_iter + 1):
        p = a + (b - a) / 2
        fp = f(p)
        err = (b - a) / 2
        if log_callback:
            log_callback(n, a, b, p, fp, err)
        if fp == 0 or err < tol:
            return p, n, err, True
        if fa * fp > 0:
            a, fa = p, fp
        else:
            b = p
    return p, max_iter, err, False


class Biseccion(MetodoBase):
    DESCRIPCION = ("Divide a la mitad el intervalo [a, b] y conserva la mitad "
                   "donde f(x) cambia de signo.")
    CAMPOS = [
        {"clave": "f", "etiqueta": "f(x)", "ejemplo": "x^3 + 4x^2 - 10", "ancho": True,
         "ayuda": "Usa ^ para potencias. Se permite 2x, sin(x), exp(x), ln(x), sqrt(x)…"},
        {"clave": "a", "etiqueta": "a", "ejemplo": "1"},
        {"clave": "b", "etiqueta": "b", "ejemplo": "2"},
        {"clave": "tol", "etiqueta": "Tolerancia", "ejemplo": "1e-6", "ayuda": "Por defecto 1e-6"},
        {"clave": "max", "etiqueta": "Iteraciones máx.", "ejemplo": "100", "ayuda": "Por defecto 100"},
    ]
    COLUMNAS = ["n", "aₙ", "bₙ", "pₙ", "f(pₙ)", "(bₙ − aₙ)/2"]
    TITULO_GRAFICA = "Bisección"

    def ejecutar(self):
        _, f = self.funcion("f")
        a, b = self.numero("a"), self.numero("b")
        tol = self.numero("tol", 1e-6)
        n_max = self.entero("max", 100)
        if a >= b:
            raise ErrorMetodo("a debe ser menor que b.")
        fa, fb = f(a), f(b)
        if fa == 0 or fb == 0:
            raiz = a if fa == 0 else b
            self.mostrar_resultado(f"Raíz exacta en un extremo: p = {fmt(raiz)}")
            return
        if fa * fb > 0:
            raise ErrorMetodo("f(a) y f(b) deben tener signos opuestos.")

        puntos = []
        p, n, err, ok = biseccion(
            f, a, b, tol, n_max,
            log_callback=lambda *fila: (self.agregar_fila(*fila), puntos.append(fila[3]))
        )
        n_teorico = math.ceil(math.log((b - a) / tol) / math.log(2))
        self.resultado_raiz(p, n, err, ok,
                            f"Iteraciones necesarias según la cota: n ≥ {n_teorico}")
        self.graficar(f, [a, b] + puntos, puntos_x=puntos, raiz=p)

