"""
alerts.py – Stock alerts and expiry warnings
"""

import tkinter as tk
from tkinter import ttk

BG_DARK   = "#1A1A2E"
BG_PANEL  = "#16213E"
BG_CARD   = "#0F3460"
ACCENT    = "#E94560"
GREEN     = "#00B894"
YELLOW    = "#FDCB6E"
RED       = "#E17055"
TEXT_MAIN = "#EAEAEA"
TEXT_DIM  = "#A0A0B0"


class AlertFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=BG_DARK)
        self.db = db
        self._build()

    def _build(self):
        tk.Label(self, text="⚠️  Stock & Expiry Alerts",
                 font=("Segoe UI", 16, "bold"), bg=BG_DARK, fg=TEXT_MAIN
                 ).pack(pady=(20, 4), anchor="w", padx=24)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=24, pady=12)

        self.tabs = {}
        for label, color in [
            ("❌ Out of Stock",    RED),
            ("⚠️ Low Stock",      YELLOW),
            ("🕐 Expiring Soon",  "#E67E22"),
            ("💀 Expired",        "#636E72"),
        ]:
            f = tk.Frame(nb, bg=BG_PANEL)
            nb.add(f, text=label)
            self.tabs[label] = self._build_tab(f, color)

        self.refresh()

    def _build_tab(self, parent, row_color):
        cols = ("ID", "Product", "Category", "Qty", "Reorder", "Expiry", "Supplier")
        tree = ttk.Treeview(parent, columns=cols, show="headings",
                            height=20, style="Custom.Treeview")
        widths = [90, 180, 150, 70, 80, 110, 160]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")
        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        sb.pack(side="right", fill="y", pady=8)

        style = ttk.Style()
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
        return tree

    def _populate(self, tree, df):
        for row in tree.get_children():
            tree.delete(row)
        for _, r in df.iterrows():
            tree.insert("", "end", values=(
                r["product_id"], r["product_name"], r["category"],
                int(r["quantity"]), int(r["reorder_level"]),
                r["expiry_date"], r["supplier"]
            ))

    def refresh(self):
        keys = list(self.tabs.keys())
        dfs  = [
            self.db.get_all()[self.db.get_all()["quantity"] == 0],
            self.db.get_low_stock(),
            self.db.get_expiring_soon(),
            self.db.get_expired(),
        ]
        for key, df in zip(keys, dfs):
            self._populate(self.tabs[key], df)
