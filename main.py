from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from biseccion import *
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metodos Numericos")
        self.resize(800, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        
        navbar = QWidget()
        navbar.setFixedWidth(180)
        navbar.setStyleSheet("background-color: #2b2b3d;")
        nav_layout = QVBoxLayout(navbar)
        nav_layout.setContentsMargins(10, 20, 10, 10)
        nav_layout.setSpacing(10)
        nav_layout.setAlignment(Qt.AlignTop)
        
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
        
        self.btn_home = QPushButton("Inicio")
        self.btn_Biseccion = QPushButton("Biseccion")
        self.btn_Secante = QPushButton("Secante")
        self.btn_FalsaPosicion = QPushButton("Falsa Posición")
        self.btn_PuntoFijo = QPushButton("Punto fijo")
        self.btn_NewtonRaphson = QPushButton("Newton-Raphson")
        self.btn_ValorIntermedio = QPushButton("Valor intermedio")
        self.btn_Steffensen  = QPushButton("Steffensent")
        
        
        for btn in (self.btn_home, self.btn_Biseccion, self.btn_Secante, self.btn_FalsaPosicion, self.btn_PuntoFijo, self.btn_ValorIntermedio, self.btn_NewtonRaphson, self.btn_Steffensen):
            btn.setStyleSheet(btn_style)
            nav_layout.addWidget(btn)

        # ---------- STACK DE PÁGINAS ----------
        self.stack = QStackedWidget()

        self.page_home = self.crear_pagina("Página de Inicio")
        self.page_Biseccion = self.crear_pagina("Biseccion")
        self.page_Secante = self.crear_pagina("Secante")
        self.page_FalsaPosicion = self.crear_pagina("Falsa Posición")
        self.page_PuntoFijo = self.crear_pagina("Punto Fijo")
        self.page_ValorIntermedio = self.crear_pagina("Valor Intermedio")
        self.page_NewtonRaphson = self.crear_pagina("Newton-Raphson")
        self.page_Steffensen = self.crear_pagina("Steffensen")

        self.stack.addWidget(self.page_home)      # index 0
        self.stack.addWidget(self.page_Biseccion)   # index 1
        self.stack.addWidget(self.page_Secante)  # index 2
        self.stack.addWidget(self.page_FalsaPosicion)
        self.stack.addWidget(self.page_PuntoFijo)
        self.stack.addWidget(self.page_ValorIntermedio)
        self.stack.addWidget(self.page_NewtonRaphson)
        self.stack.addWidget(self.page_Steffensen)

        # ---------- Conectar botones con páginas ----------
        self.btn_home.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_Biseccion.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_Secante.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_FalsaPosicion.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.btn_PuntoFijo.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.btn_ValorIntermedio.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.btn_NewtonRaphson.clicked.connect(lambda: self.stack.setCurrentIndex(6))
        self.btn_Steffensen.clicked.connect(lambda: self.stack.setCurrentIndex(7))

        # Agregar navbar y stack al layout principal
        main_layout.addWidget(navbar)
        main_layout.addWidget(self.stack)

    def crear_pagina(self, texto):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        label = QLabel(texto)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 22px;")
        layout.addWidget(label)
        return pagina

def main():
    
    app = QApplication(sys.argv)
    ventana = MainWindow()    
    ventana.show()
    sys.exit(app.exec())
    
    
    
    # opc = 0
    # while opc != 10:
    #     match opc:
    #         case 1:
    #                 a = float(input("Ingrese el valor de a: "))
    #                 b = float(input("Ingrese el valor de b: "))
    #                 err = float(input("Ingrese el error deseado: "))

    #                 func = funcion()

    #                 raiz = biseccion(a, b, func, err)

    #                 print(f"\nRaíz aproximada: {raiz}")
    #         case 2:
    #             print("Aca va la Secante")
    #         case _:
    #             print("Error, ingrese un argumento valido")


    
    
if __name__ == "__main__":
    main()
    
