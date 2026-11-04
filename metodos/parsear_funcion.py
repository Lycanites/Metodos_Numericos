import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor
)

x = sp.symbols("x")

_TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application, convert_xor
)
_LOCALES = {"x": x, "e": sp.E, "pi": sp.pi, "ln": sp.log}


def parsear_funcion(texto):
    """
    Convierte el texto del usuario en una expresión de sympy que depende de x.
    Acepta ^ para potencias y multiplicación implícita: 2x, 3sin(x), x(x+1).
    Lanza ValueError con un mensaje claro si no se puede interpretar.
    """
    texto = (texto or "").strip()
    if not texto:
        raise ValueError("Escribe una función.")
    texto = texto.replace("√", "sqrt").replace("π", "pi").replace("−", "-")
    try:
        expr = parse_expr(texto, local_dict=dict(_LOCALES),
                          transformations=_TRANSFORMACIONES)
    except Exception as e:
        raise ValueError(f"No se pudo interpretar «{texto}». Revisa la sintaxis.\n({e})")

    libres = expr.free_symbols - {x}
    if libres:
        nombres = ", ".join(sorted(str(s) for s in libres))
        raise ValueError(f"La función solo puede depender de x (encontré: {nombres}).")
    return expr
