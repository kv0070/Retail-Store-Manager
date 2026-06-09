"""
billing.py – Billing / Sales module with GST, discount, bill generation
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

GST_RATE = 0.05   # 5 % GST


class BillingFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=BG_DARK)
        self.db = db
        self.bill_items = []   # list of dicts
        self._build()

    def _build(self):
        tk.Label(self, text="🧾  Billing & Sales",
                 font=("Segoe UI", 16, "bold"), bg=BG_DARK, fg=TEXT_MAIN
                 ).pack(pady=(20, 4), anchor="w", padx=24)

        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=24, pady=8)

        self._build_left(main)
        self._build_right(main)

    # ── Left: item picker ─────────────────────────────────────────────────
    def _build_left(self, parent):
        left = tk.Frame(parent, bg=BG_PANEL, width=350)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(left, text="🔍 Search Product",
                 font=("Segoe UI", 11, "bold"), bg=BG_PANEL, fg=TEXT_MAIN
                 ).pack(pady=(16, 4), padx=16, anchor="w")

        self.srch_var = tk.StringVar()
        self.srch_var.trace_add("write", lambda *_: self._filter_products())
        tk.Entry(left, textvariable=self.srch_var, font=("Segoe UI", 10),
                 bg=ENTRY_BG, fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                 relief="flat", bd=6).pack(fill="x", padx=16)

        self.prod_lb = tk.Listbox(left, bg=ENTRY_BG, fg=TEXT_MAIN,
                                   selectbackground=ACCENT,
                                   font=("Segoe UI", 9), height=10,
                                   relief="flat", bd=0)
        self.prod_lb.pack(fill="x", padx=16, pady=8)
        self.prod_lb.bind("<<ListboxSelect>>", self._on_prod_select)

        # Qty spinner
        tk.Label(left, text="Quantity to Sell",
                 font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXT_DIM
                 ).pack(anchor="w", padx=16, pady=(4, 0))
        self.qty_var = tk.IntVar(value=1)
        tk.Spinbox(left, from_=1, to=9999, textvariable=self.qty_var,
                   font=("Segoe UI", 10), bg=ENTRY_BG, fg=TEXT_MAIN,
                   buttonbackground=BG_CARD, relief="flat", bd=6
                   ).pack(fill="x", padx=16, pady=(0, 8))

        tk.Button(left, text="➕  Add to Bill", font=("Segoe UI", 10, "bold"),
                  bg=GREEN, fg="white", relief="flat", cursor="hand2",
                  command=self._add_to_bill).pack(fill="x", padx=16, ipady=8)

        # Customer name
        tk.Label(left, text="Customer Name",
                 font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXT_DIM
                 ).pack(anchor="w", padx=16, pady=(16, 0))
        self.cust_var = tk.StringVar(value="Walk-in Customer")
        tk.Entry(left, textvariable=self.cust_var, font=("Segoe UI", 10),
                 bg=ENTRY_BG, fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                 relief="flat", bd=6).pack(fill="x", padx=16)

        # Action buttons
        for txt, cmd, col in [
            ("🧾  Generate Bill",   self._generate_bill,   ACCENT),
            ("🔄  Clear Bill",      self._clear_bill,      BG_CARD),
        ]:
            tk.Button(left, text=txt, font=("Segoe UI", 10, "bold"),
                      bg=col, fg="white", relief="flat", cursor="hand2",
                      command=cmd).pack(fill="x", padx=16, pady=4, ipady=8)

        # Selected product info
        self.info_var = tk.StringVar(value="No product selected")
        tk.Label(left, textvariable=self.info_var,
                 font=("Segoe UI", 8), bg=BG_PANEL, fg=YELLOW,
                 wraplength=310, justify="left"
                 ).pack(padx=16, pady=8, anchor="w")

        self._filter_products()

    # ── Right: bill display ───────────────────────────────────────────────
    def _build_right(self, parent):
        right = tk.Frame(parent, bg=BG_PANEL)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="📋  Current Bill",
                 font=("Segoe UI", 12, "bold"), bg=BG_PANEL, fg=TEXT_MAIN
                 ).pack(pady=(16, 4), padx=16, anchor="w")

        cols = ("Product", "Qty", "Unit Price", "Disc%", "Amount")
        self.bill_tree = ttk.Treeview(right, columns=cols, show="headings",
                                      height=14, style="Custom.Treeview")
        widths = [200, 60, 100, 70, 100]
        for col, w in zip(cols, widths):
            self.bill_tree.heading(col, text=col)
            self.bill_tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(right, orient="vertical", command=self.bill_tree.yview)
        self.bill_tree.configure(yscrollcommand=sb.set)
        self.bill_tree.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=(0, 8))
        sb.pack(side="right", fill="y", pady=(0, 8), padx=(0, 8))

        self.bill_tree.bind("<Delete>", self._remove_item)

        # Totals panel
        totals_frame = tk.Frame(right, bg=BG_CARD)
        totals_frame.pack(fill="x", padx=8, pady=4)
        self.sub_lbl   = tk.Label(totals_frame, text="Subtotal:  ₹0.00",
                                   font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_MAIN)
        self.gst_lbl   = tk.Label(totals_frame, text=f"GST ({int(GST_RATE*100)}%): ₹0.00",
                                   font=("Segoe UI", 10), bg=BG_CARD, fg=YELLOW)
        self.disc_lbl  = tk.Label(totals_frame, text="Discount:  ₹0.00",
                                   font=("Segoe UI", 10), bg=BG_CARD, fg=GREEN)
        self.total_lbl = tk.Label(totals_frame, text="TOTAL:  ₹0.00",
                                   font=("Segoe UI", 14, "bold"), bg=BG_CARD, fg=ACCENT)
        for lbl in (self.sub_lbl, self.gst_lbl, self.disc_lbl, self.total_lbl):
            lbl.pack(anchor="e", padx=20, pady=2)

        # Bill receipt area
        self.receipt = tk.Text(right, height=6, bg=ENTRY_BG, fg=GREEN,
                               font=("Courier New", 9), relief="flat", bd=6,
                               state="disabled")
        self.receipt.pack(fill="x", padx=8, pady=4)

        self._apply_style()

    def _apply_style(self):
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

    # ── Product list helpers ──────────────────────────────────────────────
    def _filter_products(self):
        q = self.srch_var.get().strip()
        df = self.db.search(q) if q else self.db.get_all()
        self._prod_df = df.reset_index(drop=True)
        self.prod_lb.delete(0, tk.END)
        for _, r in self._prod_df.iterrows():
            qty = int(r["quantity"])
            self.prod_lb.insert(tk.END,
                f"{r['product_id']}  {r['product_name']}  [Qty:{qty}]")

    def _on_prod_select(self, _):
        sel = self.prod_lb.curselection()
        if not sel:
            return
        r = self._prod_df.iloc[sel[0]]
        disc = float(r["discount_pct"])
        eff  = float(r["price"]) * (1 - disc / 100)
        self.info_var.set(
            f"📦 {r['product_name']}  |  Price: ₹{float(r['price']):.2f}"
            f"  |  Disc: {disc}%  |  Effective: ₹{eff:.2f}"
            f"  |  Stock: {int(r['quantity'])} {r['unit']}"
        )
        self._sel_row = r

    def _add_to_bill(self):
        if not hasattr(self, "_sel_row"):
            messagebox.showwarning("Warning", "Select a product first!")
            return
        r   = self._sel_row
        qty = self.qty_var.get()
        if qty > int(r["quantity"]):
            messagebox.showerror("Error",
                f"Only {int(r['quantity'])} units available!")
            return
        disc   = float(r["discount_pct"])
        uprice = float(r["price"])
        amount = uprice * qty * (1 - disc / 100)
        item = {
            "product_id": r["product_id"],
            "name":       r["product_name"],
            "qty":        qty,
            "unit_price": uprice,
            "disc":       disc,
            "amount":     round(amount, 2),
        }
        self.bill_items.append(item)
        self.bill_tree.insert("", "end", values=(
            item["name"], qty, f"₹{uprice:.2f}", f"{disc}%", f"₹{amount:.2f}"
        ))
        self._update_totals()

    def _remove_item(self, _):
        sel = self.bill_tree.selection()
        if sel:
            idx = self.bill_tree.index(sel[0])
            self.bill_tree.delete(sel[0])
            self.bill_items.pop(idx)
            self._update_totals()

    def _update_totals(self):
        subtotal = sum(i["amount"] for i in self.bill_items)
        gst      = round(subtotal * GST_RATE, 2)
        disc_tot = sum(i["unit_price"]*i["qty"] - i["amount"] for i in self.bill_items)
        total    = round(subtotal + gst, 2)
        self.sub_lbl.configure(text=f"Subtotal:  ₹{subtotal:.2f}")
        self.gst_lbl.configure(text=f"GST ({int(GST_RATE*100)}%): ₹{gst:.2f}")
        self.disc_lbl.configure(text=f"Discount saved: ₹{disc_tot:.2f}")
        self.total_lbl.configure(text=f"TOTAL:  ₹{total:.2f}")

    def _generate_bill(self):
        if not self.bill_items:
            messagebox.showwarning("Warning", "Bill is empty!")
            return
        # Reduce stock in DB
        for item in self.bill_items:
            ok = self.db.reduce_stock(item["product_id"], item["qty"])
            if not ok:
                messagebox.showerror("Stock Error",
                    f"Failed to reduce stock for {item['name']}")
                return

        subtotal  = sum(i["amount"] for i in self.bill_items)
        gst       = round(subtotal * GST_RATE, 2)
        total     = round(subtotal + gst, 2)
        now       = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        cust_name = self.cust_var.get()

        lines = [
            "=" * 42,
            "    🛒  GROCERY STORE  RECEIPT",
            "=" * 42,
            f"  Date    : {now}",
            f"  Customer: {cust_name}",
            "-" * 42,
            f"  {'Item':<22} {'Qty':>4}  {'Amount':>8}",
            "-" * 42,
        ]
        for item in self.bill_items:
            lines.append(
                f"  {item['name'][:22]:<22} {item['qty']:>4}  ₹{item['amount']:>7.2f}"
            )
        lines += [
            "-" * 42,
            f"  {'Subtotal':<30} ₹{subtotal:>7.2f}",
            f"  {'GST (5%)':<30} ₹{gst:>7.2f}",
            "=" * 42,
            f"  {'GRAND TOTAL':<30} ₹{total:>7.2f}",
            "=" * 42,
            "  Thank you for shopping! 😊",
            "=" * 42,
        ]
        receipt_text = "\n".join(lines)

        self.receipt.configure(state="normal")
        self.receipt.delete("1.0", tk.END)
        self.receipt.insert("1.0", receipt_text)
        self.receipt.configure(state="disabled")

        messagebox.showinfo("Bill Generated",
            f"✅ Bill generated!\nTotal: ₹{total:.2f}\nStock updated.")

    def _clear_bill(self):
        self.bill_items.clear()
        for row in self.bill_tree.get_children():
            self.bill_tree.delete(row)
        self._update_totals()
        self.receipt.configure(state="normal")
        self.receipt.delete("1.0", tk.END)
        self.receipt.configure(state="disabled")

    def refresh(self):
        self._filter_products()
