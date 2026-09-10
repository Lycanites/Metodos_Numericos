from sympy import symbols, sympify
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

x = symbols('x')

transformaciones = standard_transformations + (
    implicit_multiplication_application,  # permite "2x" en vez de "2*x"
    convert_xor,                          # permite "^" en vez de "**"
)

def parsear_funcion(texto):
    """
    Convierte un string ingresado por el usuario en una expresión sympy en x.
    Lanza ValueError con mensaje claro si el input es inválido.
    """
    texto = texto.strip()
    if not texto:
        raise ValueError("La función no puede estar vacía.")

    try:
        expr = parse_expr(texto, local_dict={"x": x}, transformations=transformaciones)
    except Exception as e:
        raise ValueError(f"No se pudo interpretar la función: {e}")

    # Verificar que la expresión solo dependa de x (o sea constante)
    simbolos_extra = expr.free_symbols - {x}
    if simbolos_extra:
        raise ValueError(
            f"La función solo debe depender de x. Símbolo(s) no reconocido(s): "
            f"{', '.join(str(s) for s in simbolos_extra)}"
        )

    return expr

def puntoMedio(a, b):
    return (a + b) / 2

def evalua(func, valor_x):
    return float(func.subs(x, valor_x))

def nuevoIntervalo(a, b, func):
    m = puntoMedio(a, b)
    if evalua(func, a) * evalua(func, m)<0:
        return a, m
    else:
        return m, b
    
def funcion():
    print("escribe la funcion a calcular f(x): ")
    return sympify(input())
    
def calcError(a, b):
    return abs(b - a) / 2

def biseccion(a, b, func, err, log_callback=None, max_iter = 1000):
    
    error = 100
    iteracion = 0
    fx_texto = str(func)

    while error > err and iteracion < max_iter:
        
        m = puntoMedio(a, b)

        fa = evalua(func, a)
        fb = evalua(func, b)
        fm = evalua(func, m)

        # Actualizamos el intervalo
        if fa * fm < 0:
            b = m
        else:
            a = m

        # Calculamos error
        error = calcError(a, b)

        iteracion += 1
        
        if log_callback:
            log_callback(iteracion, fx_texto, a, b, m, fa, fb, fm, error)
        else:
            print(
                f"Iteración: {iteracion} | a: {a} | b: {b} | "
                f"m: {m} | fa: {fa} | fb: {fb} | fm: {fm} | Error: {error}"
            )

    return m

    


class Biseccion(QWidget):
    def __init__(self):
        super().__init__()
        
        self.resize(500, 500)
        
        
        self.funcionInput = QLineEdit()
        self.funcionInput.setPlaceholderText("Ej: x**3 - x - 2")
        
        self.aInput = QLineEdit()
        self.aInput.setPlaceholderText("a")
        
        self.bInput = QLineEdit()
        self.bInput.setPlaceholderText("b")
        
        self.errInput = QLineEdit()
        self.errInput.setPlaceholderText("err")
        
        self.calcularBtn = QPushButton("Calcular aproximaciones")
        self.calcularBtn.clicked.connect(self.calcular)
        
        self.resultadoLabel = QLabel("Resultado: ")
                
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["Iteración", "f(x)", "a", "b", "m", "f(m)", "Error"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        form = QFormLayout()
        form.addRow("f(x): ", self.funcionInput)
        form.addRow("a: ", self.aInput)
        form.addRow("b: ", self.bInput)
        form.addRow("Error", self.errInput)
        
        # ======= PANEL IZQUIERDO ========
        panelIzquierdo =QWidget()
        layoutIzq = QVBoxLayout(panelIzquierdo)
        layoutIzq.addLayout(form)
        layoutIzq.addWidget(self.calcularBtn)
        layoutIzq.addWidget(self.resultadoLabel)
        layoutIzq.addWidget(self.tabla)
        
        # ======= PANEL DERECHO ========
        
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
        splitter.setStretchFactor(0,1)
        splitter.setStretchFactor(1,2)
        
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        # layout.addWidget(self.calcularBtn)
        # layout.addWidget(self.resultadoLabel)
        # layout.addWidget(self.logArea)
        
        self.setLayout(layout)
        
    def calcular(self):
        try:
            func = parsear_funcion(self.funcionInput.text())
            a = float(self.aInput.text())
            b = float(self.bInput.text())
            err = float(self.errInput.text())
        except Exception as e:
            QMessageBox.warning(self, "Error de entrada", f"Revisa los datos: \n{e}")
            return
        if evalua(func, a) * evalua(func, b)>=0:
            QMessageBox.warning(self, "Error", "f(a) y f(b) deben tener signos opuestos.")
            return
        
        resultado = biseccion(a, b, func, err, log_callback=self.agregar_fila)
        # self.resultadoLabel.setText(f"Resultado: {resultado: .7f}")
        
    def agregar_fila(self, iteracion, fx, a, b, m, fa, fb, fm, error):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        valores = [
            iteracion,
            fx,
            f"{a: .7f}",
            f"{b: .7f}",
            f"{m: .7f}",
            f"{fa: .7f}",
            f"{fb: .7f}",
            f"{fm: .7f}",
            f"{error: .7f}",
        ]
        
        for col, valor in enumerate(valores):
            item = QTableWidgetItem(str(valor))
            item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(fila, col, item)
        self.tabla.scrollToBottom()
    
