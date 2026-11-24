"""Aproximación de Vogel (VAM). (Archivo 'miguel.py' según la estructura del proyecto.)"""
from modelos.problema_transporte import Constructor, fmt


def penalizacion(vals):
    """Diferencia entre los dos costos menores (si hay uno solo, ese costo)."""
    if len(vals) == 1:
        return vals[0]
    a = vals[0]
    b = vals[1]
    if b < a:
        a = vals[1]
        b = vals[0]
    for k in range(2, len(vals)):
        x = vals[k]
        if x < a:
            b = a
            a = x
        elif x < b:
            b = x
    return b - a


def resolver(p):
    k = Constructor(p)
    pasos = [k.inicio("Vogel (VAM)")]
    while k.activo():
        pf = {}
        pc = {}
        for i in k.filas:
            vals = []
            for j in k.cols:
                vals.append(p.costos[i][j])
            pf[i] = penalizacion(vals)
        for j in k.cols:
            vals = []
            for i in k.filas:
                vals.append(p.costos[i][j])
            pc[j] = penalizacion(vals)
        mx = -1
        sel = None
        for i in k.filas:
            if pf[i] > mx:
                mx = pf[i]
                sel = ('f', i)
        for j in k.cols:
            if pc[j] > mx:
                mx = pc[j]
                sel = ('c', j)
        bi = -1
        bj = -1
        if sel[0] == 'f':
            bi = sel[1]
            for j in k.cols:
                if bj == -1 or p.costos[bi][j] < p.costos[bi][bj]:
                    bj = j
            linea = "fila O" + str(bi + 1)
        else:
            bj = sel[1]
            for i in k.filas:
                if bi == -1 or p.costos[i][bj] < p.costos[bi][bj]:
                    bi = i
            linea = "columna D" + str(bj + 1)
        txt = ("Mayor penalización = " + fmt(mx) + " en la " + linea + ". Menor costo en esa línea: c = "
               + fmt(p.costos[bi][bj]) + " en (O" + str(bi + 1) + ", D" + str(bj + 1) + "). " + k.asignar(bi, bj))
        ps = k.paso(txt)
        ps.actual = (bi, bj)
        ps.penal_f = pf
        ps.penal_c = pc
        ps.marcada = sel
        pasos.append(ps)
    pasos.append(k.cierre())
    return pasos
