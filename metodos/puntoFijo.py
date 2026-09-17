from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from sympy import symbols, lambdify

from metodos.parsear_funcion import parsear_funcion

x = symbols('x')


class PuntoFijo(QWidget):
    """
    Método de punto fijo: encuentra la raíz de f(x) = 0 reescribiéndola
    como x = g(x). El usuario debe ingresar directamente g(x).
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        titulo = QLabel("Método de Punto Fijo")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # ---------- Formulario de entradas ----------
        form_layout = QHBoxLayout()

        self.input_funcion = QLineEdit()
        self.input_funcion.setPlaceholderText("g(x), ej: sqrt(2x + 5)")

        self.input_x0 = QLineEdit()
        self.input_x0.setPlaceholderText("x0")

        self.input_tol = QLineEdit()
        self.input_tol.setPlaceholderText("Tolerancia (ej: 1e-6)")

        form_layout.addWidget(QLabel("g(x):"))
        form_layout.addWidget(self.input_funcion)
        form_layout.addWidget(QLabel("x0:"))
        form_layout.addWidget(self.input_x0)
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
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(
            ["Iter", "x0", "x1 = g(x0)", "Error"]
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
            tol_texto = self.input_tol.text().strip()
            tol = float(tol_texto) if tol_texto else 1e-6
        except ValueError as e:
            QMessageBox.warning(self, "Error de entrada", str(e))
            return

        g = lambdify(x, expr, "numpy")

        max_iter = 100
        raiz = None

        for i in range(1, max_iter + 1):
            try:
                x1 = g(x0)
            except Exception as e:
                QMessageBox.warning(self, "Error al evaluar g(x)", str(e))
                return

            if isinstance(x1, complex):
                QMessageBox.warning(
                    self, "Error",
                    "g(x) produjo un valor complejo; el método diverge con este x0."
                )
                return

            error = abs(x1 - x0)

            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(i)))
            self.tabla.setItem(fila, 1, QTableWidgetItem(f"{x0:.8f}"))
            self.tabla.setItem(fila, 2, QTableWidgetItem(f"{x1:.8f}"))
            self.tabla.setItem(fila, 3, QTableWidgetItem(f"{error:.8g}"))

            if error < tol:
                raiz = x1
                break

            if abs(x1) > 1e15:
                QMessageBox.warning(
                    self, "Error",
                    "El método está divergiendo (valores demasiado grandes)."
                )
                return

            x0 = x1

        if raiz is not None:
            self.label_resultado.setText(f"Raíz aproximada: {raiz:.8f}")
        else:
            self.label_resultado.setText(
                f"El método no convergió después de {max_iter} iteraciones."
            )