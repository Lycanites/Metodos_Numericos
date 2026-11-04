"""
Base común para las pantallas de métodos numéricos.

Cada método hereda de MetodoBase, declara sus CAMPOS y COLUMNAS
y escribe solamente ejecutar(). La base se encarga del formulario,
los botones, la tabla, la gráfica, la lectura de datos y los errores.
"""
import traceback

import numpy as np
import sympy as sp
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSplitter, QMessageBox
)

from metodos.parsear_funcion import parsear_funcion
from metodos.graficador import Graficador

x = sp.symbols("x")
_REQUERIDO = object()


class ErrorMetodo(Exception):
    """Error esperado (datos inválidos, división entre cero…): se muestra al usuario."""


# ---------------------------------------------------------------------
#  Utilidades de formato
# ---------------------------------------------------------------------
_SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def sub(n):
    return str(n).translate(_SUB)


def fmt(v, dec=8):
    """Formatea números para tablas y resultados."""
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, (bool, np.bool_)):
        return str(v)
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, complex) or np.iscomplexobj(v):
        v = complex(v)
        if abs(v.imag) < 1e-12 * max(1.0, abs(v.real)):
            return fmt(v.real, dec)
        signo = "+" if v.imag >= 0 else "−"
        return f"{fmt(v.real, dec)} {signo} {fmt(abs(v.imag), dec)}i"
    v = float(v)
    if v == 0:
        return "0"
    if not np.isfinite(v):
        return str(v)
    if 1e-4 <= abs(v) < 1e7:
        return f"{v:.{dec}f}".rstrip("0").rstrip(".")
    return f"{v:.{dec - 2}e}"


def poli_texto(coefs):
    """[a_n, …, a_0] → 'a_n x^n + … + a_0'."""
    n = len(coefs) - 1
    partes = []
    for i, c in enumerate(coefs):
        p = n - i
        if abs(c) < 1e-14:
            continue
        signo = "−" if c < 0 else "+"
        mag = abs(c)
        if p == 0:
            termino = fmt(mag)
        else:
            coef = "" if abs(mag - 1) < 1e-14 else fmt(mag)
            termino = coef + ("x" if p == 1 else f"x^{p}")
        partes.append((signo, termino))
    if not partes:
        return "0"
    texto = ("−" if partes[0][0] == "−" else "") + partes[0][1]
    for signo, termino in partes[1:]:
        texto += f" {signo} {termino}"
    return texto


def factor_texto(xi):
    """(x − xi) bien escrito para xi negativo o cero."""
    if xi == 0:
        return "x"
    return f"(x − {fmt(xi)})" if xi > 0 else f"(x + {fmt(-xi)})"


def horner(coefs, x0):
    """División sintética. Devuelve [b_n, …, b_0]; b_0 = P(x0) y el resto es Q(x)."""
    b = [coefs[0]]
    for a in coefs[1:]:
        b.append(a + b[-1] * x0)
    return b


def envolver_real(f, nombre="f"):
    """Envuelve una función de lambdify para que devuelva float o lance ErrorMetodo."""
    def g(v):
        with np.errstate(all="ignore"):
            y = f(v)
        if isinstance(y, complex) or np.iscomplexobj(y):
            if abs(np.imag(y)) > 1e-12:
                raise ErrorMetodo(f"{nombre}({fmt(v)}) no es un número real.")
            y = np.real(y)
        y = float(y)
        if not np.isfinite(y):
            raise ErrorMetodo(f"{nombre}({fmt(v)}) no está definida (resultado: {y}).")
        return y
    return g


