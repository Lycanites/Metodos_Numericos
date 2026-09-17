from sympy import symbols, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, exp, log, sqrt, pi, E, ln
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

x = symbols('x')

transformaciones = standard_transformations + (
    implicit_multiplication_application,  # permite "2x" en vez de "2*x"
    convert_xor,                          # permite "^" en vez de "**"
)

#Diccionario de funciones, permite ciertas constantes y funciones permitidas

contexto_matematico = {
    "x": x,
    "e": E,
    "pi": pi,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "asin": asin,
    "acos": acos,
    "atan": atan,
    "sinh": sinh,
    "cosh": cosh,
    "tanh": tanh,
    "exp": exp,
    "log": log,
    "ln": ln,
    "sqrt": sqrt,
}

def parsear_funcion(texto):
    """
    Convierte un string ingresado por el usuario en una expresión sympy en x.
    Lanza ValueError con mensaje claro si el input es inválido.
    """
    texto = texto.strip()
    if not texto:
        raise ValueError("La función no puede estar vacía.")

    try:
        expr = parse_expr(texto, local_dict=contexto_matematico, transformations=transformaciones)
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