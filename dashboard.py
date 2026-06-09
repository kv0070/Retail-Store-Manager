"""
dashboard.py – Summary cards + quick stats
"""

import tkinter as tk
from tkinter import ttk

BG_DARK  = "#1A1A2E"
BG_PANEL = "#16213E"
BG_CARD  = "#0F3460"
ACCENT   = "#E94560"
GREEN    = "#00B894"
YELLOW   = "#FDCB6E"
RED      = "#E17055"
BLUE     = "#74B9FF"
PURPLE   = "#A29BFE"
TEXT_MAIN = "#EAEAEA"
TEXT_DIM  = "#A0A0B0"


class StatCard(tk.Frame):
    """A colourful KPI card."""
    def __init__(self, parent, title, value, color, icon, **kwargs):
        super().__init__(parent, bg=color, **kwargs)
        self.configure(relief="flat", bd=0)

        tk.Label(self, text=icon, font=("Segoe UI", 26),
                 bg=color, fg="white").pack(pady=(18, 0))
        self.val_lbl = tk.Label(self, text=str(value),
                                font=("Segoe UI", 28, "bold"), bg=color, fg="white")
        self.val_lbl.pack()
        tk.Label(self, text=title, font=("Segoe UI", 10),
                 bg=color, fg="#DDDDDD").pack(pady=(0, 18))

    def update_value(self, v):
        self.val_lbl.configure(text=str(v))


class DashboardFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=BG_DARK)
        self.db = db
        self._build()

    def _build(self):
        # Title
        tk.Label(self, text="📊  Dashboard  –  Live Inventory Overview",
                 font=("Segoe UI", 16, "bold"), bg=BG_DARK, fg=TEXT_MAIN
                 ).pack(pady=(20, 4), anchor="w", padx=24)
        tk.Label(self, text="Real-time statistics pulled from database",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_DIM
                 ).pack(anchor="w", padx=24)

        # Cards container
        self.cards_frame = tk.Frame(self, bg=BG_DARK)
        self.cards_frame.pack(fill="x", padx=24, pady=20)

        card_specs = [
            ("Total Products",    "0", BG_CARD,  "📦", "total_products"),
            ("Categories",        "0", ACCENT2,  "🗂️",  "total_categories"),
            ("Low Stock Items",   "0", YELLOW,   "⚠️",  "low_stock"),
            ("Out of Stock",      "0", RED,      "❌", "out_of_stock"),
            ("Expiring Soon",     "0", "#E67E22","🕐", "expiring_soon"),
            ("Inventory Value ₹", "0", GREEN,    "💰", "total_value"),
        ]
        self.cards = {}
        for i, (title, val, color, icon, key) in enumerate(card_specs):
            c = StatCard(self.cards_frame, title, val, color, icon,
                         width=180, height=160)
            c.grid(row=0, column=i, padx=10, pady=6, sticky="nsew")
            self.cards_frame.columnconfigure(i, weight=1)
            self.cards[key] = c

        # Recent products table
        tk.Label(self, text="📋  Recent Inventory (Top 15)",
                 font=("Segoe UI", 13, "bold"), bg=BG_DARK, fg=TEXT_MAIN
                 ).pack(anchor="w", padx=24, pady=(10, 4))

        tbl_frame = tk.Frame(self, bg=BG_PANEL)
        tbl_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        cols = ("ID", "Product", "Category", "Qty", "Price ₹", "Reorder Lvl", "Status")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                 height=10, style="Custom.Treeview")

        widths = [90, 170, 150, 60, 90, 100, 90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Tag colours
        self.tree.tag_configure("low",  background="#4D3800", foreground=YELLOW)
        self.tree.tag_configure("out",  background="#4D1C1C", foreground=RED)
        self.tree.tag_configure("ok",   background="#1A3A2A", foreground=GREEN)

        self._apply_style()
        self.refresh()

    def _apply_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=BG_PANEL, foreground=TEXT_MAIN,
                        fieldbackground=BG_PANEL, rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("Custom.Treeview.Heading",
                        background=BG_CARD, foreground=TEXT_MAIN,
                        font=("Segoe UI", 9, "bold"))
        style.map("Custom.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

    def refresh(self):
        summary = self.db.get_summary()
        for key, card in self.cards.items():
            v = summary.get(key, 0)
            if key == "total_value":
                card.update_value(f"₹{v:,.0f}")
            else:
                card.update_value(v)

        # Reload table
        for row in self.tree.get_children():
            self.tree.delete(row)
        df = self.db.get_all().head(15)
        for _, r in df.iterrows():
            qty = int(r["quantity"])
            rl  = int(r["reorder_level"])
            if qty == 0:
                tag, status = "out", "Out of Stock"
            elif qty < rl:
                tag, status = "low", "Low Stock"
            else:
                tag, status = "ok", "In Stock"
            self.tree.insert("", "end", tags=(tag,), values=(
                r["product_id"], r["product_name"], r["category"],
                qty, f"₹{float(r['price']):.2f}", rl, status
            ))


# ── Dark purple accent used in sidebar ───────────────────────────────────
ACCENT2 = "#533483"
