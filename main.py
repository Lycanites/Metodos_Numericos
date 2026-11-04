import sys
import importlib
import importlib.util
import traceback

from PySide6.QtCore import (
    Qt, QEvent, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QFrame,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QScrollArea,
    QButtonGroup, QSizePolicy
)


# =====================================================================
#  CATÁLOGO DEL MENÚ
#  Para conectar un método nuevo solo crea el archivo/clase indicado en
#  "modulo" y "clase". La clase debe heredar de QWidget.
#  Si el archivo aún no existe, se muestra una página "Pendiente".
# =====================================================================
MENU = [
    {
        "id": "cerrados",
        "titulo": "Métodos cerrados",
        "icono": "▣",
        "descripcion": "Requieren un intervalo [a, b] con cambio de signo",
        "metodos": [
            {"nombre": "Bisección", "modulo": "metodos.biseccion", "clase": "Biseccion",
             "formula": "pₙ = a + (b − a)/2\n|pₙ − p| ≤ (b − a)/2ⁿ"},
            {"nombre": "Falsa posición", "modulo": "metodos.falsaPosicion", "clase": "FalsaPosicion",
             "formula": "pₙ = b − f(b)(b − a) / [f(b) − f(a)]"},
        ],
    },
    {
        "id": "abiertos",
        "titulo": "Métodos abiertos",
        "icono": "◇",
        "descripcion": "Parten de uno o más valores iniciales",
        "metodos": [
            {"nombre": "Punto fijo", "modulo": "metodos.puntoFijo", "clase": "PuntoFijo",
             "formula": "pₙ = g(pₙ₋₁),   |g′(x)| ≤ k < 1"},
            {"nombre": "Newton-Raphson", "modulo": "metodos.newtonRaphson", "clase": "FrmNewtonRaphson",
             "formula": "pₙ = pₙ₋₁ − f(pₙ₋₁) / f′(pₙ₋₁)"},
            {"nombre": "Newton (raíces múltiples)", "modulo": "metodos.newtonMultiple", "clase": "NewtonMultiple",
             "formula": "xᵢ₊₁ = xᵢ − f(xᵢ)f′(xᵢ) / ([f′(xᵢ)]² − f(xᵢ)f″(xᵢ))"},
            {"nombre": "Secante", "modulo": "metodos.secante", "clase": "Secante",
             "formula": "pₙ = pₙ₋₁ − f(pₙ₋₁)(pₙ₋₁ − pₙ₋₂) / [f(pₙ₋₁) − f(pₙ₋₂)]"},
            {"nombre": "Steffensen", "modulo": "metodos.steffensen", "clase": "steffensen",
             "formula": "p₁ = g(p₀),  p₂ = g(p₁)\np = p₀ − (p₁ − p₀)² / (p₂ − 2p₁ + p₀)"},
            {"nombre": "Müller", "modulo": "metodos.muller", "clase": "Muller",
             "formula": "Ajusta una parábola por x₀, x₁, x₂ y toma la raíz más cercana"},
        ],
    },
    {
        "id": "aceleradores",
        "titulo": "Aceleradores",
        "icono": "»",
        "descripcion": "Polinomios y aceleración de convergencia",
        "metodos": [
            {"nombre": "Horner", "modulo": "metodos.horner", "clase": "Horner",
             "formula": "bₙ = aₙ,   bₖ = aₖ + bₖ₊₁·x₀\nP(x₀) = b₀,   P′(x₀) = Q(x₀)"},
            {"nombre": "Newton-Horner", "modulo": "metodos.newtonHorner", "clase": "NewtonHorner",
             "formula": "xₖ₊₁ = xₖ − P(xₖ) / P′(xₖ)   (evaluados con Horner)"},
            {"nombre": "Deflación", "modulo": "metodos.deflacion", "clase": "Deflacion",
             "formula": "P(x) ≈ (x − x₁)·Q₁(x)"},
            {"nombre": "Aitken Δ²", "modulo": "metodos.aitken", "clase": "Aitken",
             "formula": "p̂ₙ = pₙ − (pₙ₊₁ − pₙ)² / (pₙ₊₂ − 2pₙ₊₁ + pₙ)"},
            {"nombre": "Bairstow", "modulo": "metodos.bairstow", "clase": "Bairstow",
             "formula": "Extrae factores cuadráticos x² − r·x − s de P(x)"},
        ],
    },
    {
        "id": "interpolacion",
        "titulo": "Interpolación",
        "icono": "∿",
        "descripcion": "Polinomios que pasan por puntos dados",
        "metodos": [
            {"nombre": "Vandermonde", "modulo": "interpolacion.vandermonde", "clase": "Vandermonde",
             "formula": "V·a = f,   Vᵢⱼ = xᵢʲ"},
            {"nombre": "Lagrange", "modulo": "interpolacion.lagrange", "clase": "lagrange",
             "formula": "Pₙ(x) = Σ f(xₖ)·Lₙ,ₖ(x)\nLₙ,ₖ(x) = Π (x − xᵢ)/(xₖ − xᵢ)"},
            {"nombre": "Neville", "modulo": "interpolacion.neville", "clase": "Neville",
             "formula": "Qᵢ,ⱼ = [(x − xᵢ₋ⱼ)Qᵢ,ⱼ₋₁ − (x − xᵢ)Qᵢ₋₁,ⱼ₋₁] / (xᵢ − xᵢ₋ⱼ)"},
            {"nombre": "Diferencias divididas", "modulo": "interpolacion.diferenciasDivididas",
             "clase": "DiferenciasDivididas",
             "formula": "Fᵢ,ⱼ = (Fᵢ,ⱼ₋₁ − Fᵢ₋₁,ⱼ₋₁) / (xᵢ − xᵢ₋ⱼ)\nPₙ(x) = Σ Fₖ,ₖ·Π(x − xᵢ)"},
            {"nombre": "Hermite", "modulo": "interpolacion.hermite", "clase": "Hermite",
             "formula": "z₂ᵢ = z₂ᵢ₊₁ = xᵢ,   f[z₂ᵢ, z₂ᵢ₊₁] = f′(xᵢ)"},
        ],
    },
    {
        "id": "extrapolacion",
        "titulo": "Extrapolación",
        "icono": "∫",
        "descripcion": "Richardson e integración numérica",
        "metodos": [
            {"nombre": "Richardson", "modulo": "extrapolacion.richardson", "clase": "Richardson",
             "formula": "Nⱼ(h) = Nⱼ₋₁(h/2) + [Nⱼ₋₁(h/2) − Nⱼ₋₁(h)] / (4ʲ⁻¹ − 1)"},
            {"nombre": "Simpson 1/3", "modulo": "extrapolacion.simpson13", "clase": "Simpson13",
             "formula": "∫ f ≈ (h/3)[f₀ + 4f₁ + f₂]"},
            {"nombre": "Simpson 3/8", "modulo": "extrapolacion.simpson38", "clase": "Simpson38",
             "formula": "∫ f ≈ (3h/8)[f₀ + 3f₁ + 3f₂ + f₃]"},
            {"nombre": "Cuadratura adaptativa", "modulo": "extrapolacion.cuadraturaAdaptativa",
             "clase": "CuadraturaAdaptativa",
             "formula": "Subdivide mientras |S(a,b) − S(a,m) − S(m,b)| ≥ 15ε"},
            {"nombre": "Cuadratura gaussiana", "modulo": "extrapolacion.cuadraturaGaussiana",
             "clase": "CuadraturaGaussiana",
             "formula": "∫₋₁¹ f ≈ Σ cᵢ·f(xᵢ),   xᵢ raíces de Legendre Pₙ"},
        ],
    },
]

