import sys
import numpy as np
from sympy import symbols, diff
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QHBoxLayout, QFormLayout, QSplitter, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

x = symbols('x')

transformaciones = standard_transformations + (
    implicit_multiplication_application,  # Permite "2x" en vez de "2*x"
    convert_xor,                          # Permite "^" en vez de "**"
)


def parsear_funcion(texto):
    """
    Convierte un string ingresado por el usuario en una expresión sympy en x.
    Lanza ValueError si el input es inválido.
    """
    texto = texto.strip()
    if not texto:
        raise ValueError("La función no puede estar vacía.")

    try:
        expr = parse_expr(texto, local_dict={"x": x}, transformations=transformaciones)
    except Exception as e:
        raise ValueError(f"No se pudo interpretar la función: {e}")

    simbolos_extra = expr.free_symbols - {x}
    if simbolos_extra:
        raise ValueError(
            f"La función solo debe depender de x. Símbolo(s) no reconocido(s): "
            f"{', '.join(str(s) for s in simbolos_extra)}"
        )

    return expr


def evalua(func, valor_x):
    return float(func.subs(x, valor_x))


def obtener_derivada(func):
    return diff(func, x)


def newton_raphson(p0, err, max_iter, func, log_callback=None):
    func_derivada = obtener_derivada(func)

    pi = p0
    error_calculado = float('inf')
    iteracion = 0

    while error_calculado > err and iteracion < max_iter:
        f_pi = evalua(func, pi)
        f_prime_pi = evalua(func_derivada, pi)

        if abs(f_prime_pi) < 1e-12:
            raise ValueError(f"La derivada f'(x) se aproximó a 0 en x = {pi}. No se puede dividir entre cero.")

        p_siguiente = pi - (f_pi / f_prime_pi)
        error_calculado = abs(p_siguiente - pi)
        iteracion += 1

        if log_callback:
            log_callback(iteracion, pi, f_pi, f_prime_pi, p_siguiente, error_calculado)

        pi = p_siguiente

    return pi, func_derivada, iteracion, error_calculado


class NewtonRaphsonWidget(QWidget):
    """Componente QWidget autónomo del Método de Newton-Raphson."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Entradas de texto
        self.funcionInput = QLineEdit()
        self.funcionInput.setPlaceholderText("Ej: x^3 - 2 o x**3 - x - 2")

        self.derivadaInput = QLineEdit()
        self.derivadaInput.setPlaceholderText("Derivada f'(x)")
        self.derivadaInput.setReadOnly(True)

        self.p0Input = QLineEdit()
        self.p0Input.setPlaceholderText("P0")

        self.errInput = QLineEdit()
        self.errInput.setPlaceholderText("Error")

        self.iteracionesInput = QLineEdit()
        self.iteracionesInput.setPlaceholderText("Max Iteraciones")

        # Botones
        self.calcularBtn = QPushButton("Calcular")
        self.calcularBtn.clicked.connect(self.calcular)

        self.limpiarBtn = QPushButton("Limpiar")
        self.limpiarBtn.clicked.connect(self.limpiar)

        self.resultadoLabel = QLabel("Resultado: ")
        self.resultadoLabel.setStyleSheet("font-weight: bold;")

        # Tabla de resultados
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Iteración", "P0", "f(P0)", "f'(P0)", "P_i+1", "Error"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Formulario
        form = QFormLayout()
        form.addRow("Ecuación f(x): ", self.funcionInput)
        form.addRow("Derivada f'(x): ", self.derivadaInput)
        form.addRow("P0: ", self.p0Input)
        form.addRow("Error: ", self.errInput)
        form.addRow("Iteraciones: ", self.iteracionesInput)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.calcularBtn)
        btnLayout.addWidget(self.limpiarBtn)

        # ======= PANEL IZQUIERDO ========
        panelIzquierdo = QWidget()
        layoutIzq = QVBoxLayout(panelIzquierdo)
        layoutIzq.addLayout(form)
        layoutIzq.addLayout(btnLayout)
        layoutIzq.addWidget(self.resultadoLabel)
        layoutIzq.addWidget(self.tabla)

        # ======= PANEL DERECHO (Gráfica Matplotlib) ========
        panelDerecho = QWidget()
        layoutDer = QVBoxLayout(panelDerecho)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        layoutDer.addWidget(self.canvas)

        # ======== SPLITTER =========
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(panelIzquierdo)
        splitter.addWidget(panelDerecho)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

    def calcular(self):
        self.tabla.setRowCount(0)

        try:
            func = parsear_funcion(self.funcionInput.text())
            p0 = float(self.p0Input.text())
            err = float(self.errInput.text())
            max_iter = int(self.iteracionesInput.text())
        except ValueError as ve:
            QMessageBox.warning(self, "Error de entrada", f"Revisa los datos:\n{ve}")
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado:\n{e}")
            return

        try:
            raiz, func_derivada, iters_realizadas, error_final = newton_raphson(
                p0, err, max_iter, func, log_callback=self.agregar_fila
            )

            self.derivadaInput.setText(str(func_derivada))
            self.resultadoLabel.setText(f"Resultado: Raíz ≈ {raiz:.6f} | Iteraciones: {iters_realizadas}")

            self.graficar(func, raiz, p0)

            QMessageBox.information(
                self,
                "Cálculo Exitoso",
                f"Proceso finalizado con éxito.\n"
                f"Raíz aproximada: {raiz:.6f}\n"
                f"Iteraciones realizadas: {iters_realizadas}\n"
                f"Error final: {error_final:.6f}"
            )

        except ValueError as ve:
            QMessageBox.critical(self, "División por Cero", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error Matemático", f"Error al evaluar la función:\n{e}")

    def agregar_fila(self, iteracion, pi, f_pi, f_prime_pi, p_siguiente, error):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        valores = [
            iteracion,
            f"{pi:.6f}",
            f"{f_pi:.6f}",
            f"{f_prime_pi:.6f}",
            f"{p_siguiente:.6f}",
            f"{error:.6f}",
        ]

        for col, valor in enumerate(valores):
            item = QTableWidgetItem(str(valor))
            item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(fila, col, item)
        self.tabla.scrollToBottom()

    def graficar(self, func, raiz, p0):
        self.ax.clear()

        margin = max(abs(raiz - p0) * 1.5, 2.0)
        x_vals = np.linspace(raiz - margin, raiz + margin, 400)
        y_vals = [evalua(func, val) for val in x_vals]

        self.ax.plot(x_vals, y_vals, label="f(x)", color="blue")
        self.ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        self.ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
        self.ax.plot(raiz, evalua(func, raiz), 'ro', label=f"Raíz ≈ {raiz:.4f}")

        self.ax.set_title("Gráfica de f(x)")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.ax.legend()
        self.ax.grid(True)

        self.canvas.draw()

    def limpiar(self):
        self.funcionInput.clear()
        self.derivadaInput.clear()
        self.p0Input.clear()
        self.errInput.clear()
        self.iteracionesInput.clear()
        self.resultadoLabel.setText("Resultado: ")
        self.tabla.setRowCount(0)
        self.ax.clear()
        self.canvas.draw()
        self.funcionInput.setFocus()


class MainWindow(QMainWindow):
    """Ventana principal que aloja el QWidget de Newton-Raphson."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicación Métodos Numéricos - Newton-Raphson")
        self.resize(1000, 600)

        # Asignar NewtonRaphsonWidget como el widget central del QMainWindow
        self.newton_widget = NewtonRaphsonWidget()
        self.setCentralWidget(self.newton_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_principal = MainWindow()
    ventana_principal.show()
    sys.exit(app.exec())