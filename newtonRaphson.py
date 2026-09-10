import sys
import sympy as sp
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt

class FrmNewtonRaphson(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Newton-Raphson")
        self.resize(800, 600)

        # Widget principal y Layout
        main_widget = QWidget()
        # self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # Título
        lbl_titulo = QLabel("Newton-Raphson")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(lbl_titulo)

        # Formulario de entradas
        grid_layout = QGridLayout()

        lbl_ecuacion = QLabel("Ecuación:")
        lbl_ecuacion.setStyleSheet("font-size: 14px;")
        self.txt_ecuacion = QLineEdit()
        self.txt_ecuacion.setStyleSheet("font-size: 14px;")

        lbl_derivada = QLabel("Derivada:")
        lbl_derivada.setStyleSheet("font-size: 14px;")
        self.txt_derivada = QLineEdit()
        self.txt_derivada.setStyleSheet("font-size: 14px;")
        self.txt_derivada.setReadOnly(True)  # Campo solo lectura para la derivada generada

        grid_layout.addWidget(lbl_ecuacion, 0, 0)
        grid_layout.addWidget(self.txt_ecuacion, 0, 1, 1, 5)
        grid_layout.addWidget(lbl_derivada, 1, 0)
        grid_layout.addWidget(self.txt_derivada, 1, 1, 1, 5)

        lbl_p0 = QLabel("P0:")
        lbl_p0.setStyleSheet("font-size: 14px;")
        self.txt_p0 = QLineEdit()
        self.txt_p0.setStyleSheet("font-size: 14px;")

        lbl_error = QLabel("Error:")
        lbl_error.setStyleSheet("font-size: 14px;")
        self.txt_error = QLineEdit()
        self.txt_error.setStyleSheet("font-size: 14px;")

        lbl_iteraciones = QLabel("Iteraciones:")
        lbl_iteraciones.setStyleSheet("font-size: 14px;")
        self.txt_iteraciones = QLineEdit()
        self.txt_iteraciones.setStyleSheet("font-size: 14px;")

        grid_layout.addWidget(lbl_p0, 2, 0)
        grid_layout.addWidget(self.txt_p0, 2, 1)
        grid_layout.addWidget(lbl_error, 2, 2)
        grid_layout.addWidget(self.txt_error, 2, 3)
        grid_layout.addWidget(lbl_iteraciones, 2, 4)
        grid_layout.addWidget(self.txt_iteraciones, 2, 5)

        layout.addLayout(grid_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.setStyleSheet("font-size: 16px; padding: 6px 15px;")
        self.btn_calcular.clicked.connect(self.btn_calcular_action)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setStyleSheet("font-size: 16px; padding: 6px 15px;")
        self.btn_limpiar.clicked.connect(self.btn_limpiar_action)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_calcular)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(self.btn_limpiar)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Tabla de resultados
        self.tbl_tabla = QTableWidget()
        self.tbl_tabla.setColumnCount(6)
        self.tbl_tabla.setHorizontalHeaderLabels([
            "Iteración", "P0", "f(P0)", "f'(P0)", "P_i+1", "Error"
        ])
        self.tbl_tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tbl_tabla)

        main_widget.setLayout(layout)

        # Centrar la ventana en la pantalla
        self.center_on_screen()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def btn_calcular_action(self):
        try:
            # 1. Lectura de la ecuación de entrada
            ecuacion_text = self.txt_ecuacion.text().strip()

            if not ecuacion_text:
                QMessageBox.warning(
                    self, "Campo Vacío", "Por favor, ingrese la función f(x)."
                )
                return

            p0 = float(self.txt_p0.text().strip())
            error_deseado = float(self.txt_error.text().strip())
            max_iter = int(self.txt_iteraciones.text().strip())

            # 2. Parseo de la expresión matemática y cálculo de derivada simbólica
            x = sp.Symbol('x')
            # Permite interpretar sintaxis común como ^ para potencias
            expr_format = ecuacion_text.replace('^', '**')
            f_expr = sp.sympify(expr_format)
            f_prime_expr = sp.diff(f_expr, x)

            # Mostrar la derivada en pantalla
            self.txt_derivada.setText(str(f_prime_expr).replace('**', '^'))

            # Convertir las expresiones a funciones numéricas rápidas
            f = sp.lambdify(x, f_expr, 'math')
            f_prime = sp.lambdify(x, f_prime_expr, 'math')

            # 3. Limpiar tabla
            self.tbl_tabla.setRowCount(0)

            pi = p0
            p_siguiente = 0.0
            error_calculado = float('inf')
            iteracion = 1

            # 4. Bucle principal de Newton-Raphson
            while error_calculado > error_deseado and iteracion <= max_iter:
                f_pi = float(f(pi))
                f_prime_pi = float(f_prime(pi))

                # Validar división entre cero
                if abs(f_prime_pi) < 1e-12:
                    QMessageBox.critical(
                        self, 
                        "División por Cero", 
                        f"Error: La derivada f'(x) se aproximó a 0 en x = {pi}.\nNo se puede dividir entre cero."
                    )
                    return

                # Aplicar la fórmula: P_{i+1} = P_i - ( f(P_i) / f'(P_i) )
                p_siguiente = pi - (f_pi / f_prime_pi)
                error_calculado = abs(p_siguiente - pi)

                # Agregar fila a la tabla
                row_position = self.tbl_tabla.rowCount()
                self.tbl_tabla.insertRow(row_position)

                datos_fila = [
                    str(iteracion),
                    f"{pi:.6f}",
                    f"{f_pi:.6f}",
                    f"{f_prime_pi:.6f}",
                    f"{p_siguiente:.6f}",
                    f"{error_calculado:.6f}"
                ]

                for col, val in enumerate(datos_fila):
                    item = QTableWidgetCellItem = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_tabla.setItem(row_position, col, item)

                pi = p_siguiente
                iteracion += 1

            # 5. Mensaje con el resultado final
            QMessageBox.information(
                self,
                "Cálculo Exitoso",
                f"Proceso finalizado con éxito.\n"
                f"Raíz aproximada: {p_siguiente:.6f}\n"
                f"Iteraciones realizadas: {iteracion - 1}\n"
                f"Error final: {error_calculado:.6f}"
            )

        except ValueError:
            QMessageBox.critical(
                self,
                "Error de Entrada",
                "Por favor, ingrese valores numéricos válidos en P0, Error e Iteraciones."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Matemático",
                "Error al evaluar las expresiones. Verifique la sintaxis de f(x) (ejemplo: x^3 - 2)."
            )

    def btn_limpiar_action(self):
        self.txt_ecuacion.clear()
        self.txt_derivada.clear()
        self.txt_p0.clear()
        self.txt_error.clear()
        self.txt_iteraciones.clear()
        self.tbl_tabla.setRowCount(0)
        self.txt_ecuacion.setFocus()


