"""
products.py – Full CRUD for inventory products
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

BG_DARK   = "#1A1A2E"
BG_PANEL  = "#16213E"
BG_CARD   = "#0F3460"
ACCENT    = "#E94560"
GREEN     = "#00B894"
YELLOW    = "#FDCB6E"
RED       = "#E17055"
TEXT_MAIN = "#EAEAEA"
TEXT_DIM  = "#A0A0B0"
ENTRY_BG  = "#0D2137"

CATEGORIES = [
    "Grains & Pulses", "Spices & Masalas", "Dairy Products",
    "Oils & Fats", "Snacks & Biscuits", "Beverages",
    "Personal Care", "Vegetables", "Fruits", "Packaged Foods",
]
UNITS = ["kg", "L", "pcs", "g", "ml", "pack"]


class ProductFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=BG_DARK)
        self.db = db
        self._selected_id = None
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────
    def _build(self):
        tk.Label(self, text="📦  Product Management  –  Add / Edit / Delete",
                 font=("Segoe UI", 16, "bold"), bg=BG_DARK, fg=TEXT_MAIN
                 ).pack(pady=(20, 4), anchor="w", padx=24)

        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=24, pady=8)

        self._build_form(main)
        self._build_table(main)

    # ── Left form panel ───────────────────────────────────────────────────
    def _build_form(self, parent):
        form = tk.Frame(parent, bg=BG_PANEL, width=330)
        form.pack(side="left", fill="y", padx=(0, 12))
        form.pack_propagate(False)

        tk.Label(form, text="➕  Product Details",
                 font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg=TEXT_MAIN
                 ).pack(pady=(16, 8), padx=16, anchor="w")

        fields = [
            ("Product Name *",   "name"),
            ("Category",         "cat"),
            ("Brand",            "brand"),
            ("Quantity",         "qty"),
            ("Price (₹) *",      "price"),
            ("Supplier",         "supplier"),
            ("Expiry Date",      "expiry"),
            ("Reorder Level",    "reorder"),
            ("Discount %",       "disc"),
            ("Unit",             "unit"),
        ]
        self.vars = {}
        for label, key in fields:
            tk.Label(form, text=label, font=("Segoe UI", 9, "bold"),
                     bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", padx=16, pady=(6, 0))

            if key == "cat":
                v = tk.StringVar(value=CATEGORIES[0])
                w = ttk.Combobox(form, textvariable=v, values=CATEGORIES,
                                 state="readonly", font=("Segoe UI", 9))
            elif key == "unit":
                v = tk.StringVar(value=UNITS[0])
                w = ttk.Combobox(form, textvariable=v, values=UNITS,
                                 state="readonly", font=("Segoe UI", 9))
            else:
                v = tk.StringVar()
                w = tk.Entry(form, textvariable=v, font=("Segoe UI", 9),
                             bg=ENTRY_BG, fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                             relief="flat", bd=6)
            w.pack(fill="x", padx=16, pady=(0, 2))
            self.vars[key] = v

        # Placeholder hint for expiry
        tk.Label(form, text="Format: YYYY-MM-DD", font=("Segoe UI", 7),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", padx=16)

        # Buttons
        btn_frame = tk.Frame(form, bg=BG_PANEL)
        btn_frame.pack(fill="x", padx=16, pady=16)

        for txt, cmd, col in [
            ("➕ Add",    self._add,    GREEN),
            ("💾 Update", self._update, YELLOW),
            ("🗑 Delete",  self._delete, RED),
            ("🔄 Clear",  self._clear,  BG_CARD),
        ]:
            tk.Button(btn_frame, text=txt, font=("Segoe UI", 9, "bold"),
                      bg=col, fg="white", activebackground=col,
                      relief="flat", cursor="hand2", command=cmd
                      ).pack(fill="x", pady=3, ipady=6)

        # Search
        tk.Label(form, text="🔍 Search", font=("Segoe UI", 9, "bold"),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", padx=16, pady=(8, 0))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._search())
        tk.Entry(form, textvariable=self.search_var, font=("Segoe UI", 9),
                 bg=ENTRY_BG, fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                 relief="flat", bd=6).pack(fill="x", padx=16, pady=(0, 8))

    # ── Right table ───────────────────────────────────────────────────────
    def _build_table(self, parent):
        tbl_frame = tk.Frame(parent, bg=BG_PANEL)
        tbl_frame.pack(side="left", fill="both", expand=True)

        cols = ("ID", "Name", "Category", "Brand", "Qty", "Price", "Supplier",
                "Expiry", "Reorder", "Disc%", "Unit", "Sales")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                 height=20, style="Custom.Treeview")

        widths = [85, 130, 130, 90, 50, 75, 130, 90, 70, 50, 50, 60]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, anchor="center")

        sb_y = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        sb_x = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        self.tree.pack(side="left", fill="both", expand=True)
        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")

        self.tree.tag_configure("low", background="#4D3800", foreground=YELLOW)
        self.tree.tag_configure("out", background="#4D1C1C", foreground=RED)
        self.tree.tag_configure("ok",  background="#1A3A2A", foreground=GREEN)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self._apply_style()
        self.refresh()

    def _apply_style(self):
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background=BG_PANEL, foreground=TEXT_MAIN,
                        fieldbackground=BG_PANEL, rowheight=24,
                        font=("Segoe UI", 9))
        style.configure("Custom.Treeview.Heading",
                        background=BG_CARD, foreground=TEXT_MAIN,
                        font=("Segoe UI", 9, "bold"))
        style.map("Custom.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

    # ── CRUD handlers ─────────────────────────────────────────────────────
    def _add(self):
        name  = self.vars["name"].get().strip()
        price = self.vars["price"].get().strip()
        if not name or not price:
            messagebox.showerror("Error", "Product Name and Price are required!")
            return
        try:
            record = {
                "product_id":   self.db.next_product_id(),
                "product_name": name,
                "category":     self.vars["cat"].get(),
                "brand":        self.vars["brand"].get().strip() or "Generic",
                "quantity":     int(self.vars["qty"].get() or 0),
                "price":        float(price),
                "supplier":     self.vars["supplier"].get().strip() or "Unknown",
                "expiry_date":  self.vars["expiry"].get().strip() or "2026-12-31",
                "date_added":   datetime.today().strftime("%Y-%m-%d"),
                "reorder_level": int(self.vars["reorder"].get() or 10),
                "discount_pct": float(self.vars["disc"].get() or 0),
                "sales_count":  0,
                "unit":         self.vars["unit"].get(),
            }
            if self.db.insert(record):
                messagebox.showinfo("Success", f"✅ {name} added successfully!")
                self._clear()
                self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Quantity and Price must be numbers!")

    def _update(self):
        if not self._selected_id:
            messagebox.showwarning("Warning", "Select a product first!")
            return
        try:
            updates = {
                "product_name":  self.vars["name"].get().strip(),
                "category":      self.vars["cat"].get(),
                "brand":         self.vars["brand"].get().strip(),
                "quantity":      int(self.vars["qty"].get() or 0),
                "price":         float(self.vars["price"].get() or 0),
                "supplier":      self.vars["supplier"].get().strip(),
                "expiry_date":   self.vars["expiry"].get().strip(),
                "reorder_level": int(self.vars["reorder"].get() or 10),
                "discount_pct":  float(self.vars["disc"].get() or 0),
                "unit":          self.vars["unit"].get(),
            }
            if self.db.update(self._selected_id, updates):
                messagebox.showinfo("Success", "✅ Product updated!")
                self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Quantity and Price must be numbers!")

    def _delete(self):
        if not self._selected_id:
            messagebox.showwarning("Warning", "Select a product first!")
            return
        name = self.vars["name"].get()
        if messagebox.askyesno("Confirm Delete", f"Delete '{name}'?"):
            self.db.delete(self._selected_id)
            messagebox.showinfo("Deleted", "🗑️ Product deleted.")
            self._clear()
            self.refresh()

    def _clear(self):
        for v in self.vars.values():
            v.set("")
        self.vars["cat"].set(CATEGORIES[0])
        self.vars["unit"].set(UNITS[0])
        self._selected_id = None

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self._selected_id = vals[0]
        keys = ["name", "cat", "brand", "qty", "price", "supplier", "expiry", "reorder", "disc", "unit"]
        data = [vals[1], vals[2], vals[3], vals[4], vals[5].replace("₹",""),
                vals[6], vals[7], vals[8], vals[9], vals[10]]
        for k, d in zip(keys, data):
            self.vars[k].set(d)

    def _search(self):
        q = self.search_var.get().strip()
        if q:
            df = self.db.search(q)
        else:
            df = self.db.get_all()
        self._populate(df)

    def _sort(self, col):
        """Simple alphabetical toggle sort."""
        df = self.db.get_all()
        col_map = {
            "ID": "product_id", "Name": "product_name", "Category": "category",
            "Brand": "brand", "Qty": "quantity", "Price": "price",
        }
        key = col_map.get(col)
        if key and key in df.columns:
            df = df.sort_values(key)
        self._populate(df)

    # ── Table population ──────────────────────────────────────────────────
    def refresh(self):
        self._populate(self.db.get_all())

    def _populate(self, df):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, r in df.iterrows():
            qty = int(r["quantity"])
            rl  = int(r["reorder_level"])
            tag = "out" if qty == 0 else ("low" if qty < rl else "ok")
            self.tree.insert("", "end", tags=(tag,), values=(
                r["product_id"], r["product_name"], r["category"], r["brand"],
                qty, f"₹{float(r['price']):.2f}", r["supplier"],
                r["expiry_date"], rl, r["discount_pct"], r["unit"], r["sales_count"]
            ))
