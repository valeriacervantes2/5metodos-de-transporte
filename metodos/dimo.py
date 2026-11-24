from modelos.problema_transporte import optimizar


def calcular_uv(p, asig):
    """Resuelve u_i + v_j = c_ij en las celdas básicas, fijando u_1 = 0."""
    u = []
    for i in range(p.m):
        u.append(None)
    v = []
    for j in range(p.n):
        v.append(None)
    u[0] = 0
    cambio = True
    while cambio:
        cambio = False
        for (i, j) in asig:
            if u[i] is not None and v[j] is None:
                v[j] = p.costos[i][j] - u[i]
                cambio = True
            elif v[j] is not None and u[i] is None:
                u[i] = p.costos[i][j] - v[j]
                cambio = True
    return u, v


def evaluar(p, asig):
    u, v = calcular_uv(p, asig)
    delta = {}
    for i in range(p.m):
        for j in range(p.n):
            if (i, j) not in asig:
                delta[(i, j)] = p.costos[i][j] - u[i] - v[j]
    return delta, u, v


def resolver(p, asig0):
    return optimizar(p, asig0, evaluar, "costo reducido")
