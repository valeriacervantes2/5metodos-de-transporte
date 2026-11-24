"""Modelo del problema de transporte y utilidades comunes.
Lógica con ciclos e ifs puros: sin librerías (la única librería del proyecto es Tkinter, para el diseño)."""

EPS = 0.000000001

EJEMPLOS = {
    "balanceado": ([[8, 6, 10, 9], [9, 12, 13, 7], [14, 9, 16, 5]], [35, 50, 40], [45, 20, 30, 30]),
    "desbalanceado": ([[4, 6, 8], [5, 3, 7], [9, 2, 4]], [30, 40, 50], [25, 35, 40]),
}


def fmt(x):
    ent = int(x + 0.5) if x >= 0 else int(x - 0.5)
    d = x - ent
    if d < 0:
        d = -d
    if d < 0.000001:
        return str(ent)
    return "%.2f" % x


class Paso:
    """Una 'foto' de la tabla en un momento del método."""

    def __init__(self, asig, texto):
        self.asig = asig          # {(i, j): cantidad}; cantidad 0 = celda básica ε
        self.texto = texto
        self.actual = None        # celda resaltada
        self.tach_f = []          # filas tachadas
        self.tach_c = []          # columnas tachadas
        self.penal_f = None       # Vogel: {fila: penalización}
        self.penal_c = None
        self.marcada = None       # ('f', i) o ('c', j)
        self.delta = None         # costo marginal / reducido de celdas no básicas
        self.ciclo = None         # [((i, j), +1/-1)]
        self.u = None
        self.v = None
        self.optimo = False


class Problema:
    def __init__(self, costos, oferta, demanda, fict_fila=False, fict_col=False):
        self.costos = costos
        self.oferta = oferta
        self.demanda = demanda
        self.fict_fila = fict_fila
        self.fict_col = fict_col
        self.m = len(oferta)
        self.n = len(demanda)

    def balanceado(self):
        so = 0
        for x in self.oferta:
            so = so + x
        sd = 0
        for x in self.demanda:
            sd = sd + x
        c = []
        for fila in self.costos:
            c.append(list(fila))
        o = list(self.oferta)
        d = list(self.demanda)
        if so > sd:                      # destino ficticio
            for fila in c:
                fila.append(0)
            d.append(so - sd)
            return Problema(c, o, d, False, True)
        if sd > so:                      # origen ficticio
            nueva = []
            for j in range(len(d)):
                nueva.append(0)
            c.append(nueva)
            o.append(sd - so)
            return Problema(c, o, d, True, False)
        return Problema(c, o, d)

    def costo(self, asig):
        z = 0
        for (i, j) in asig:
            z = z + self.costos[i][j] * asig[(i, j)]
        return z

    def formula(self, asig):
        texto = ""
        for (i, j) in asig:
            if asig[(i, j)] > 0:
                if texto != "":
                    texto = texto + " + "
                texto = texto + fmt(self.costos[i][j]) + "·" + fmt(asig[(i, j)])
        return "Z = " + texto + " = " + fmt(self.costo(asig))