ANCHO_EXPANDIDO = 240
ANCHO_COMPACTO = 64

# Todos los selectores usan objectName, así no afectan el estilo
# de las páginas de cada método.
ESTILO = """
QWidget#navbar { background-color: #1e2030; }
QLabel#appTitulo { color: #ffffff; font-size: 15px; font-weight: 600; padding-left: 4px; }

QPushButton#btnMenu {
    background: transparent; color: #c8cbe0; border: none;
    font-size: 18px; padding: 6px 12px; border-radius: 6px;
}
QPushButton#btnMenu:hover { background-color: #2c2f45; color: #ffffff; }

QPushButton#btnInicio, QPushButton#btnSeccion {
    color: #c8cbe0; background: transparent; border: none;
    text-align: left; padding: 9px 12px; font-size: 13px;
    font-weight: 600; border-radius: 6px;
}
QPushButton#btnInicio:hover, QPushButton#btnSeccion:hover {
    background-color: #2c2f45; color: #ffffff;
}
QPushButton#btnInicio:checked { background-color: #33385a; color: #ffffff; }
QPushButton#btnSeccion[activa="true"] { color: #9aa8ff; }

QPushButton#btnMetodo {
    color: #a9adc6; background: transparent; border: none;
    border-left: 3px solid transparent; border-radius: 0px;
    text-align: left; padding: 7px 10px 7px 34px; font-size: 13px;
}
QPushButton#btnMetodo:hover { background-color: #2c2f45; color: #ffffff; }
QPushButton#btnMetodo[pendiente="true"] { color: #6c7090; }
QPushButton#btnMetodo:checked {
    background-color: #33385a; color: #ffffff;
    border-left: 3px solid #7c8cff; font-weight: 600;
}

QFrame#separador { background-color: #2c2f45; max-height: 1px; border: none; }

QScrollArea#navScroll { background: transparent; border: none; }
QWidget#navCuerpo { background: transparent; }
QScrollArea#navScroll QScrollBar:vertical { width: 6px; background: transparent; }
QScrollArea#navScroll QScrollBar::handle:vertical {
    background: #3a3e58; border-radius: 3px; min-height: 24px;
}
QScrollArea#navScroll QScrollBar::add-line:vertical,
QScrollArea#navScroll QScrollBar::sub-line:vertical { height: 0px; }

QWidget#contenido { background-color: #f4f5fa; }
QWidget#encabezado { background-color: #ffffff; border-bottom: 1px solid #e3e5ee; }
QLabel#migas { color: #8a8fa8; font-size: 12px; }
QLabel#tituloPagina { color: #1e2030; font-size: 20px; font-weight: 600; }
QLabel#textoSuave { color: #5d6180; font-size: 14px; }

QPushButton#tarjeta {
    background-color: #ffffff; color: #1e2030;
    border: 1px solid #e3e5ee; border-radius: 10px;
    padding: 16px; text-align: left; font-size: 13px;
}
QPushButton#tarjeta:hover { border: 1px solid #7c8cff; background-color: #f7f8ff; }

QFrame#tarjetaInfo { background-color: #ffffff; border: 1px solid #e3e5ee; border-radius: 10px; }
QLabel#tituloInfo { color: #1e2030; font-size: 16px; font-weight: 600; }
QLabel#subtitulo { color: #8a8fa8; font-size: 12px; font-weight: 600; }
QLabel#formula {
    font-family: Consolas, "Courier New", monospace; font-size: 14px;
    background-color: #f4f5fa; color: #33385a; padding: 12px; border-radius: 6px;
}
QLabel#nota { color: #5d6180; font-size: 13px; }
QLabel#badgePendiente {
    background-color: #fff4e0; color: #a86400; border-radius: 10px;
    padding: 3px 10px; font-size: 11px; font-weight: 600;
}
QLabel#badgeError {
    background-color: #fde8e8; color: #b42318; border-radius: 10px;
    padding: 3px 10px; font-size: 11px; font-weight: 600;
}
"""


