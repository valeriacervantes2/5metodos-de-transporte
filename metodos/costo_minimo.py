from modelos.problema_transporte import Constructor, fmt


def resolver(p):
    k = Constructor(p)
    pasos = [k.inicio("Costo Mínimo")]
    while k.activo():
        bi = -1
        bj = -1
        menor = None
        for i in k.filas:
            for j in k.cols:
                if menor is None or p.costos[i][j] < menor:
                    menor = p.costos[i][j]
                    bi = i
                    bj = j
        txt = ("Menor costo disponible: c = " + fmt(menor) + " en (O" + str(bi + 1) + ", D" + str(bj + 1)
               + "). " + k.asignar(bi, bj))
        ps = k.paso(txt)
        ps.actual = (bi, bj)
        pasos.append(ps)
    pasos.append(k.cierre())
    return pasos
