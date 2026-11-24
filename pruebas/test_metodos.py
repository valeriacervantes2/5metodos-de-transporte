"""Pruebas sin librerías. Ejecutar desde la raíz:  python -m pruebas.test_metodos"""
from modelos.problema_transporte import Problema, EJEMPLOS
from metodos import esquina_noroeste, costo_minimo, miguel, banquillo, dimo


def probar():
    for nombre in EJEMPLOS:
        c, o, d = EJEMPLOS[nombre]
        p = Problema(c, o, d).balanceado()
        optimos = []
        for mod in (esquina_noroeste, costo_minimo, miguel):
            a = mod.resolver(p)[-1].asig
            assert len(a) == p.m + p.n - 1, nombre + ": faltan celdas básicas"
            for i in range(p.m):
                s = 0
                for (r, k) in a:
                    if r == i:
                        s = s + a[(r, k)]
                assert s == p.oferta[i], nombre + ": oferta no cumplida"
            for j in range(p.n):
                s = 0
                for (r, k) in a:
                    if k == j:
                        s = s + a[(r, k)]
                assert s == p.demanda[j], nombre + ": demanda no cumplida"
            zb = p.costo(banquillo.resolver(p, a)[-1].asig)
            zd = p.costo(dimo.resolver(p, a)[-1].asig)
            assert zb == zd, nombre + ": Banquillo y DIMO difieren"
            optimos.append(zd)
        assert optimos[0] == optimos[1] == optimos[2], nombre + ": óptimos distintos"
        print("OK", nombre, "Z óptimo =", optimos[0])
    p = Problema(*EJEMPLOS["desbalanceado"]).balanceado()
    assert p.fict_col and p.demanda[-1] == 20
    print("OK balanceo automático (destino ficticio)")


if __name__ == "__main__":
    probar()