# =====================================================================
#  Carga de páginas
# =====================================================================
def modulo_existe(nombre_modulo):
    try:
        return importlib.util.find_spec(nombre_modulo) is not None
    except Exception:
        return False


def cargar_pagina(metodo, categoria):
    """Devuelve el widget del método o una página informativa si aún no existe."""
    modulo, clase = metodo["modulo"], metodo["clase"]
    try:
        mod = importlib.import_module(modulo)
    except ModuleNotFoundError as e:
        if e.name == modulo:
            return crear_pagina_info(metodo, categoria)
        traceback.print_exc()
        return crear_pagina_info(metodo, categoria, error=e)
    except Exception as e:
        traceback.print_exc()
        return crear_pagina_info(metodo, categoria, error=e)

    obj = getattr(mod, clase, None)
    if obj is None:
        return crear_pagina_info(
            metodo, categoria,
            error=f"El archivo existe, pero no contiene la clase '{clase}'.")
    if not (isinstance(obj, type) and issubclass(obj, QWidget)):
        return crear_pagina_info(
            metodo, categoria,
            error=f"'{clase}' existe, pero no es una clase QWidget.")
    try:
        return obj()
    except Exception as e:
        traceback.print_exc()
        return crear_pagina_info(metodo, categoria, error=e)


