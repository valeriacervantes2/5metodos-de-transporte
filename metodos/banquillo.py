from modelos.problema_transporte import encontrar_ciclo, optimizar


def evaluar(p, asig):
    base = list(asig.keys())
    delta = {}
    for i in range(p.m):
        for j in range(p.n):
            if (i, j) not in asig:
                ciclo = encontrar_ciclo(base, (i, j))
                total = 0
                for (c, s) in ciclo:
                    total = total + s * p.costos[c[0]][c[1]]
                delta[(i, j)] = total
    return delta, None, None


def resolver(p, asig0):
    return optimizar(p, asig0, evaluar, "costo marginal")
