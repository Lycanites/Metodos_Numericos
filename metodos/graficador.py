import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class Graficador(QWidget):
    """
    Widget reutilizable para graficar f(x) junto con los puntos
    generados por cualquier método numérico (bisección, secante,
    Newton-Raphson, punto fijo, etc.)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = Figure(figsize=(5, 4))
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
                          raiz=None, titulo="f(x)", num_muestras=400):
        """
        f: función numérica (resultado de lambdify)
        x_min, x_max: rango del eje x
        puntos_x: lista de valores x (iteraciones) a marcar sobre la curva
        raiz: valor final de la raíz aproximada, se resalta en rojo
        """
        self.ax.clear()

        xs = np.linspace(x_min, x_max, num_muestras)
        ys = []
        for val in xs:
            try:
                y = f(val)
                if isinstance(y, complex):
                    y = np.nan
            except Exception:
                y = np.nan
            ys.append(y)

        self.ax.plot(xs, ys, color="#3498db", linewidth=1.8, label="f(x)")
        self.ax.axhline(0, color="gray", linewidth=0.8)
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.ax.set_title(titulo)

        # Marca los puntos de iteración sobre la curva
        if puntos_x:
            puntos_y = []
            for val in puntos_x:
                try:
                    y = f(val)
                    if isinstance(y, complex):
                        y = np.nan
                except Exception:
                    y = np.nan
                puntos_y.append(y)

            self.ax.plot(puntos_x, puntos_y, "o", color="#f39c12",
                         markersize=5, label="Iteraciones")

        # Resalta la raíz encontrada
        if raiz is not None:
            try:
                y_raiz = f(raiz)
                self.ax.plot(raiz, y_raiz, "o", color="#e74c3c",
                             markersize=9, label=f"Raíz ≈ {raiz:.6f}")
            except Exception:
                pass

        self.ax.legend(loc="best", fontsize=8)
        self.canvas.draw()