# ---------------------------------------------------------------------
#  Estilo de las páginas
# ---------------------------------------------------------------------
ESTILO_PAGINA = """
QLabel#descMetodo { color: #5d6180; font-size: 13px; }
QLabel#etiquetaCampo { color: #33385a; font-size: 12px; font-weight: 600; }
QLineEdit#campo {
    background: #ffffff; border: 1px solid #d5d8e4; border-radius: 6px;
    padding: 6px 8px; font-size: 13px; color: #1e2030;
}
QLineEdit#campo:hover { border: 1px solid #aab3ff; }
QLineEdit#campo:focus { border: 1px solid #7c8cff; }
QPushButton#btnPrimario {
    background-color: #4f5bd5; color: #ffffff; border: none; border-radius: 6px;
    padding: 8px 20px; font-size: 13px; font-weight: 600;
}
QPushButton#btnPrimario:hover { background-color: #6270f0; }
QPushButton#btnPrimario:pressed { background-color: #3f4ab8; }
QPushButton#btnSecundario {
    background: transparent; color: #4f5bd5; border: 1px solid #c9cdf5;
    border-radius: 6px; padding: 8px 14px; font-size: 13px;
}
QPushButton#btnSecundario:hover { background-color: #eef0ff; }
QLabel#resultado {
    background-color: #eef0ff; color: #1e2030; border-left: 4px solid #7c8cff;
    border-radius: 4px; padding: 10px 12px; font-size: 14px;
}
QTableWidget#tablaMetodo {
    background: #ffffff; alternate-background-color: #f7f8fc;
    border: 1px solid #e3e5ee; border-radius: 6px; gridline-color: #eceef5;
    font-size: 12px; color: #1e2030;
    selection-background-color: #dfe3ff; selection-color: #1e2030;
}
QTableWidget#tablaMetodo QHeaderView::section {
    background-color: #f0f1f7; color: #5d6180; border: none;
    border-bottom: 1px solid #e3e5ee; padding: 6px; font-weight: 600;
}
"""

# Campos compartidos por los métodos de interpolación (ejemplo: Burden, J₀)
CAMPOS_INTERPOLACION = [
    {"clave": "xs", "etiqueta": "Nodos xᵢ", "ancho": True,
     "ejemplo": "1.0, 1.3, 1.6, 1.9, 2.2", "ayuda": "Valores separados por comas"},
    {"clave": "ys", "etiqueta": "Valores f(xᵢ)", "ancho": True,
     "ejemplo": "0.7651977, 0.6200860, 0.4554022, 0.2818186, 0.1103623",
     "ayuda": "Déjalo vacío si escribes f(x)"},
    {"clave": "f", "etiqueta": "f(x) (opcional)", "ejemplo": "",
     "ayuda": "Si la escribes se calcula f(xᵢ) y el error real"},
    {"clave": "xe", "etiqueta": "Evaluar en x", "ejemplo": "1.5",
     "ayuda": "Punto donde se aproxima f(x)"},
]


