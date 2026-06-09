import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tracker import Combattente, Combattimento, salva_combattimento, carica_combattimento

# ── PALETTE ──────────────────────────────────────────────────────────────────
BG      = "#0f0f1a"
SURFACE = "#1a1a2e"
CARD    = "#16213e"
GOLD    = "#f5a623"
RED     = "#e94560"
GREEN   = "#4caf7d"
BLUE    = "#5b8dee"
PURPLE  = "#9b59b6"
TEXT    = "#e8e0d5"
MUTED   = "#7a8fa6"
ORANGE  = "#e67e22"
FM      = "Courier"


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("⚔️  D&D Combat Tracker")
        self.root.geometry("1280x800")
        self.root.configure(bg=BG)
        self.root.minsize(900, 600)

        self.combattimento = Combattimento()
        self.selezionato: int | None = None

        self._build_ui()
        self._refresh()

    # ── UI CONSTRUCTION ───────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        corpo = tk.Frame(self.root, bg=BG)
        corpo.pack(fill="both", expand=True)
        # Right must be packed before center (pack side="right" order)
        self._build_col_sinistra(corpo)
        self._build_col_destra(corpo)
        self._build_col_centro(corpo)

    def _build_header(self):
        h = tk.Frame(self.root, bg=SURFACE, height=62)
        h.pack(fill="x")
        h.pack_propagate(False)

        self.lbl_round = tk.Label(h, text="Round 1", bg=SURFACE, fg=GOLD,
                                   font=(FM, 18, "bold"))
        self.lbl_round.pack(side="left", padx=20)

        self.lbl_turno = tk.Label(h, text="Turno di: —", bg=SURFACE, fg=MUTED,
                                   font=(FM, 10))
        self.lbl_turno.pack(side="left", padx=12)

        bs = dict(font=(FM, 10, "bold"), relief="flat", padx=14, pady=5, cursor="hand2")

        tk.Button(h, text="Turno Successivo ▶", bg=GOLD, fg="#111",
                  command=self._prossimo_turno, **bs).pack(side="left", padx=14)
        tk.Button(h, text="↕ Ordina Init", bg=CARD, fg=TEXT,
                  command=self._ordina, **bs).pack(side="left", padx=4)

        tk.Button(h, text="📂 Carica", bg=CARD, fg=TEXT,
                  command=self._carica, **bs).pack(side="right", padx=10)
        tk.Button(h, text="💾 Salva", bg=CARD, fg=TEXT,
                  command=self._salva, **bs).pack(side="right", padx=4)
        tk.Button(h, text="🗑 Reset", bg="#2a1010", fg=RED,
                  command=self._reset, **bs).pack(side="right", padx=4)

    def _build_col_sinistra(self, parent):
        col = tk.Frame(parent, bg=SURFACE, width=240)
        col.pack(side="left", fill="y")
        col.pack_propagate(False)

        tk.Label(col, text="➕ Nuovo Combattente", bg=SURFACE, fg=GOLD,
                 font=(FM, 11, "bold")).pack(pady=(16, 4))
        tk.Frame(col, bg=GOLD, height=1).pack(fill="x", padx=16, pady=2)

        ff = tk.Frame(col, bg=SURFACE)
        ff.pack(fill="x", padx=16, pady=6)
        ff.columnconfigure(0, weight=1)

        lbl_s = dict(bg=SURFACE, fg=MUTED, font=(FM, 8), anchor="w")
        ent_s = dict(bg=CARD, fg=TEXT, font=(FM, 11),
                     insertbackground=TEXT, relief="flat", bd=6)

        self.v_nome   = tk.StringVar()
        self.v_ca     = tk.StringVar(value="10")
        self.v_hp     = tk.StringVar(value="10")
        self.v_init   = tk.StringVar(value="10")
        self.v_hptemp = tk.StringVar(value="0")

        fields = [
            ("Nome", self.v_nome),
            ("CA", self.v_ca),
            ("HP Massimi", self.v_hp),
            ("Iniziativa", self.v_init),
            ("HP Temporanei (opz.)", self.v_hptemp),
        ]
        for i, (label, var) in enumerate(fields):
            tk.Label(ff, text=label, **lbl_s).grid(row=i*2,   column=0, sticky="w", pady=(6, 0))
            tk.Entry(ff, textvariable=var, **ent_s).grid(row=i*2+1, column=0, sticky="ew", ipady=4)

        tk.Button(col, text="➕ Aggiungi al Combattimento",
                  bg=GREEN, fg="#111", font=(FM, 10, "bold"),
                  relief="flat", cursor="hand2", pady=8,
                  command=self._aggiungi).pack(fill="x", padx=16, pady=12)

        tk.Frame(col, bg=MUTED, height=1).pack(fill="x", padx=16, pady=4)
        tk.Label(col, text="⚡ Preset veloci", bg=SURFACE, fg=MUTED,
                 font=(FM, 8, "bold")).pack(pady=(4, 4))

        presets = [
            ("Goblin",    13,  7, 3),
            ("Scheletro", 13, 13, 4),
            ("Zombie",     8, 22, 2),
            ("Orco",      13, 15, 2),
            ("Troll",     15, 84, 0),
            ("Drago",     19, 256, 5),
        ]
        for nome, ca, hp, init in presets:
            tk.Button(col, text=f"  {nome:<12}CA:{ca:<4}HP:{hp}",
                      bg=CARD, fg=TEXT, font=(FM, 9), relief="flat",
                      cursor="hand2", anchor="w", padx=8, pady=3,
                      command=lambda n=nome, c=ca, h=hp, i=init: self._preset(n, c, h, i)
                      ).pack(fill="x", padx=12, pady=1)

    def _build_col_centro(self, parent):
        col = tk.Frame(parent, bg=BG)
        col.pack(side="left", fill="both", expand=True)

        tk.Label(col, text="⚔️  Ordine di Iniziativa", bg=BG, fg=MUTED,
                 font=(FM, 9)).pack(anchor="w", padx=20, pady=8)

        cf = tk.Frame(col, bg=BG)
        cf.pack(fill="both", expand=True, padx=8, pady=4)

        self.canvas = tk.Canvas(cf, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(cf, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.cards_frame = tk.Frame(self.canvas, bg=BG)
        self._cw = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")

        self.cards_frame.bind(
            "<Configure>",
            lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self._cw, width=e.width))
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def _build_col_destra(self, parent):
        col = tk.Frame(parent, bg=SURFACE, width=300)
        col.pack(side="right", fill="y")
        col.pack_propagate(False)
        self.detail_frame = col
        self._build_detail_empty()

    # ── DETAIL PANEL ─────────────────────────────────────────────────────────

    def _build_detail_empty(self):
        for w in self.detail_frame.winfo_children():
            w.destroy()
        tk.Label(self.detail_frame, text="⚙️ Dettaglio", bg=SURFACE, fg=GOLD,
                 font=(FM, 11, "bold")).pack(pady=(16, 4))
        tk.Frame(self.detail_frame, bg=GOLD, height=1).pack(fill="x", padx=16, pady=2)
        tk.Label(self.detail_frame,
                 text="Clicca su un\ncombattente\nper i dettagli.",
                 bg=SURFACE, fg=MUTED, font=(FM, 10)).pack(expand=True)

    def _build_detail(self, idx: int):
        if idx >= len(self.combattimento.combattenti):
            self._build_detail_empty()
            return

        c = self.combattimento.combattenti[idx]
        for w in self.detail_frame.winfo_children():
            w.destroy()

        f = self.detail_frame
        es = dict(bg=CARD, fg=TEXT, font=(FM, 11),
                  insertbackground=TEXT, relief="flat", bd=6, width=7)
        bs = dict(font=(FM, 9, "bold"), relief="flat", cursor="hand2", padx=10, pady=5)

        tk.Label(f, text="⚙️ Dettaglio", bg=SURFACE, fg=GOLD,
                 font=(FM, 11, "bold")).pack(pady=(16, 4))
        tk.Frame(f, bg=GOLD, height=1).pack(fill="x", padx=16, pady=2)
        tk.Label(f, text=c.nome, bg=SURFACE, fg=TEXT,
                 font=(FM, 13, "bold"), wraplength=270).pack(pady=(10, 4))

        # Stats boxes
        stats = tk.Frame(f, bg=SURFACE)
        stats.pack(pady=4)
        pct = c.hpAttuali / c.hpMassimi if c.hpMassimi else 0
        hp_col = GREEN if pct > 0.5 else (ORANGE if pct > 0.25 else RED)

        def sbox(parent, lbl, val, col):
            b = tk.Frame(parent, bg=CARD, padx=10, pady=6)
            b.pack(side="left", padx=3)
            tk.Label(b, text=lbl, bg=CARD, fg=MUTED, font=(FM, 7)).pack()
            tk.Label(b, text=str(val), bg=CARD, fg=col, font=(FM, 13, "bold")).pack()

        sbox(stats, "INIT", c.iniziativa, PURPLE)
        sbox(stats, "CA",   c.ca,          BLUE)
        sbox(stats, "HP",   f"{c.hpAttuali}/{c.hpMassimi}", hp_col)
        if c.hpTemporanei > 0:
            sbox(stats, "TEMP", c.hpTemporanei, GOLD)

        self._draw_hp_bar(f, c, width=268)

        def sep():
            tk.Frame(f, bg=MUTED, height=1).pack(fill="x", padx=16, pady=6)

        def sec(txt):
            tk.Label(f, text=txt, bg=SURFACE, fg=MUTED,
                     font=(FM, 8, "bold")).pack(anchor="w", padx=16, pady=(4, 2))

        # Damage
        sep()
        sec("💥  DANNO")
        row = tk.Frame(f, bg=SURFACE)
        row.pack(fill="x", padx=16)
        self.v_danno = tk.StringVar(value="1")
        tk.Entry(row, textvariable=self.v_danno, **es).pack(side="left")
        tk.Button(row, text="Applica", bg=RED, fg="white",
                  command=lambda: self._danno(idx), **bs).pack(side="left", padx=6)

        # Heal
        sep()
        sec("💚  CURA")
        row = tk.Frame(f, bg=SURFACE)
        row.pack(fill="x", padx=16)
        self.v_cura = tk.StringVar(value="1")
        tk.Entry(row, textvariable=self.v_cura, **es).pack(side="left")
        tk.Button(row, text="Cura", bg=GREEN, fg="#111",
                  command=lambda: self._cura(idx), **bs).pack(side="left", padx=6)

        # Temp HP
        sep()
        sec("🛡  HP TEMPORANEI")
        row = tk.Frame(f, bg=SURFACE)
        row.pack(fill="x", padx=16)
        self.v_temp_d = tk.StringVar(value="0")
        tk.Entry(row, textvariable=self.v_temp_d, **es).pack(side="left")
        tk.Button(row, text="Aggiungi", bg=BLUE, fg="white",
                  command=lambda: self._temp_hp(idx), **bs).pack(side="left", padx=6)

        # Initiative
        sep()
        sec("⚡  INIZIATIVA")
        row = tk.Frame(f, bg=SURFACE)
        row.pack(fill="x", padx=16)
        self.v_init_d = tk.StringVar(value=str(c.iniziativa))
        tk.Entry(row, textvariable=self.v_init_d, **es).pack(side="left")
        tk.Button(row, text="Aggiorna", bg=PURPLE, fg="white",
                  command=lambda: self._aggiorna_init(idx), **bs).pack(side="left", padx=6)

        # Conditions
        sep()
        sec("⚠️  CONDIZIONI")
        crow = tk.Frame(f, bg=SURFACE)
        crow.pack(fill="x", padx=16, pady=(0, 4))

        self.v_cond_n = tk.StringVar()
        self.v_cond_d = tk.StringVar(value="1")

        cond_name_ent = tk.Entry(crow, textvariable=self.v_cond_n,
                                  bg=CARD, fg=MUTED, font=(FM, 9),
                                  insertbackground=TEXT, relief="flat", bd=4, width=11)
        cond_name_ent.insert(0, "nome...")
        cond_name_ent.bind("<FocusIn>", lambda _: (
            cond_name_ent.delete(0, "end"),
            cond_name_ent.configure(fg=TEXT)
        ))
        cond_name_ent.pack(side="left")

        tk.Entry(crow, textvariable=self.v_cond_d,
                 bg=CARD, fg=TEXT, font=(FM, 9),
                 insertbackground=TEXT, relief="flat", bd=4, width=3
                 ).pack(side="left", padx=4)
        tk.Label(crow, text="R", bg=SURFACE, fg=MUTED, font=(FM, 8)).pack(side="left")
        tk.Button(crow, text="Add", bg=ORANGE, fg="#111",
                  command=lambda: self._add_cond(idx), **bs).pack(side="left", padx=4)

        self.cond_list = tk.Frame(f, bg=SURFACE)
        self.cond_list.pack(fill="x", padx=16)
        self._redraw_cond_list(idx)

        sep()
        tk.Button(f, text="🗑  Rimuovi dal Combattimento",
                  bg="#2a1010", fg=RED, font=(FM, 9), relief="flat",
                  cursor="hand2", pady=6,
                  command=lambda: self._rimuovi(idx)).pack(fill="x", padx=16, pady=6)

    def _draw_hp_bar(self, parent, c: Combattente, width=240):
        H = 14
        canvas = tk.Canvas(parent, width=width, height=H,
                            bg="#0a0a14", highlightthickness=0)
        canvas.pack(pady=(4, 8))

        pct = max(0.0, min(1.0, c.hpAttuali / c.hpMassimi if c.hpMassimi else 0))
        col = GREEN if pct > 0.5 else (ORANGE if pct > 0.25 else RED)

        if pct > 0:
            canvas.create_rectangle(0, 0, int(width * pct), H, fill=col, outline="")
        if c.hpTemporanei > 0:
            tp = min(1.0 - pct, c.hpTemporanei / c.hpMassimi)
            x0, x1 = int(width * pct), min(width, int(width * pct) + int(width * tp))
            if x1 > x0:
                canvas.create_rectangle(x0, 0, x1, H, fill=GOLD, outline="")

        canvas.create_text(width // 2, H // 2,
                            text=f"{c.hpAttuali}/{c.hpMassimi}",
                            fill="white", font=(FM, 8, "bold"))

    def _redraw_cond_list(self, idx: int):
        for w in self.cond_list.winfo_children():
            w.destroy()
        c = self.combattimento.combattenti[idx]
        if not c.condizioni:
            tk.Label(self.cond_list, text="Nessuna condizione attiva.",
                     bg=SURFACE, fg=MUTED, font=(FM, 8)).pack(anchor="w")
            return
        for cond in c.condizioni:
            r = tk.Frame(self.cond_list, bg=CARD, padx=6, pady=3)
            r.pack(fill="x", pady=1)
            tk.Label(r, text=f"⚠ {cond['Condizione']}  ({cond['Durata']}R)",
                     bg=CARD, fg=ORANGE, font=(FM, 9)).pack(side="left")
            tk.Button(r, text="✕", bg=CARD, fg=RED, font=(FM, 9),
                      relief="flat", cursor="hand2",
                      command=lambda cn=cond['Condizione']: self._rm_cond(idx, cn)
                      ).pack(side="right")

    # ── CARD RENDERING ────────────────────────────────────────────────────────

    def _refresh(self):
        comb = self.combattimento.combattenti
        self.lbl_round.configure(text=f"Round {self.combattimento.round_attuale}")
        if comb:
            self.lbl_turno.configure(
                text=f"Turno di: {comb[self.combattimento.turno_attuale].nome}")
        else:
            self.lbl_turno.configure(text="Turno di: —")

        for w in self.cards_frame.winfo_children():
            w.destroy()

        if not comb:
            tk.Label(self.cards_frame,
                     text="Nessun combattente in campo.\nUsa il pannello sinistro per aggiungerne.",
                     bg=BG, fg=MUTED, font=(FM, 11)).pack(pady=80, padx=40)
            return

        for i, c in enumerate(comb):
            self._make_card(i, c)

    def _make_card(self, idx: int, c: Combattente):
        turno       = self.combattimento.turno_attuale
        is_active   = (idx == turno)
        is_selected = (idx == self.selezionato)

        border_col  = GOLD if is_active else (BLUE if is_selected else "#252545")
        pad         = 2 if (is_active or is_selected) else 1

        outer = tk.Frame(self.cards_frame, bg=border_col, padx=pad, pady=pad)
        outer.pack(fill="x", padx=12, pady=4)

        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both")

        def click(_=None, i=idx):
            self.selezionato = i
            self._build_detail(i)
            self._refresh()

        # Initiative badge
        badge_bg = GOLD if is_active else ("#2a2a4e" if is_selected else "#1c1c30")
        badge_fg = "#111" if is_active else (BLUE if is_selected else MUTED)

        badge = tk.Frame(inner, bg=badge_bg, width=56)
        badge.pack(side="left", fill="y")
        badge.pack_propagate(False)
        tk.Label(badge, text=str(c.iniziativa),
                 bg=badge_bg, fg=badge_fg,
                 font=(FM, 22, "bold")).pack(expand=True)

        # Body
        body = tk.Frame(inner, bg=CARD, padx=12, pady=8)
        body.pack(side="left", fill="both", expand=True)

        # Name row
        top = tk.Frame(body, bg=CARD)
        top.pack(fill="x")
        prefix = "▶ " if is_active else ""
        tk.Label(top, text=f"{prefix}{c.nome}",
                 bg=CARD, fg=GOLD if is_active else TEXT,
                 font=(FM, 12, "bold"), anchor="w").pack(side="left")
        if c.hpAttuali == 0:
            tk.Label(top, text="☠ KO", bg=CARD, fg=RED,
                     font=(FM, 9, "bold")).pack(side="right", padx=8)
        tk.Label(top, text=f"CA {c.ca}",
                 bg=CARD, fg=BLUE, font=(FM, 9)).pack(side="right")

        # HP bar
        pct = max(0.0, min(1.0, c.hpAttuali / c.hpMassimi if c.hpMassimi else 0))
        hp_col = GREEN if pct > 0.5 else (ORANGE if pct > 0.25 else RED)

        hp_row = tk.Frame(body, bg=CARD)
        hp_row.pack(fill="x", pady=4)

        BW, BH = 210, 10
        bar = tk.Canvas(hp_row, width=BW, height=BH, bg="#0a0a14", highlightthickness=0)
        bar.pack(side="left")
        if pct > 0:
            bar.create_rectangle(0, 0, int(BW * pct), BH, fill=hp_col, outline="")
        if c.hpTemporanei > 0:
            tp = min(1.0 - pct, c.hpTemporanei / c.hpMassimi)
            x0, x1 = int(BW * pct), min(BW, int(BW * pct) + int(BW * tp))
            if x1 > x0:
                bar.create_rectangle(x0, 0, x1, BH, fill=GOLD, outline="")

        hp_str = f"{c.hpAttuali}/{c.hpMassimi}"
        if c.hpTemporanei:
            hp_str += f"  +{c.hpTemporanei}♦"
        tk.Label(hp_row, text=hp_str, bg=CARD, fg=hp_col,
                 font=(FM, 9)).pack(side="left", padx=8)

        # Condition tags
        if c.condizioni:
            cr = tk.Frame(body, bg=CARD)
            cr.pack(fill="x")
            for cond in c.condizioni:
                tk.Label(cr,
                         text=f" {cond['Condizione']} {cond['Durata']}R ",
                         bg="#3a2000", fg=ORANGE,
                         font=(FM, 8), padx=2, pady=1
                         ).pack(side="left", padx=2, pady=2)

        self._bind_recursive(inner, click)

    def _bind_recursive(self, widget, callback):
        widget.bind("<Button-1>", callback)
        try:
            widget.configure(cursor="hand2")
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._bind_recursive(child, callback)

    # ── ACTIONS ───────────────────────────────────────────────────────────────

    def _aggiungi(self):
        nome = self.v_nome.get().strip()
        if not nome:
            messagebox.showwarning("Attenzione", "Inserisci un nome per il combattente.")
            return
        try:
            ca   = int(self.v_ca.get())
            hp   = int(self.v_hp.get())
            init = int(self.v_init.get())
            temp = int(self.v_hptemp.get() or 0)
        except ValueError:
            messagebox.showwarning("Errore", "CA, HP e Iniziativa devono essere numeri interi.")
            return

        self.combattimento.aggiungere_combattente(Combattente(nome, ca, hp, hp, temp, init))
        self.v_nome.set("")
        self.v_ca.set("10")
        self.v_hp.set("10")
        self.v_init.set("10")
        self.v_hptemp.set("0")
        self._refresh()

    def _preset(self, nome, ca, hp, init):
        self.combattimento.aggiungere_combattente(Combattente(nome, ca, hp, hp, 0, init))
        self._refresh()

    def _prossimo_turno(self):
        if not self.combattimento.combattenti:
            return
        self.combattimento.prossimo_turno()
        self._refresh()
        if self.selezionato is not None:
            self._build_detail(self.selezionato)

    def _ordina(self):
        self.combattimento.ordinare_iniziativa()
        self._refresh()

    def _reset(self):
        if messagebox.askyesno("Reset", "Resettare il combattimento? Tutti i dati verranno persi."):
            self.combattimento = Combattimento()
            self.selezionato = None
            self._build_detail_empty()
            self._refresh()

    def _danno(self, idx):
        try:
            d = int(self.v_danno.get())
            if d < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Errore", "Inserisci un valore intero non negativo.")
            return
        self.combattimento.combattenti[idx].subire_danno(d)
        self._refresh()
        self._build_detail(idx)

    def _cura(self, idx):
        try:
            v = int(self.v_cura.get())
            if v < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Errore", "Inserisci un valore intero non negativo.")
            return
        self.combattimento.combattenti[idx].curare(v)
        self._refresh()
        self._build_detail(idx)

    def _temp_hp(self, idx):
        try:
            v = int(self.v_temp_d.get())
        except ValueError:
            return
        self.combattimento.combattenti[idx].aggiungere_hp_temporanei(v)
        self._refresh()
        self._build_detail(idx)

    def _aggiorna_init(self, idx):
        try:
            v = int(self.v_init_d.get())
        except ValueError:
            messagebox.showwarning("Errore", "Inserisci un numero intero per l'iniziativa.")
            return
        target = self.combattimento.combattenti[idx]
        target.iniziativa = v
        self.combattimento.ordinare_iniziativa()
        new_idx = self.combattimento.combattenti.index(target)
        self.selezionato = new_idx
        self._refresh()
        self._build_detail(new_idx)

    def _add_cond(self, idx):
        nome = self.v_cond_n.get().strip()
        if not nome or nome == "nome...":
            return
        try:
            durata = int(self.v_cond_d.get())
        except ValueError:
            durata = 1
        self.combattimento.combattenti[idx].aggiungere_condizione(nome, durata)
        self.v_cond_n.set("")
        self._refresh()
        self._build_detail(idx)

    def _rm_cond(self, idx, nome_cond):
        self.combattimento.combattenti[idx].rimuovere_condizione(nome_cond)
        self._refresh()
        self._build_detail(idx)

    def _rimuovi(self, idx):
        del self.combattimento.combattenti[idx]
        n = len(self.combattimento.combattenti)
        if n == 0:
            self.combattimento.turno_attuale = 0
        elif self.combattimento.turno_attuale >= n:
            self.combattimento.turno_attuale = 0
        self.selezionato = None
        self._build_detail_empty()
        self._refresh()

    def _salva(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Tutti i file", "*.*")],
            title="Salva combattimento"
        )
        if path:
            salva_combattimento(self.combattimento, path)
            messagebox.showinfo("Salvato", f"Combattimento salvato in:\n{path}")

    def _carica(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("Tutti i file", "*.*")],
            title="Carica combattimento"
        )
        if path:
            try:
                self.combattimento = carica_combattimento(path)
                self.selezionato = None
                self._build_detail_empty()
                self._refresh()
            except Exception as e:
                messagebox.showerror("Errore di caricamento", str(e))


# ── AVVIA ─────────────────────────────────────────────────────────────────────
root = tk.Tk()
App(root)
root.mainloop()
