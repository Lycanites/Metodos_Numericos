from sympy import symbols, sympify
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
from PySide6.QtWidgets import *

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

def biseccion(a, b, func, err, log_callback=None):
    
    error = 100
    iteracion = 0

    while error > err:
        
        m = puntoMedio(a, b)

        fa = evalua(func, a)
        fm = evalua(func, m)

        # Actualizamos el intervalo
        if fa * fm < 0:
            b = m
        else:
            a = m

        # Calculamos error
        error = calcError(a, b)

        iteracion += 1

        linea = (
            f"Iteración: {iteracion} | "
            f"a: {a} | "
            f"b: {b} | "
            f"m: {m} | "
            f"Error: {error}"
        )

        if log_callback:
            log_callback(linea)
        else:
            print(linea)

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
        
        self.calcularBtn = QPushButton("Calcular")
        self.calcularBtn.clicked.connect(self.calcular)
        
        self.resultadoLabel = QLabel("Resultado: ")
        
        self.logArea = QTextEdit()
        self.logArea.setReadOnly(True)
        
        form = QFormLayout()
        form.addRow("f(x): ", self.funcionInput)
        form.addRow("a: ", self.aInput)
        form.addRow("b: ", self.bInput)
        form.addRow("Error", self.errInput)
        
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.calcularBtn)
        layout.addWidget(self.resultadoLabel)
        layout.addWidget(self.logArea)
        
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
        self.logArea.clear()
        resultado = biseccion(a, b, func, err, log_callback  = self.logArea.append)
        self.resultadoLabel.setText(f"Resultado: {resultado: .7f}")
    
