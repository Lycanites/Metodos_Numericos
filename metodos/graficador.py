import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


def _evaluar(f, val):
    try:
        with np.errstate(all="ignore"):
            y = f(val)
        if isinstance(y, complex) or np.iscomplexobj(y):
            return np.nan
        y = float(y)
        return y if np.isfinite(y) else np.nan
    except Exception:
        return np.nan


class Graficador(QWidget):
    """
    Widget reutilizable para graficar f(x) junto con los puntos
    generados por cualquier método numérico.
    Es compatible con la versión anterior: los parámetros nuevos son opcionales.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = Figure(figsize=(5, 4))
        self.figure.set_facecolor("white")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout.addWidget(self.canvas)
        self.limpiar()

    def limpiar(self):
        """Limpia la gráfica y deja los ejes en blanco."""
        self.ax.clear()
        self.ax.set_title("Gráfica")
        self.ax.axhline(0, color="gray", linewidth=0.8)
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.canvas.draw()

    def graficar_funcion(self, f, x_min, x_max, puntos_x=None,
                         raiz=None, titulo="f(x)", num_muestras=400,
                         etiqueta_curva="f(x)", etiqueta_puntos="Iteraciones",
                         etiqueta_raiz=None, area=None, verticales=None,
                         curva_extra=None):
        """
        f: función numérica
        x_min, x_max: rango del eje x
        puntos_x: valores x a marcar sobre la curva (iteraciones, nodos…)
        raiz: punto a resaltar en rojo
        area: (a, b) sombrea el área bajo la curva (integración)
        verticales: lista de x donde dibujar líneas verticales tenues
        curva_extra: (g, etiqueta) segunda curva punteada, p. ej. la f real
        """
        self.ax.clear()

        xs = np.linspace(x_min, x_max, num_muestras)
        ys = np.array([_evaluar(f, v) for v in xs])

        if curva_extra is not None:
            g, etiqueta = curva_extra
            ys_g = np.array([_evaluar(g, v) for v in xs])
            self.ax.plot(xs, ys_g, "--", color="#95a5a6", linewidth=1.2, label=etiqueta)

        self.ax.plot(xs, ys, color="#3498db", linewidth=1.8, label=etiqueta_curva)
        self.ax.axhline(0, color="gray", linewidth=0.8)
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.ax.set_title(titulo)

        if area is not None:
            a, b = area
            xa = np.linspace(a, b, 300)
            ya = np.array([_evaluar(f, v) for v in xa])
            self.ax.fill_between(xa, ya, 0, color="#3498db", alpha=0.18)

        if verticales:
            for v in verticales:
                self.ax.axvline(v, color="#7f8c8d", linewidth=0.6, alpha=0.5)

        if puntos_x:
            puntos_y = [_evaluar(f, v) for v in puntos_x]
            self.ax.plot(puntos_x, puntos_y, "o", color="#f39c12",
                         markersize=5, label=etiqueta_puntos)

        if raiz is not None:
            y_raiz = _evaluar(f, raiz)
            if np.isfinite(y_raiz):
                etiqueta = etiqueta_raiz or f"Raíz ≈ {raiz:.6f}"
                self.ax.plot(raiz, y_raiz, "o", color="#e74c3c",
                             markersize=9, label=etiqueta)

        self.ax.legend(loc="best", fontsize=8)
        try:
            self.figure.tight_layout()
        except Exception:
            pass
        self.canvas.draw()
