from modelos.problema_transporte import Constructor


def resolver(p):
    k = Constructor(p)
    pasos = [k.inicio("Esquina Noroeste")]
    while k.activo():
        i = k.filas[0]
        j = k.cols[0]
        txt = "Celda noroeste disponible: (O" + str(i + 1) + ", D" + str(j + 1) + "). " + k.asignar(i, j)
        ps = k.paso(txt)
        ps.actual = (i, j)
        pasos.append(ps)
    pasos.append(k.cierre())
    return pasos
