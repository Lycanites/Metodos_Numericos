from sympy import symbols, sympify

x = symbols('x')

def puntoMedio(a, b):
    return (a + b) / 2

def evalua(func, valor_x):
    return float(func.subs(x, valor_x))

def nuevoIntervalo(a, b, func):
    m = puntoMedio(a, b)
    if evalua(func, a) * evalua(func, m) < 0:
        return a, m
    else:
        return m, b

def funcion():
    print("Escribe la función a calcular f(x): ")
    return sympify(input())

def calcError(a, b):
    return abs(b - a) / 2

def biseccion(a, b, func, err):

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

        print(
            f"Iteración: {iteracion} | "
            f"a: {a} | "
            f"b: {b} | "
            f"m: {m} | "
            f"Error: {error}"
        )

    return m


# Programa principal
func = funcion()

a = float(input("Ingrese el límite inferior a: "))
b = float(input("Ingrese el límite superior b: "))
err = float(input("Ingrese el error tolerado: "))

raiz = biseccion(a, b, func, err)

print("\n================================")
print(f"La raíz aproximada es: {raiz}")
print("================================")