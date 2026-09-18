from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QEvent
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from metodos.biseccion import Biseccion
from metodos.secante import Secante
from metodos.falsaPosicion import FalsaPosicion
from metodos.puntoFijo import PuntoFijo
from metodos.newtonRaphson import FrmNewtonRaphson
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metodos Numericos")
        self.resize(800, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------- NAVBAR ----------
        self.navbar = QWidget()
        self.navbar.setStyleSheet("background-color: #2b2b3d;")
        self.navbar.setMinimumWidth(180)
        self.navbar.setMaximumWidth(180)
        self.navbar.setMouseTracking(True)
        self.navbar.installEventFilter(self)

        # Estado de la navbar
        self._navbar_colapsada = False
        self._expandido_por_hover = False

        nav_layout = QVBoxLayout(self.navbar)
        nav_layout.setContentsMargins(10, 20, 10, 10)
        nav_layout.setSpacing(10)
        nav_layout.setAlignment(Qt.AlignTop)

        combo_style = """
            QComboBox {
                color: white;
                background-color: #34495e;
                padding: 8px;
                border-radius: 5px;
                font-size: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b3d;
                color: white;
                selection-background-color: #44475a;
            }
        """
        label_style = "color: #9aa0b3; font-size: 12px; font-weight: bold; margin-top: 6px;"

        btn_style = """
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                padding: 10px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #44475a;
                border-radius: 5px;
            }
        """

        # Botón de menú (toggle) - icono de tres rayas (hamburguesa)
        self.btn_menu = QPushButton("☰")
        self.btn_menu.setStyleSheet(
            "background-color: #34495e; color: white; border: none; padding: 8px; font-size: 18px;"
        )
        self.btn_menu.clicked.connect(self.alternar_navbar)
        nav_layout.addWidget(self.btn_menu)

        # ---------- STACK DE PÁGINAS ----------
        self.stack = QStackedWidget()

        self.page_home = self.crear_pagina("Metodos Numericos")
        self.page_Biseccion = Biseccion()
        self.page_Secante = Secante()
        self.page_FalsaPosicion = FalsaPosicion()
        self.page_PuntoFijo = PuntoFijo()
        self.page_NewtonRaphson = FrmNewtonRaphson()
        self.page_Steffensen = self.crear_pagina("Steffensen")
        self.page_Muller = self.crear_pagina("Müller")
        self.page_Bairstow = self.crear_pagina("Bairstow")
        self.page_Aitken = self.crear_pagina("Aitken")
        self.page_Deflacion = self.crear_pagina("Deflacion")
        self.page_Horner = self.crear_pagina("Horner")

        # NOTA: las claves de este diccionario deben coincidir EXACTAMENTE
        # (incluyendo acentos) con los textos que se agregan a los QComboBox.
        self.paginas = {
            "Inicio": self.page_home,
            "Biseccion": self.page_Biseccion,
            "Secante": self.page_Secante,
            "Falsa Posición": self.page_FalsaPosicion,  # <- corregido (antes "Falsa Posicion")
            "Punto fijo": self.page_PuntoFijo,
            "Newton-Raphson": self.page_NewtonRaphson,
            "Steffensen": self.page_Steffensen,
            "Muller": self.page_Muller,
            "Bairstow": self.page_Bairstow,
            "Aitken": self.page_Aitken,
            "Deflacion": self.page_Deflacion,
            "Horner": self.page_Horner
        }

        self.indice_por_nombre = {}
        for nombre, pagina in self.paginas.items():
            indice = self.stack.addWidget(pagina)
            self.indice_por_nombre[nombre] = indice

        lbl_abiertos = QLabel("Metodos Abiertos")
        lbl_abiertos.setStyleSheet(label_style)
        self.metodosAbiertos = QComboBox()
        self.metodosAbiertos.addItems([
            "",
            "Secante",
            "Punto fijo",
            "Newton-Raphson",
            "Steffensen",
            "Muller",
        ])
        self.metodosAbiertos.setStyleSheet(combo_style)

        lbl_cerrados = QLabel("Metodos Cerrados")
        lbl_cerrados.setStyleSheet(label_style)
        self.metodosCerrados = QComboBox()
        self.metodosCerrados.addItems([
            "",
            "Biseccion",
            "Falsa Posición",
        ])
        self.metodosCerrados.setStyleSheet(combo_style)

        lbl_raicesDePolinomios = QLabel("Raices De Polinomios")
        lbl_raicesDePolinomios.setStyleSheet(label_style)
        self.raicesDePolinomios = QComboBox()
        self.raicesDePolinomios.addItems([
            "",
            "Aitken",
            "Deflacion",
            "Horner"
        ])
        self.raicesDePolinomios.setStyleSheet(combo_style)

        self.metodosCerrados.currentTextChanged.connect(
            lambda texto: self.ir_a_pagina(texto, origen="cerrados")
        )
        self.metodosAbiertos.currentTextChanged.connect(
            lambda texto: self.ir_a_pagina(texto, origen="abiertos")
        )
        self.raicesDePolinomios.currentTextChanged.connect(
            lambda texto: self.ir_a_pagina(texto, origen="raices")
        )

        # En esta area se configura el orden en el que se visualiza en la pantalla del usuario
        self.btn_home = QPushButton("Inicio")
        self.btn_home.setStyleSheet(btn_style)
        self.btn_home.clicked.connect(lambda: self.ir_a_pagina("Inicio", origen=None))

        nav_layout.addWidget(self.btn_home)
        nav_layout.addWidget(lbl_cerrados)
        nav_layout.addWidget(self.metodosCerrados)
        nav_layout.addWidget(lbl_abiertos)
        nav_layout.addWidget(self.metodosAbiertos)
        nav_layout.addWidget(lbl_raicesDePolinomios)
        nav_layout.addWidget(self.raicesDePolinomios)

        # Agregar navbar y stack al layout principal
        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.stack)

    def ir_a_pagina(self, nombre, origen=None):
        if not nombre:
            return

        indice = self.indice_por_nombre.get(nombre)
        if indice is None:
            return

        self._pagina_actual = nombre
        self.stack.setCurrentIndex(indice)

        # Limpia los combos que no originaron el cambio
        combos = {
            "cerrados": self.metodosCerrados,
            "abiertos": self.metodosAbiertos,
            "raices": self.raicesDePolinomios,
        }
        for clave, combo in combos.items():
            if clave != origen:
                combo.blockSignals(True)
                combo.setCurrentIndex(0)
                combo.blockSignals(False)

    def crear_pagina(self, texto):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        label = QLabel(texto)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 22px;")
        layout.addWidget(label)
        return pagina

    # ---------- Colapsar / expandir manual ----------
    def alternar_navbar(self):
        current_width = self.navbar.maximumWidth()
        colapsando = current_width != 60
        target_width = 60 if colapsando else 180

        self._navbar_colapsada = colapsando
        self._expandido_por_hover = False
        self._animar_navbar(target_width)

    # ---------- Hover: expandir/colapsar temporalmente ----------
    def eventFilter(self, obj, event):
        if obj is self.navbar:
            if event.type() == QEvent.Enter:
                self.expandir_por_hover()
            elif event.type() == QEvent.Leave:
                self.colapsar_por_hover()
        return super().eventFilter(obj, event)

    def expandir_por_hover(self):
        # Solo expande por hover si el usuario la dejó colapsada manualmente
        if self._navbar_colapsada and self.navbar.maximumWidth() == 60:
            self._expandido_por_hover = True
            self._animar_navbar(180)

    def colapsar_por_hover(self):
        if self._expandido_por_hover:
            self._expandido_por_hover = False
            self._animar_navbar(60)

    def _animar_navbar(self, target_width):
        current_width = self.navbar.width()

        self.anim_min = QPropertyAnimation(self.navbar, b"minimumWidth")
        self.anim_min.setDuration(300)
        self.anim_min.setStartValue(current_width)
        self.anim_min.setEndValue(target_width)
        self.anim_min.setEasingCurve(QEasingCurve.InOutQuad)

        self.anim_max = QPropertyAnimation(self.navbar, b"maximumWidth")
        self.anim_max.setDuration(300)
        self.anim_max.setStartValue(current_width)
        self.anim_max.setEndValue(target_width)
        self.anim_max.setEasingCurve(QEasingCurve.InOutQuad)

        self.anim_min.start()
        self.anim_max.start()


def main():
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()