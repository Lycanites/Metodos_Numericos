# metodos/secante.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from sympy import symbols, lambdify

from metodos.parsear_funcion import parsear_funcion

x = symbols('x')


class Secante(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        titulo = QLabel("Método de la Secante")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # ---------- Formulario de entradas ----------
        form_layout = QHBoxLayout()

        self.input_funcion = QLineEdit()
        self.input_funcion.setPlaceholderText("f(x), ej: x^3 - 2x - 5")

        self.input_x0 = QLineEdit()
        self.input_x0.setPlaceholderText("x0")

        self.input_x1 = QLineEdit()
        self.input_x1.setPlaceholderText("x1")

        self.input_tol = QLineEdit()
        self.input_tol.setPlaceholderText("Tolerancia (ej: 1e-6)")

        form_layout.addWidget(QLabel("f(x):"))
        form_layout.addWidget(self.input_funcion)
        form_layout.addWidget(QLabel("x0:"))
        form_layout.addWidget(self.input_x0)
        form_layout.addWidget(QLabel("x1:"))
        form_layout.addWidget(self.input_x1)
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
            ["Iter", "x0", "x1", "x2", "f(x2)", "Error"]
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
            x0 = float(self.input_x0.text())
            x1 = float(self.input_x1.text())
            tol_texto = self.input_tol.text().strip()
            tol = float(tol_texto) if tol_texto else 1e-6
        except ValueError as e:
            QMessageBox.warning(self, "Error de entrada", str(e))
            return

        f = lambdify(x, expr, "numpy")

        try:
            f0 = f(x0)
            f1 = f(x1)
        except Exception as e:
            QMessageBox.warning(self, "Error al evaluar f(x)", str(e))
            return

        if f1 - f0 == 0:
            QMessageBox.warning(
                self, "Error",
                "f(x1) - f(x0) = 0, no se puede continuar con el método de la secante."
            )
            return

        max_iter = 100
        raiz = None

        for i in range(1, max_iter + 1):
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
            f2 = f(x2)
            error = abs(x2 - x1)

            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(i)))
            self.tabla.setItem(fila, 1, QTableWidgetItem(f"{x0:.8f}"))
            self.tabla.setItem(fila, 2, QTableWidgetItem(f"{x1:.8f}"))
            self.tabla.setItem(fila, 3, QTableWidgetItem(f"{x2:.8f}"))
            self.tabla.setItem(fila, 4, QTableWidgetItem(f"{f2:.8g}"))
            self.tabla.setItem(fila, 5, QTableWidgetItem(f"{error:.8g}"))

            if error < tol or abs(f2) < tol:
                raiz = x2
                break

            x0, f0 = x1, f1
            x1, f1 = x2, f2

            if f1 - f0 == 0:
                QMessageBox.warning(
                    self, "Error",
                    "f(x1) - f(x0) = 0 en una iteración posterior, no se puede continuar."
                )
                return

        if raiz is not None:
            self.label_resultado.setText(f"Raíz aproximada: {raiz:.8f}")
        else:
            self.label_resultado.setText(
                f"El método no convergió después de {max_iter} iteraciones."
            )