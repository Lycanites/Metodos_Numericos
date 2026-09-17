from PySide6.QtCore import QPropertyAnimation, QEasingCurve
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
        
        style = self.style()
        self.icono_colapsar = style.standardIcon(QStyle.SP_ArrowLeft)
        self.icono_expandir = style.standardIcon(QStyle.SP_ArrowRight)

        # Botón de menú (toggle)
        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(self.icono_colapsar)
        self.btn_menu.setStyleSheet(
            "background-color: #34495e; color: white; border: none; padding: 8px;"
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

        self.paginas = {
            "Inicio": self.page_home,
            "Biseccion":self.page_Biseccion,
            "Secante":self.page_Secante,
            "Falsa Posicion":self.page_FalsaPosicion,
            "Punto fijo":self.page_PuntoFijo,
            "Newton-Raphson":self.page_NewtonRaphson,
            "Steffensen":self.page_Steffensen,
            "Muller":self.page_Muller,
            "Bairstow":self.page_Bairstow,
            "Aitken":self.page_Aitken,
            "Deflacion":self.page_Deflacion,
            "Horner":self.page_Horner
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
            "Aitken",
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
            "Bairstow",
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
        self.btn_home.clicked.connect(lambda: self.ir_a_pagina("Inicio", origen=None)) # <- Conexión faltante

        self.btn_home.setStyleSheet(btn_style)
        
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
        
        #Quita los combos que no originaron el cambio
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

    def alternar_navbar(self):
        current_width = self.navbar.width()

        min_width = 60
        max_width = 180
        
        colapsando = current_width == max_width
        target_width = min_width if colapsando else max_width
        
        self.btn_menu.setIcon(
            self.icono_expandir if colapsando else self.icono_colapsar
        )

        # ======= Animación =======
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