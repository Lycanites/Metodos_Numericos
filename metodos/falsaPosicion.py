from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from sympy import symbols, lambdify

from metodos.parsear_funcion import parsear_funcion

x = symbols('x')


class FalsaPosicion(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        titulo = QLabel("Método de Falsa Posición")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # ---------- Formulario de entradas ----------
        form_layout = QHBoxLayout()

        self.input_funcion = QLineEdit()
        self.input_funcion.setPlaceholderText("f(x), ej: x^3 - 2x - 5")

        self.input_a = QLineEdit()
        self.input_a.setPlaceholderText("a")

        self.input_b = QLineEdit()
        self.input_b.setPlaceholderText("b")

        self.input_tol = QLineEdit()
        self.input_tol.setPlaceholderText("Tolerancia (ej: 1e-6)")

        form_layout.addWidget(QLabel("f(x):"))
        form_layout.addWidget(self.input_funcion)
        form_layout.addWidget(QLabel("a:"))
        form_layout.addWidget(self.input_a)
        form_layout.addWidget(QLabel("b:"))
        form_layout.addWidget(self.input_b)
        form_layout.addWidget(QLabel("Tol:"))
        form_layout.addWidget(self.input_tol)

        layout.addLayout(form_layout)

        # ---------- Botón calcular ----------
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.setStyleSheet(
            "background-color: #34495e; color: white; padding: 8px; border-radius: 5px;"
        )
        self.btn_calcular.clicked.connect(self.calcular)
        layout.addWidget(self.btn_calcular)

        # ---------- Tabla de resultados ----------
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Iter", "a", "b", "xr", "f(xr)", "Error"]
        )
        layout.addWidget(self.tabla)

        # ---------- Resultado final ----------
        self.label_resultado = QLabel("")
        self.label_resultado.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.label_resultado.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_resultado)

    def calcular(self):
        self.tabla.setRowCount(0)
        self.label_resultado.setText("")

        try:
            expr = parsear_funcion(self.input_funcion.text())
            a = float(self.input_a.text())
            b = float(self.input_b.text())
            tol_texto = self.input_tol.text().strip()
            tol = float(tol_texto) if tol_texto else 1e-6
        except ValueError as e:
            QMessageBox.warning(self, "Error de entrada", str(e))
            return

        f = lambdify(x, expr, "numpy")

        try:
            fa = f(a)
            fb = f(b)
        except Exception as e:
            QMessageBox.warning(self, "Error al evaluar f(x)", str(e))
            return

        if fa == 0:
            self.label_resultado.setText(f"Raíz exacta encontrada: {a:.8f}")
            return
        if fb == 0:
            self.label_resultado.setText(f"Raíz exacta encontrada: {b:.8f}")
            return

        if fa * fb > 0:
            QMessageBox.warning(
                self, "Error",
                "f(a) y f(b) deben tener signos opuestos para aplicar el método."
            )
            return

        max_iter = 100
        raiz = None
        xr_anterior = a

        for i in range(1, max_iter + 1):
            xr = b - (fb * (a - b)) / (fa - fb)
            fxr = f(xr)
            error = abs(xr - xr_anterior)

            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(i)))
            self.tabla.setItem(fila, 1, QTableWidgetItem(f"{a:.8f}"))
            self.tabla.setItem(fila, 2, QTableWidgetItem(f"{b:.8f}"))
            self.tabla.setItem(fila, 3, QTableWidgetItem(f"{xr:.8f}"))
            self.tabla.setItem(fila, 4, QTableWidgetItem(f"{fxr:.8g}"))
            self.tabla.setItem(fila, 5, QTableWidgetItem(f"{error:.8g}"))

            if abs(fxr) < tol or error < tol:
                raiz = xr
                break

            if fa * fxr < 0:
                b, fb = xr, fxr
            else:
                a, fa = xr, fxr

            xr_anterior = xr

        if raiz is not None:
            self.label_resultado.setText(f"Raíz aproximada: {raiz:.8f}")
        else:
            self.label_resultado.setText(
                f"El método no convergió después de {max_iter} iteraciones."
            )