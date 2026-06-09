"""
graphs.py – Matplotlib charts embedded in Tkinter
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BG_DARK   = "#1A1A2E"
BG_PANEL  = "#16213E"
BG_CARD   = "#0F3460"
ACCENT    = "#E94560"
GREEN     = "#00B894"
YELLOW    = "#FDCB6E"
RED       = "#E17055"
TEXT_MAIN = "#EAEAEA"
TEXT_DIM  = "#A0A0B0"

CHART_BG = "#16213E"
CHART_FG = "#EAEAEA"

PALETTE = ["#E94560","#00B894","#FDCB6E","#74B9FF","#A29BFE",
           "#FD79A8","#55EFC4","#81ECEC","#FFEAA7","#DFE6E9"]


class GraphFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg=BG_DARK)
        self.db = db
        self._build()

    def _build(self):
        tk.Label(self, text="📈  Data Visualisation",
                 font=("Segoe UI", 16, "bold"), bg=BG_DARK, fg=TEXT_MAIN
                 ).pack(pady=(20, 4), anchor="w", padx=24)

        btn_bar = tk.Frame(self, bg=BG_DARK)
        btn_bar.pack(fill="x", padx=24, pady=4)

        charts = [
            ("Category Stock",    self._chart_category),
            ("Top Sellers",       self._chart_top_sellers),
            ("Low Stock Pie",     self._chart_low_pie),
            ("Price Distribution",self._chart_price_hist),
            ("Stock Value",       self._chart_stock_value),
        ]
        for label, cmd in charts:
            tk.Button(btn_bar, text=label, font=("Segoe UI", 9, "bold"),
                      bg=BG_CARD, fg=TEXT_MAIN, activebackground=ACCENT,
                      relief="flat", cursor="hand2", command=cmd,
                      padx=12, pady=6).pack(side="left", padx=4)

        self.canvas_frame = tk.Frame(self, bg=BG_PANEL)
        self.canvas_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self._chart_category()   # default chart

    def _clear(self):
        for w in self.canvas_frame.winfo_children():
            w.destroy()

    def _embed(self, fig):
        self._clear()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # ── Chart 1: Category-wise total stock (bar) ──────────────────────────
    def _chart_category(self):
        df  = self.db.get_all()
        grp = df.groupby("category")["quantity"].sum().sort_values(ascending=False)
        fig, ax = self._styled_fig()
        bars = ax.bar(range(len(grp)), grp.values, color=PALETTE[:len(grp)], edgecolor="none")
        ax.set_xticks(range(len(grp)))
        ax.set_xticklabels(grp.index, rotation=35, ha="right", fontsize=8, color=CHART_FG)
        ax.set_title("Category-wise Total Stock", color=CHART_FG, fontsize=13, fontweight="bold")
        ax.set_ylabel("Total Units", color=CHART_FG)
        for bar, val in zip(bars, grp.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    str(int(val)), ha="center", va="bottom", fontsize=8, color=CHART_FG)
        fig.tight_layout()
        self._embed(fig)

    # ── Chart 2: Top 10 selling products (horizontal bar) ─────────────────
    def _chart_top_sellers(self):
        df  = self.db.get_all()
        top = df.nlargest(10, "sales_count")[["product_name", "sales_count"]]
        fig, ax = self._styled_fig()
        colors = PALETTE[:len(top)]
        ax.barh(top["product_name"], top["sales_count"],
                color=colors[::-1], edgecolor="none")
        ax.set_title("Top 10 Best-Selling Products", color=CHART_FG,
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Sales Count", color=CHART_FG)
        ax.tick_params(colors=CHART_FG)
        fig.tight_layout()
        self._embed(fig)

    # ── Chart 3: In-stock vs Low-stock vs Out (pie) ───────────────────────
    def _chart_low_pie(self):
        df      = self.db.get_all()
        out     = int((df["quantity"] == 0).sum())
        low     = int(((df["quantity"] > 0) & (df["quantity"] < df["reorder_level"])).sum())
        ok      = len(df) - out - low
        labels  = ["In Stock", "Low Stock", "Out of Stock"]
        sizes   = [ok, low, out]
        colors  = [GREEN, YELLOW, RED]
        fig, ax = self._styled_fig()
        wedges, texts, auto = ax.pie(
            sizes, labels=labels, colors=colors,
            autopct="%1.1f%%", startangle=140,
            textprops={"color": CHART_FG},
            wedgeprops={"edgecolor": CHART_BG, "linewidth": 2}
        )
        for t in auto:
            t.set_color(CHART_BG)
            t.set_fontweight("bold")
        ax.set_title("Stock Level Distribution", color=CHART_FG,
                     fontsize=13, fontweight="bold")
        fig.tight_layout()
        self._embed(fig)

    # ── Chart 4: Price distribution histogram ─────────────────────────────
    def _chart_price_hist(self):
        df  = self.db.get_all()
        prices = df["price"].astype(float).values
        fig, ax = self._styled_fig()
        ax.hist(prices, bins=20, color=ACCENT, edgecolor=CHART_BG, alpha=0.85)
        mean_price = np.mean(prices)
        ax.axvline(mean_price, color=YELLOW, linestyle="--", linewidth=2,
                   label=f"Mean ₹{mean_price:.2f}")
        ax.set_title("Price Distribution of Products", color=CHART_FG,
                     fontsize=13, fontweight="bold")
        ax.set_xlabel("Price (₹)", color=CHART_FG)
        ax.set_ylabel("Number of Products", color=CHART_FG)
        ax.legend(facecolor=BG_CARD, labelcolor=CHART_FG)
        fig.tight_layout()
        self._embed(fig)

    # ── Chart 5: Top 8 categories by stock value (stacked) ────────────────
    def _chart_stock_value(self):
        df        = self.db.get_all()
        df        = df.copy()
        df["value"] = df["quantity"].astype(float) * df["price"].astype(float)
        grp       = df.groupby("category")["value"].sum().nlargest(8)
        fig, ax   = self._styled_fig()
        bars = ax.bar(range(len(grp)), grp.values, color=PALETTE[:len(grp)],
                      edgecolor="none")
        ax.set_xticks(range(len(grp)))
        ax.set_xticklabels(grp.index, rotation=35, ha="right",
                           fontsize=8, color=CHART_FG)
        ax.set_title("Inventory Value by Category (₹)", color=CHART_FG,
                     fontsize=13, fontweight="bold")
        ax.set_ylabel("Value (₹)", color=CHART_FG)
        for bar, val in zip(bars, grp.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                    f"₹{val:,.0f}", ha="center", va="bottom",
                    fontsize=7, color=CHART_FG)
        fig.tight_layout()
        self._embed(fig)

    # ── Helper ────────────────────────────────────────────────────────────
    def _styled_fig(self):
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=CHART_BG)
        ax.set_facecolor(CHART_BG)
        ax.tick_params(colors=CHART_FG)
        for spine in ax.spines.values():
            spine.set_edgecolor("#2D3561")
        return fig, ax

    def refresh(self):
        self._chart_category()