class Constructor:
    """Estado común de los métodos SBFI (maneja la degeneración con ε)."""

    def __init__(self, p):
        self.p = p
        self.o = list(p.oferta)
        self.d = list(p.demanda)
        self.filas = list(range(p.m))
        self.cols = list(range(p.n))
        self.asig = {}

    def asignar(self, i, j):
        q = self.o[i]
        if self.d[j] < q:
            q = self.d[j]
        txt = ("Se asigna min(oferta " + fmt(self.o[i]) + ", demanda " + fmt(self.d[j]) + ") = " + fmt(q)
               + " a (O" + str(i + 1) + ", D" + str(j + 1) + "). ")
        self.asig[(i, j)] = q
        self.o[i] = self.o[i] - q
        self.d[j] = self.d[j] - q
        fo = self.o[i] <= EPS
        fd = self.d[j] <= EPS
        if fo and fd:
            txt = txt + "Oferta y demanda se agotan a la vez (degeneración): "
            if len(self.filas) > 1:
                self.filas.remove(i)
                txt = txt + "se tacha solo la fila O" + str(i + 1) + "; la columna quedará con una asignación ε."
            elif len(self.cols) > 1:
                self.cols.remove(j)
                txt = txt + "se tacha solo la columna D" + str(j + 1) + "; la fila quedará con una asignación ε."
            else:
                self.filas.remove(i)
                self.cols.remove(j)
                txt = txt + "fin."
        elif fo:
            self.filas.remove(i)
            txt = txt + "Se agota la oferta: se tacha la fila O" + str(i + 1) + "."
        else:
            self.cols.remove(j)
            txt = txt + "Se satisface la demanda: se tacha la columna D" + str(j + 1) + "."
        return txt

    def activo(self):
        return len(self.filas) > 0 and len(self.cols) > 0

    def paso(self, txt):
        ps = Paso(dict(self.asig), txt)
        for i in range(self.p.m):
            if i not in self.filas:
                ps.tach_f.append(i)
        for j in range(self.p.n):
            if j not in self.cols:
                ps.tach_c.append(j)
        return ps

    def inicio(self, nombre):
        return self.paso(nombre + ": tabla inicial. Se requieren m+n−1 = " + str(self.p.m + self.p.n - 1)
                         + " celdas básicas.")

    def cierre(self):
        return Paso(dict(self.asig), "SBFI completa con " + str(len(self.asig)) + " celdas básicas (m+n−1 = "
                    + str(self.p.m + self.p.n - 1) + "). Las celdas con ε son ceros básicos.")


def encontrar_ciclo(base, ent):
    """Ciclo cerrado (alternando fila/columna) que pasa por ent y celdas básicas."""
    def buscar(camino, horizontal):
        i = camino[-1][0]
        j = camino[-1][1]
        if len(camino) > 3:
            if horizontal and ent[0] == i:
                return camino
            if (not horizontal) and ent[1] == j:
                return camino
        for c in base:
            if c in camino:
                continue
            if horizontal and c[0] == i:
                r = buscar(camino + [c], False)
                if r is not None:
                    return r
            if (not horizontal) and c[1] == j:
                r = buscar(camino + [c], True)
                if r is not None:
                    return r
        return None

    camino = buscar([ent], True)
    ciclo = []
    signo = 1
    for c in camino:
        ciclo.append((c, signo))
        signo = -signo
    return ciclo


def aplicar_ciclo(asig, ciclo):
    theta = None
    sale = None
    for (c, s) in ciclo:
        if s < 0:
            if theta is None or asig[c] < theta:
                theta = asig[c]
                sale = c
    nueva = dict(asig)
    for (c, s) in ciclo:
        valor = 0
        if c in nueva:
            valor = nueva[c]
        valor = valor + s * theta
        if valor < EPS and valor > -EPS:
            valor = 0
        nueva[c] = valor
    del nueva[sale]
    return nueva, theta, sale


def optimizar(p, asig0, evaluar, etiqueta):
    """Evalúa, elige el costo más negativo, aplica el ciclo y repite hasta que no haya negativos."""
    asig = dict(asig0)
    pasos = []
    for vuelta in range(500):
        delta, u, v = evaluar(p, asig)
        ent = None
        menor = -EPS
        for c in delta:
            if delta[c] < menor:
                menor = delta[c]
                ent = c
        if ent is None:
            ps = Paso(asig, "Ningún " + etiqueta + " es negativo: la solución es ÓPTIMA.")
            ps.delta, ps.u, ps.v, ps.optimo = delta, u, v, True
            pasos.append(ps)
            break
        ciclo = encontrar_ciclo(list(asig.keys()), ent)
        nueva, theta, sale = aplicar_ciclo(asig, ciclo)
        txt = ("La celda (O" + str(ent[0] + 1) + ", D" + str(ent[1] + 1) + ") tiene el " + etiqueta
               + " más negativo (" + fmt(menor) + "). Ciclo cerrado con signos +/−: θ = " + fmt(theta)
               + " (mínimo de las celdas con −). Sale de la base (O" + str(sale[0] + 1) + ", D"
               + str(sale[1] + 1) + "). Z cambia en " + fmt(menor * theta) + ".")
        ps = Paso(asig, txt)
        ps.actual, ps.delta, ps.ciclo, ps.u, ps.v = ent, delta, ciclo, u, v
        pasos.append(ps)
        asig = nueva
    return pasos