# ---------------------------------------------------------------------
#  Clase base
# ---------------------------------------------------------------------
class MetodoBase(QWidget):
    DESCRIPCION = ""
    CAMPOS = []          # dicts: clave, etiqueta, ejemplo, ayuda, ancho
    COLUMNAS = []
    TITULO_GRAFICA = ""
    COLUMNAS_FORM = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(ESTILO_PAGINA)
        self.campos = {}
        self._etiquetas = {c["clave"]: c["etiqueta"] for c in self.CAMPOS}
        self._construir()

    # ---------------- interfaz ----------------
    def _construir(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 18, 24, 18)
        v.setSpacing(12)

        if self.DESCRIPCION:
            desc = QLabel(self.DESCRIPCION)
            desc.setObjectName("descMetodo")
            desc.setWordWrap(True)
            v.addWidget(desc)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(4)
        fila, col, n = 0, 0, self.COLUMNAS_FORM
        for c in self.CAMPOS:
            ancho = c.get("ancho", False)
            if ancho and col != 0:
                fila, col = fila + 2, 0
            etiqueta = QLabel(c["etiqueta"])
            etiqueta.setObjectName("etiquetaCampo")
            edit = QLineEdit()
            edit.setObjectName("campo")
            if c.get("ejemplo"):
                edit.setPlaceholderText(f"ej: {c['ejemplo']}")
            edit.setToolTip(c.get("ayuda", ""))
            edit.returnPressed.connect(self.calcular)
            span = n if ancho else 1
            grid.addWidget(etiqueta, fila, col, 1, span)
            grid.addWidget(edit, fila + 1, col, 1, span)
            self.campos[c["clave"]] = edit
            if ancho:
                fila, col = fila + 2, 0
            else:
                col += 1
                if col == n:
                    fila, col = fila + 2, 0
        for i in range(n):
            grid.setColumnStretch(i, 1)
        v.addLayout(grid)

        botones = QHBoxLayout()
        botones.setSpacing(8)
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.setObjectName("btnPrimario")
        self.btn_calcular.setToolTip("También puedes presionar Enter en cualquier campo")
        self.btn_calcular.clicked.connect(self.calcular)
        btn_ejemplo = QPushButton("Cargar ejemplo")
        btn_ejemplo.setObjectName("btnSecundario")
        btn_ejemplo.setToolTip("Llena el formulario con un ejemplo que funciona")
        btn_ejemplo.clicked.connect(self.cargar_ejemplo)
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("btnSecundario")
        btn_limpiar.clicked.connect(self.limpiar)
        for b in (self.btn_calcular, btn_ejemplo, btn_limpiar):
            b.setCursor(Qt.PointingHandCursor)
            botones.addWidget(b)
        botones.addStretch()
        v.addLayout(botones)

        self.lbl_resultado = QLabel()
        self.lbl_resultado.setObjectName("resultado")
        self.lbl_resultado.setWordWrap(True)
        self.lbl_resultado.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_resultado.hide()
        v.addWidget(self.lbl_resultado)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        self.tabla = QTableWidget()
        self.tabla.setObjectName("tablaMetodo")
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.graficador = Graficador()
        splitter.addWidget(self.tabla)
        splitter.addWidget(self.graficador)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        v.addWidget(splitter, 1)

        self.configurar_columnas(self.COLUMNAS)

    # ---------------- acciones ----------------
    def calcular(self):
        self.configurar_columnas(self.COLUMNAS)
        self.lbl_resultado.hide()
        try:
            self.ejecutar()
        except (ErrorMetodo, ValueError, ZeroDivisionError, OverflowError) as e:
            QMessageBox.warning(self, "Revisa los datos", str(e))
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error inesperado", f"{type(e).__name__}: {e}")

    def ejecutar(self):
        raise NotImplementedError

    def cargar_ejemplo(self):
        for c in self.CAMPOS:
            self.campos[c["clave"]].setText(c.get("ejemplo", ""))

    def limpiar(self):
        for edit in self.campos.values():
            edit.clear()
        self.configurar_columnas(self.COLUMNAS)
        self.lbl_resultado.hide()
        self.graficador.limpiar()
        if self.CAMPOS:
            self.campos[self.CAMPOS[0]["clave"]].setFocus()

    # ---------------- tabla y resultado ----------------
    def configurar_columnas(self, columnas):
        self.tabla.clear()
        self.tabla.setRowCount(0)
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)

    def agregar_fila(self, *valores):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        for col, val in enumerate(valores):
            item = QTableWidgetItem(fmt(val))
            item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(fila, col, item)

    def mostrar_resultado(self, texto):
        self.lbl_resultado.setText(texto)
        self.lbl_resultado.show()

    def resultado_raiz(self, p, n, error, convergio, extra=""):
        if convergio:
            texto = f"Raíz aproximada  p ≈ {fmt(p)}\n{n} iteraciones · error {fmt(error)}"
        else:
            texto = (f"No convergió en {n} iteraciones.\n"
                     f"Última aproximación: {fmt(p)} · error {fmt(error)}")
        if extra:
            texto += "\n" + extra
        self.mostrar_resultado(texto)

    def graficar(self, f, referencia, **kw):
        """Grafica f en un rango que cubre los valores de 'referencia'."""
        try:
            vals = [float(v) for v in referencia
                    if v is not None and np.isfinite(float(v))]
            if not vals:
                vals = [0.0]
            lo, hi = min(vals), max(vals)
            m = (hi - lo) * 0.25 if hi > lo else 1.0
            kw.setdefault("titulo", self.TITULO_GRAFICA)
            self.graficador.graficar_funcion(f, lo - m, hi + m, **kw)
        except Exception:
            traceback.print_exc()

    # ---------------- lectura de datos ----------------
    def _etiqueta(self, clave):
        return self._etiquetas.get(clave, clave)

    def texto(self, clave):
        return self.campos[clave].text().strip()

    @staticmethod
    def _a_numero(t):
        t = t.replace("^", "**").replace("−", "-")
        return float(sp.sympify(t, locals={"e": sp.E, "pi": sp.pi}))

    def numero(self, clave, defecto=_REQUERIDO):
        t = self.texto(clave)
        if not t:
            if defecto is _REQUERIDO:
                raise ErrorMetodo(f"Falta el valor de «{self._etiqueta(clave)}».")
            return defecto
        try:
            return self._a_numero(t)
        except Exception:
            raise ErrorMetodo(f"«{self._etiqueta(clave)}» debe ser un número (escribiste «{t}»).")

    def entero(self, clave, defecto=_REQUERIDO, minimo=1):
        v = self.numero(clave, defecto)
        if v is None:
            return None
        if v != int(v) or v < minimo:
            raise ErrorMetodo(f"«{self._etiqueta(clave)}» debe ser un entero ≥ {minimo}.")
        return int(v)

    def funcion(self, clave):
        """Devuelve (expresión sympy, función numérica real)."""
        t = self.texto(clave)
        if not t:
            raise ErrorMetodo(f"Escribe {self._etiqueta(clave)}.")
        expr = parsear_funcion(t)
        nombre = self._etiqueta(clave).split("(")[0].strip() or "f"
        return expr, envolver_real(sp.lambdify(x, expr, "numpy"), nombre)

    def lista(self, clave, requerido=True):
        t = self.texto(clave)
        if not t:
            if requerido:
                raise ErrorMetodo(f"Escribe «{self._etiqueta(clave)}» separados por comas.")
            return []
        t = t.replace(";", ",")
        partes = t.split(",") if "," in t else t.split()
        valores = []
        for p in partes:
            p = p.strip()
            if not p:
                continue
            try:
                valores.append(self._a_numero(p))
            except Exception:
                raise ErrorMetodo(f"En «{self._etiqueta(clave)}», «{p}» no es un número.")
        return valores

    def coeficientes(self, clave="coefs"):
        coefs = self.lista(clave)
        while len(coefs) > 1 and coefs[0] == 0:
            coefs.pop(0)
        if len(coefs) < 2:
            raise ErrorMetodo("El polinomio debe ser al menos de grado 1.")
        return coefs

    # ---------------- interpolación ----------------
    def datos_interpolacion(self, requiere_xe=False):
        xs = self.lista("xs")
        ys = self.lista("ys", requerido=False)
        expr, f = None, None
        if self.texto("f"):
            expr, f = self.funcion("f")
        if not ys:
            if f is None:
                raise ErrorMetodo("Escribe los valores f(xᵢ) o una función f(x).")
            ys = [f(v) for v in xs]
        if len(xs) != len(ys):
            raise ErrorMetodo(f"Hay {len(xs)} nodos pero {len(ys)} valores f(xᵢ).")
        if len(xs) < 2:
            raise ErrorMetodo("Se necesitan al menos 2 nodos.")
        if len(set(xs)) != len(xs):
            raise ErrorMetodo("Los nodos xᵢ deben ser distintos.")
        xe = self.numero("xe", _REQUERIDO if requiere_xe else None)
        return xs, ys, expr, f, xe

    def terminar_interpolacion(self, poli, xs, f, xe, valor_xe=None,
                               lineas=(), nodos=None):
        poli = sp.expand(poli)
        coefs = [float(c) for c in sp.Poly(poli, x).all_coeffs()]
        texto = [f"P(x) = {poli_texto(coefs)}"]
        pnum = lambda t: np.polyval(coefs, t)
        if xe is not None:
            val = valor_xe if valor_xe is not None else pnum(xe)
            texto.append(f"P({fmt(xe)}) ≈ {fmt(val)}")
            if f is not None:
                try:
                    real = f(xe)
                    texto.append(f"f({fmt(xe)}) = {fmt(real)} · error real = {fmt(abs(real - val))}")
                except ErrorMetodo:
                    pass
        texto += list(lineas)
        self.mostrar_resultado("\n".join(texto))
        nodos = nodos if nodos is not None else xs
        self.graficar(pnum, list(nodos) + ([xe] if xe is not None else []),
                      puntos_x=list(nodos), etiqueta_puntos="Nodos",
                      etiqueta_curva="P(x)", raiz=xe,
                      etiqueta_raiz=f"P({fmt(xe, 4)})" if xe is not None else None,
                      curva_extra=(f, "f(x)") if f is not None else None)

    # ---------------- integración ----------------
    def terminar_integral(self, expr, f, a, b, aprox, nodos=(), lineas=(),
                          verticales=None):
        texto = [f"∫ f(x) dx en [{fmt(a)}, {fmt(b)}] ≈ {fmt(aprox, 10)}"]
        try:
            import mpmath
            exacto = float(mpmath.quad(sp.lambdify(x, expr, "mpmath"), [a, b]))
            texto.append(f"Valor de referencia = {fmt(exacto, 10)} · "
                         f"error = {fmt(abs(exacto - aprox))}")
        except Exception:
            pass
        texto += list(lineas)
        self.mostrar_resultado("\n".join(texto))
        self.graficar(f, [a, b], puntos_x=list(nodos) or None,
                      etiqueta_puntos="Nodos", area=(a, b), verticales=verticales)