def crear_pagina_info(metodo, categoria, error=None):
    pagina = QWidget()
    externo = QVBoxLayout(pagina)
    externo.setContentsMargins(32, 28, 32, 28)

    tarjeta = QFrame()
    tarjeta.setObjectName("tarjetaInfo")
    tarjeta.setAttribute(Qt.WA_StyledBackground, True)
    tarjeta.setMaximumWidth(720)
    v = QVBoxLayout(tarjeta)
    v.setContentsMargins(24, 22, 24, 22)
    v.setSpacing(12)

    fila = QHBoxLayout()
    titulo = QLabel(metodo["nombre"])
    titulo.setObjectName("tituloInfo")
    badge = QLabel("Error al cargar" if error else "Pendiente de implementar")
    badge.setObjectName("badgeError" if error else "badgePendiente")
    fila.addWidget(titulo)
    fila.addSpacing(10)
    fila.addWidget(badge)
    fila.addStretch()
    v.addLayout(fila)

    if metodo.get("formula"):
        sub = QLabel("FÓRMULA DE REFERENCIA")
        sub.setObjectName("subtitulo")
        formula = QLabel(metodo["formula"])
        formula.setObjectName("formula")
        formula.setTextInteractionFlags(Qt.TextSelectableByMouse)
        v.addWidget(sub)
        v.addWidget(formula)

    if error:
        texto = f"No se pudo abrir este método:\n{error}"
    else:
        ruta = metodo["modulo"].replace(".", "/") + ".py"
        texto = (f"Crea la clase {metodo['clase']} (QWidget) en {ruta} "
                 f"y aparecerá aquí automáticamente.")
    nota = QLabel(texto)
    nota.setObjectName("nota")
    nota.setWordWrap(True)
    nota.setTextInteractionFlags(Qt.TextSelectableByMouse)
    v.addWidget(nota)

    externo.addWidget(tarjeta, 0, Qt.AlignHCenter)
    externo.addStretch()
    return pagina


