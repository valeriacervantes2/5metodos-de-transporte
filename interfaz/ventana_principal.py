"""Interfaz Tkinter: editor dinámico, 5 métodos paso a paso y comparativa final."""
import tkinter as tk
from tkinter import ttk, messagebox

from modelos.problema_transporte import Problema, EJEMPLOS, fmt
from metodos import esquina_noroeste, costo_minimo, miguel, banquillo, dimo

INICIALES = {"Esquina Noroeste": esquina_noroeste, "Costo Mínimo": costo_minimo, "Vogel (VAM)": miguel}
BG, TXT, ACC = "#f7f8fa", "#111827", "#2563eb"
F = "Segoe UI"
BOLD, BIG = (F, 10, "bold"), (F, 18, "bold")


class Visor(tk.Frame):
    """Pestaña de un método con controles Anterior / Siguiente / Ir al final."""

    def __init__(self, master, fn, opt=False, app=None):
        super().__init__(master, bg=BG)
        self.fn, self.opt, self.app = fn, opt, app
        self.p, self.pasos, self.i = None, [], 0
        self.todo = True
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=4)
        if opt:
            tk.Label(top, text="Solución inicial:", bg=BG, font=BOLD).pack(side="left")
            self.sel = ttk.Combobox(top, values=list(INICIALES), state="readonly", width=18)
            self.sel.set("Vogel (VAM)")
            self.sel.pack(side="left", padx=4)
            self.sel.bind("<<ComboboxSelected>>", lambda e: self.refrescar())
        for t, c in (("◀ Anterior", -1), ("Siguiente ▶", 1), ("Ir al final ⏭", 10 ** 6)):
            ttk.Button(top, text=t, command=lambda c=c: self.ir(c)).pack(side="left", padx=3)
        self.btn_modo = ttk.Button(top, text="Paso a paso", command=self.alternar)
        self.btn_modo.pack(side="left", padx=3)
        self.lbl = tk.Label(top, bg=BG, font=BOLD)
        self.lbl.pack(side="left", padx=10)
        self.txt = tk.Label(self, bg="#eef2ff", fg=TXT, justify="left", anchor="w", wraplength=1050,
                            padx=8, pady=6, font=(F, 10))
        self.txt.pack(fill="x")
        self.zl = tk.Label(self, bg=BG, fg="#065f46", font=(F, 11, "bold"), justify="left",
                           anchor="w", wraplength=1050)
        self.zl.pack(fill="x", pady=3)
        cont = tk.Frame(self)
        cont.pack(fill="both", expand=True)
        self.cv = tk.Canvas(cont, bg="white", highlightthickness=0)
        hs = ttk.Scrollbar(cont, orient="horizontal", command=self.cv.xview)
        vs = ttk.Scrollbar(cont, orient="vertical", command=self.cv.yview)
        self.cv.configure(xscrollcommand=hs.set, yscrollcommand=vs.set)
        hs.pack(side="bottom", fill="x")
        vs.pack(side="right", fill="y")
        self.cv.pack(side="left", fill="both", expand=True)
        self.cv.bind("<MouseWheel>", lambda e: self.cv.yview_scroll(int(-e.delta / 120), "units"))
        self.cv.bind("<Button-4>", lambda e: self.cv.yview_scroll(-1, "units"))
        self.cv.bind("<Button-5>", lambda e: self.cv.yview_scroll(1, "units"))

    def cargar(self, p):
        self.p = p
        self.refrescar()

    def refrescar(self):
        if not self.p:
            return
        self.pasos = self.fn(self.p, self.app.iniciales[self.sel.get()]) if self.opt else self.fn(self.p)
        self.i = 0
        self.dibujar()

    def alternar(self):
        self.todo = not self.todo
        self.btn_modo.config(text="Paso a paso" if self.todo else "Ver todo")
        self.dibujar()

    def ir(self, d):
        if not self.pasos:
            return
        if self.todo:
            self.todo = False
            self.btn_modo.config(text="Ver todo")
        self.i = max(0, min(len(self.pasos) - 1, self.i + d))
        self.dibujar()

    def dibujar(self):
        cv = self.cv
        cv.delete("all")
        if self.todo:
            y = 10
            for k in range(len(self.pasos)):
                y = self.dibujar_paso(self.pasos[k], k, y, True)
            self.lbl.config(text=f"{len(self.pasos)} pasos")
            self.txt.config(text="Se muestran todos los pasos, de arriba hacia abajo (usa la rueda del ratón "
                                 "o la barra lateral). Pulsa «Paso a paso» para verlos de uno en uno.")
            self.zl.config(text=self.p.formula(self.pasos[-1].asig))
        else:
            ps = self.pasos[self.i]
            self.dibujar_paso(ps, self.i, 10, False)
            self.lbl.config(text=f"Paso {self.i + 1} / {len(self.pasos)}")
            self.txt.config(text=ps.texto)
            self.zl.config(text=self.p.formula(ps.asig))
        cv.configure(scrollregion=cv.bbox("all"))

    def dibujar_paso(self, ps, k, oy, titulo):
        """Dibuja un paso con su esquina superior en oy; devuelve la y donde termina."""
        p, cv = self.p, self.cv
        m, n = p.m, p.n
        W, H, LW, HH = 104, 74, 125, 54
        if titulo:
            cv.create_line(0, oy, 2000, oy, fill="#d1d5db")
            cv.create_text(10, oy + 8, anchor="nw", width=1050, font=BOLD, fill=ACC,
                           text=f"Paso {k + 1}: {ps.texto}\n{p.formula(ps.asig)}")
            oy += 88
        top = oy + HH
        cic = dict(ps.ciclo) if ps.ciclo else {}
        cx, cy = (lambda j: LW + j * W), (lambda i: top + i * H)
        grey = "#9ca3af"
        for j in range(n):
            t = f"D{j + 1}" + (" (Ficticio)" if p.fict_col and j == n - 1 else "")
            if ps.v:
                t += f"\nv = {fmt(ps.v[j])}"
            cv.create_text(cx(j) + W / 2, oy + HH / 2, text=t, font=BOLD, justify="center",
                           fill=grey if j in ps.tach_c else TXT)
        for i in range(m):
            t = f"O{i + 1}" + (" (Ficticio)" if p.fict_fila and i == m - 1 else "")
            if ps.u:
                t += f"\nu = {fmt(ps.u[i])}"
            cv.create_text(LW / 2, cy(i) + H / 2, text=t, font=BOLD, justify="center",
                           fill=grey if i in ps.tach_f else TXT)
            cv.create_text(cx(n) + W / 2, cy(i) + H / 2, text=fmt(p.oferta[i]), font=(F, 13, "bold"))
        cv.create_text(cx(n) + W / 2, oy + HH / 2, text="Oferta", font=BOLD)
        cv.create_text(LW / 2, cy(m) + H / 2, text="Demanda", font=BOLD)
        for j in range(n):
            cv.create_text(cx(j) + W / 2, cy(m) + H / 2, text=fmt(p.demanda[j]), font=(F, 13, "bold"))
        fin = cy(m) + H
        if ps.penal_f is not None:
            fin = cy(m + 1) + H
            cv.create_text(cx(n + 1) + W / 2, oy + HH / 2, text="Penal. fila", font=BOLD)
            cv.create_text(LW / 2, cy(m + 1) + H / 2, text="Penal. col.", font=BOLD)
            for i, v in ps.penal_f.items():
                cv.create_text(cx(n + 1) + W / 2, cy(i) + H / 2, text=fmt(v), font=(F, 14, "bold"),
                               fill="#dc2626" if ps.marcada == ('f', i) else TXT)
            for j, v in ps.penal_c.items():
                cv.create_text(cx(j) + W / 2, cy(m + 1) + H / 2, text=fmt(v), font=(F, 14, "bold"),
                               fill="#dc2626" if ps.marcada == ('c', j) else TXT)
        cells = [(i, j) for i in range(m) for j in range(n)]
        for i, j in cells:                                   # 1) fondos
            fill = "white"
            if ps.optimo and (i, j) not in ps.asig:
                fill = "#dcfce7"
            if i in ps.tach_f or j in ps.tach_c:
                fill = "#e5e7eb"
            if (i, j) in cic:
                fill = "#dbeafe"
            if ps.actual == (i, j):
                fill = "#fde68a"
            cv.create_rectangle(cx(j), cy(i), cx(j) + W, cy(i) + H, fill=fill, outline="#6b7280", width=1.5)
        if ps.marcada:                                       # línea de penalización elegida
            if ps.marcada[0] == 'f':
                cv.create_rectangle(LW, cy(ps.marcada[1]), cx(n), cy(ps.marcada[1]) + H, outline="#dc2626", width=3)
            else:
                cv.create_rectangle(cx(ps.marcada[1]), top, cx(ps.marcada[1]) + W, cy(m), outline="#dc2626", width=3)
        if cic:                                              # 2) ciclo cerrado
            pts = []
            for (i, j), _ in ps.ciclo:
                pts += [cx(j) + W / 2, cy(i) + H / 2]
            cv.create_line(*pts, pts[0], pts[1], fill=ACC, width=3, dash=(6, 3), arrow="last")
        for i, j in cells:                                   # 3) textos
            x, y = cx(j), cy(i)
            cv.create_rectangle(x + W - 32, y + 3, x + W - 3, y + 22, fill="#f3f4f6", outline="#9ca3af")
            cv.create_text(x + W - 17, y + 12, text=fmt(p.costos[i][j]), font=(F, 9, "bold"))
            if (i, j) in ps.asig:
                q = ps.asig[(i, j)]
                cv.create_text(x + W / 2, y + H / 2 + 4, text="ε" if q <= 0 else fmt(q), font=BIG,
                               fill="#b45309" if q <= 0 else TXT)
            if ps.delta and (i, j) in ps.delta:
                d = ps.delta[(i, j)]
                cv.create_text(x + 8, y + H - 12, anchor="w", text=f"Δ={fmt(d)}", font=(F, 10, "bold"),
                               fill="#dc2626" if d < 0 else "#16a34a")
            if (i, j) in cic:
                s = cic[(i, j)]
                cv.create_text(x + 14, y + 14, text="+" if s > 0 else "−", font=(F, 20, "bold"),
                               fill="#16a34a" if s > 0 else "#dc2626")
        for i in ps.tach_f:
            cv.create_line(LW, cy(i) + H / 2, cx(n), cy(i) + H / 2, fill="#4b5563", width=2)
        for j in ps.tach_c:
            cv.create_line(cx(j) + W / 2, top, cx(j) + W / 2, cy(m), fill="#4b5563", width=2)
        return fin + 30


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("5 Métodos de Transporte — Investigación de Operaciones")
        self.geometry("1180x800")
        self.configure(bg=BG)
        self.iniciales, self.vc, self.vo, self.vd, self.ents = {}, [], [], [], []
        barra = tk.Frame(self, bg=BG)
        barra.pack(fill="x", padx=10, pady=6)
        for t, c in (("＋ Origen", lambda: self.cambiar(1, 0)), ("－ Origen", lambda: self.cambiar(-1, 0)),
                     ("＋ Destino", lambda: self.cambiar(0, 1)), ("－ Destino", lambda: self.cambiar(0, -1)),
                     ("Ejemplo balanceado", lambda: self.ejemplo("balanceado")),
                     ("Ejemplo desbalanceado", lambda: self.ejemplo("desbalanceado")),
                     ("Limpiar tabla", self.limpiar)):
            ttk.Button(barra, text=t, command=c).pack(side="left", padx=3)
        tk.Button(barra, text="▶ Resolver", command=self.resolver, bg=ACC, fg="white", font=BOLD,
                  relief="flat", padx=14, pady=4).pack(side="right", padx=3)
        self.badge = tk.Label(barra, font=BOLD, padx=10, pady=3)
        self.badge.pack(side="right", padx=10)
        self.editor = tk.Frame(self, bg=BG)
        self.editor.pack(fill="x", padx=14, pady=4)
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=8)
        self.visores = []
        for titulo, fn, opt in (("1. Esquina Noroeste", esquina_noroeste.resolver, False),
                                ("2. Costo Mínimo", costo_minimo.resolver, False),
                                ("3. Vogel", miguel.resolver, False),
                                ("4. Banquillo", banquillo.resolver, True),
                                ("5. DIMO (MODI)", dimo.resolver, True)):
            v = Visor(self.nb, fn, opt, self)
            self.nb.add(v, text=titulo)
            self.visores.append(v)
        comp = tk.Frame(self.nb, bg=BG)
        self.nb.add(comp, text="6. Comparativa Final")
        cols = ("Método SBFI", "Z inicial", "Iter. Banquillo", "Iter. DIMO", "Z óptimo", "Sobrecosto inicial")
        self.tree = ttk.Treeview(comp, columns=cols, show="headings", height=5)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", width=160)
        self.tree.pack(fill="x", padx=10, pady=12)
        self.resumen = tk.Label(comp, bg=BG, fg="#065f46", font=(F, 11, "bold"), justify="left",
                                anchor="w", wraplength=1050)
        self.resumen.pack(fill="x", padx=10)
        self.ejemplo("balanceado")

    # ---------- editor ----------
    def crudo(self):
        return ([[v.get() for v in r] for r in self.vc], [v.get() for v in self.vo], [v.get() for v in self.vd])

    def construir(self, c, o, d):
        for w in self.editor.winfo_children():
            w.destroy()
        self.vc, self.vo, self.vd, self.ents = [], [], [], []
        m, n = len(o), len(d)

        def entrada(r, col, val, lista_v):
            v = tk.StringVar(value=str(val))
            v.trace_add("write", lambda *a: self.actualizar())
            e = tk.Entry(self.editor, textvariable=v, width=7, justify="center", font=(F, 11),
                         relief="solid", bd=1)
            e.grid(row=r, column=col, padx=2, pady=2)
            self.ents.append((v, e))
            lista_v.append(v)
            return v

        for j in range(n):
            tk.Label(self.editor, text=f"D{j + 1}", bg=BG, font=BOLD).grid(row=0, column=j + 1)
        tk.Label(self.editor, text="Oferta", bg=BG, font=BOLD).grid(row=0, column=n + 1)
        for i in range(m):
            tk.Label(self.editor, text=f"O{i + 1}", bg=BG, font=BOLD).grid(row=i + 1, column=0)
            fila = []
            for j in range(n):
                entrada(i + 1, j + 1, c[i][j], fila)
            self.vc.append(fila)
            entrada(i + 1, n + 1, o[i], self.vo)
        tk.Label(self.editor, text="Demanda", bg=BG, font=BOLD).grid(row=m + 1, column=0)
        for j in range(n):
            entrada(m + 1, j + 1, d[j], self.vd)
        self.actualizar()

    @staticmethod
    def valido(s):
        try:
            return float(s) >= 0
        except ValueError:
            return False

    def actualizar(self):
        ok = True
        for v, e in self.ents:
            bien = self.valido(v.get())
            ok &= bien
            e.config(bg="white" if bien else "#fecaca")
        if not ok:
            self.badge.config(text="Valores vacíos o negativos", bg="#fecaca", fg="#991b1b")
            return
        so = sum(float(v.get()) for v in self.vo)
        sd = sum(float(v.get()) for v in self.vd)
        if abs(so - sd) < 1e-9:
            self.badge.config(text=f"Balanceado  (Oferta {fmt(so)} = Demanda {fmt(sd)})", bg="#bbf7d0", fg="#166534")
        else:
            falta = "destino" if so > sd else "origen"
            self.badge.config(text=f"Desbalanceado ({fmt(so)} vs {fmt(sd)}): se agregará {falta} ficticio",
                              bg="#fef08a", fg="#854d0e")

    def cambiar(self, df, dc):
        c, o, d = self.crudo()
        if df > 0:
            c.append(["0"] * len(d)); o.append("0")
        elif df < 0 and len(o) > 1:
            c.pop(); o.pop()
        if dc > 0:
            for r in c: r.append("0")
            d.append("0")
        elif dc < 0 and len(d) > 1:
            for r in c: r.pop()
            d.pop()
        self.construir(c, o, d)

    def ejemplo(self, k):
        self.construir(*EJEMPLOS[k])

    def limpiar(self):
        c, o, d = self.crudo()
        self.construir([["0"] * len(d) for _ in o], ["0"] * len(o), ["0"] * len(d))

    def leer(self):
        c, o, d = self.crudo()
        if not all(self.valido(x) for x in sum(c, []) + o + d):
            raise ValueError("Todas las celdas deben tener números no negativos.")
        f = lambda x: [(int(float(s)) if float(s).is_integer() else float(s)) for s in x]
        if sum(f(o)) <= 0 or sum(f(d)) <= 0:
            raise ValueError("La oferta y la demanda totales deben ser mayores que 0.")
        return [f(r) for r in c], f(o), f(d)

    # ---------- resolver ----------
    def resolver(self):
        try:
            c, o, d = self.leer()
        except ValueError as e:
            return messagebox.showerror("Datos inválidos", str(e))
        p = Problema(c, o, d).balanceado()
        self.iniciales = {}
        self.tree.delete(*self.tree.get_children())
        res = []
        for nombre, mod in INICIALES.items():
            a0 = mod.resolver(p)[-1].asig
            self.iniciales[nombre] = a0
            b, dm = banquillo.resolver(p, a0), dimo.resolver(p, a0)
            z0, zo = p.costo(a0), p.costo(dm[-1].asig)
            extra = f"{(z0 - zo) / zo * 100:.1f} %" if zo else "0 %"
            self.tree.insert("", "end", values=(nombre, fmt(z0), len(b) - 1, len(dm) - 1, fmt(zo), extra))
            res.append((z0, nombre, dm[-1].asig))
        z0, mejor, asig = min(res, key=lambda r: r[0])
        self.resumen.config(text=f"Mejor SBFI: {mejor} (Z inicial = {fmt(z0)}).\n"
                                 f"Solución óptima — {p.formula(asig)}")
        for v in self.visores:
            v.cargar(p)
        self.nb.select(0)


def iniciar():
    App().mainloop()