# =====================================================================
#  Ventana principal
# =====================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Métodos Numéricos")
        self.resize(1040, 640)
        self.setMinimumSize(780, 480)
        self.setStyleSheet(ESTILO)

        self._colapsada = False       # el usuario la contrajo con ☰
        self._por_hover = False       # está abierta temporalmente por hover
        self._compacto = False        # se muestran solo iconos
        self._seccion_abierta = None
        self._anim = None

        self._paginas = {}            # nombre -> widget (se crean al primer uso)
        self._botones = {}            # nombre -> botón del menú
        self._secciones = {}          # id -> (botón cabecera, contenedor, categoría)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._crear_navbar())
        layout.addWidget(self._crear_contenido(), 1)

        self.ir_a_inicio()

    # ------------------------------------------------------------------
    #  Construcción de la interfaz
    # ------------------------------------------------------------------
    def _boton(self, texto, objeto, tooltip=""):
        b = QPushButton(texto)
        b.setObjectName(objeto)
        b.setCursor(Qt.PointingHandCursor)
        b.setToolTip(tooltip)
        b.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        return b

    def _crear_navbar(self):
        self.navbar = QWidget()
        self.navbar.setObjectName("navbar")
        self.navbar.setAttribute(Qt.WA_StyledBackground, True)
        self.navbar.setMinimumWidth(ANCHO_EXPANDIDO)
        self.navbar.setMaximumWidth(ANCHO_EXPANDIDO)
        self.navbar.installEventFilter(self)

        v = QVBoxLayout(self.navbar)
        v.setContentsMargins(8, 12, 8, 12)
        v.setSpacing(4)

        # Barra superior: ☰ + título
        superior = QHBoxLayout()
        superior.setSpacing(4)
        self.btn_menu = QPushButton("☰")
        self.btn_menu.setObjectName("btnMenu")
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.setToolTip("Contraer / fijar el menú")
        self.btn_menu.clicked.connect(self.alternar_navbar)
        self.lbl_app = QLabel("Métodos Numéricos")
        self.lbl_app.setObjectName("appTitulo")
        self.lbl_app.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        superior.addWidget(self.btn_menu)
        superior.addWidget(self.lbl_app, 1)
        v.addLayout(superior)
        v.addSpacing(10)

        self.grupo = QButtonGroup(self)
        self.grupo.setExclusive(True)

        self.btn_inicio = self._boton("⌂   Inicio", "btnInicio", "Pantalla de inicio")
        self.btn_inicio.setCheckable(True)
        self.btn_inicio.clicked.connect(self.ir_a_inicio)
        self.grupo.addButton(self.btn_inicio)
        v.addWidget(self.btn_inicio)

        sep = QFrame()
        sep.setObjectName("separador")
        sep.setFixedHeight(1)
        v.addSpacing(6)
        v.addWidget(sep)
        v.addSpacing(6)

        # Secciones (con scroll por si la ventana es pequeña)
        scroll = QScrollArea()
        scroll.setObjectName("navScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.viewport().setAutoFillBackground(False)

        cuerpo = QWidget()
        cuerpo.setObjectName("navCuerpo")
        cuerpo.setAutoFillBackground(False)
        cv = QVBoxLayout(cuerpo)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(2)

        for cat in MENU:
            cabecera = self._boton("", "btnSeccion",
                                   f"{cat['titulo']}\n{cat['descripcion']}")
            cabecera.clicked.connect(lambda _=False, cid=cat["id"]: self._alternar_seccion(cid))

            contenedor = QWidget()
            lv = QVBoxLayout(contenedor)
            lv.setContentsMargins(0, 2, 0, 6)
            lv.setSpacing(1)
            for metodo in cat["metodos"]:
                pendiente = not modulo_existe(metodo["modulo"])
                tip = metodo["nombre"]
                if metodo.get("formula"):
                    tip += "\n" + metodo["formula"]
                if pendiente:
                    tip += "\n(pendiente de implementar)"
                b = self._boton(metodo["nombre"], "btnMetodo", tip)
                b.setCheckable(True)
                b.setProperty("pendiente", "true" if pendiente else "false")
                b.clicked.connect(lambda _=False, c=cat, m=metodo: self.ir_a_metodo(c, m))
                self.grupo.addButton(b)
                self._botones[metodo["nombre"]] = b
                lv.addWidget(b)
            contenedor.setVisible(False)

            cv.addWidget(cabecera)
            cv.addWidget(contenedor)
            self._secciones[cat["id"]] = (cabecera, contenedor, cat)

        cv.addStretch()
        scroll.setWidget(cuerpo)
        v.addWidget(scroll, 1)

        self._refrescar_secciones()
        return self.navbar

    def _crear_contenido(self):
        contenido = QWidget()
        contenido.setObjectName("contenido")
        contenido.setAttribute(Qt.WA_StyledBackground, True)
        v = QVBoxLayout(contenido)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # Encabezado: dónde está el usuario
        encabezado = QWidget()
        encabezado.setObjectName("encabezado")
        encabezado.setAttribute(Qt.WA_StyledBackground, True)
        ev = QVBoxLayout(encabezado)
        ev.setContentsMargins(28, 14, 28, 14)
        ev.setSpacing(2)
        self.lbl_migas = QLabel()
        self.lbl_migas.setObjectName("migas")
        self.lbl_titulo = QLabel()
        self.lbl_titulo.setObjectName("tituloPagina")
        ev.addWidget(self.lbl_migas)
        ev.addWidget(self.lbl_titulo)

        self.stack = QStackedWidget()
        self.page_inicio = self._crear_inicio()
        self.stack.addWidget(self.page_inicio)

        v.addWidget(encabezado)
        v.addWidget(self.stack, 1)
        return contenido

    def _crear_inicio(self):
        pagina = QWidget()
        v = QVBoxLayout(pagina)
        v.setContentsMargins(28, 24, 28, 24)
        v.setSpacing(16)

        texto = QLabel("Elige una categoría o selecciona un método en el menú lateral.")
        texto.setObjectName("textoSuave")
        v.addWidget(texto)

        grid = QGridLayout()
        grid.setSpacing(14)
        for i, cat in enumerate(MENU):
            n = len(cat["metodos"])
            b = QPushButton(f"{cat['icono']}   {cat['titulo']}\n\n"
                            f"{n} métodos · {cat['descripcion']}")
            b.setObjectName("tarjeta")
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(96)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.setToolTip(", ".join(m["nombre"] for m in cat["metodos"]))
            b.clicked.connect(lambda _=False, c=cat: self.ir_a_metodo(c, c["metodos"][0]))
            grid.addWidget(b, i // 3, i % 3)
        v.addLayout(grid)
        v.addStretch()
        return pagina

    # ------------------------------------------------------------------
    #  Navegación
    # ------------------------------------------------------------------
    def ir_a_inicio(self):
        self.btn_inicio.setChecked(True)
        self.stack.setCurrentWidget(self.page_inicio)
        self.lbl_migas.setText("Inicio")
        self.lbl_titulo.setText("Métodos Numéricos")
        self.setWindowTitle("Métodos Numéricos")
        self._marcar_seccion_activa(None)

    def ir_a_metodo(self, cat, metodo):
        nombre = metodo["nombre"]
        if nombre not in self._paginas:
            pagina = cargar_pagina(metodo, cat)
            self._paginas[nombre] = pagina
            self.stack.addWidget(pagina)

        self.stack.setCurrentWidget(self._paginas[nombre])
        self._botones[nombre].setChecked(True)
        self._seccion_abierta = cat["id"]
        self._refrescar_secciones()
        self._marcar_seccion_activa(cat["id"])

        self.lbl_migas.setText(f"Inicio   ›   {cat['titulo']}")
        self.lbl_titulo.setText(nombre)
        self.setWindowTitle(f"{nombre} · Métodos Numéricos")

    # ------------------------------------------------------------------
    #  Secciones (acordeón: solo una abierta a la vez)
    # ------------------------------------------------------------------
    def _alternar_seccion(self, cat_id):
        if self._compacto:
            self._seccion_abierta = cat_id
            self.alternar_navbar()
            return
        self._seccion_abierta = None if self._seccion_abierta == cat_id else cat_id
        self._refrescar_secciones()

    def _refrescar_secciones(self):
        for cid, (cabecera, contenedor, cat) in self._secciones.items():
            abierta = cid == self._seccion_abierta
            contenedor.setVisible(abierta and not self._compacto)
            if self._compacto:
                cabecera.setText(cat["icono"])
            else:
                flecha = "▾" if abierta else "▸"
                cabecera.setText(f"{flecha}   {cat['icono']}   {cat['titulo']}")

    def _marcar_seccion_activa(self, cat_id):
        for cid, (cabecera, _, _) in self._secciones.items():
            cabecera.setProperty("activa", "true" if cid == cat_id else "false")
            cabecera.style().unpolish(cabecera)
            cabecera.style().polish(cabecera)

    # ------------------------------------------------------------------
    #  Contraer / expandir (manual con ☰ y temporal con hover)
    # ------------------------------------------------------------------
    def alternar_navbar(self):
        self._colapsada = not self._colapsada
        self._por_hover = False
        self._animar(ANCHO_COMPACTO if self._colapsada else ANCHO_EXPANDIDO)

    def eventFilter(self, obj, event):
        if obj is self.navbar:
            if event.type() == QEvent.Enter and self._colapsada and not self._por_hover:
                self._por_hover = True
                self._animar(ANCHO_EXPANDIDO)
            elif event.type() == QEvent.Leave and self._por_hover:
                self._por_hover = False
                self._animar(ANCHO_COMPACTO)
        return super().eventFilter(obj, event)

    def _aplicar_compacto(self, compacto):
        self._compacto = compacto
        self.lbl_app.setVisible(not compacto)
        self.btn_inicio.setText("⌂" if compacto else "⌂   Inicio")
        self._refrescar_secciones()

    def _animar(self, destino):
        if self._anim is not None:
            self._anim.stop()
        if destino == ANCHO_EXPANDIDO:
            self._aplicar_compacto(False)

        inicio = self.navbar.width()
        self._anim = QParallelAnimationGroup(self)
        for prop in (b"minimumWidth", b"maximumWidth"):
            a = QPropertyAnimation(self.navbar, prop)
            a.setDuration(220)
            a.setStartValue(inicio)
            a.setEndValue(destino)
            a.setEasingCurve(QEasingCurve.OutCubic)
            self._anim.addAnimation(a)
        if destino == ANCHO_COMPACTO:
            self._anim.finished.connect(lambda: self._aplicar_compacto(True))
        self._anim.start()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QToolTip {
            background-color: #1e2030; color: #ffffff;
            border: 1px solid #33385a; padding: 6px; font-size: 12px;
        }
    """)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()