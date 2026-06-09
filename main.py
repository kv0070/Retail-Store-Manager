
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from dashboard import DashboardFrame
from products import ProductFrame
from billing import BillingFrame
from alerts import AlertFrame
from graphs import GraphFrame



#  COLOUR PALETTE  &  FONT CONSTANTS

BG_DARK   = "#1A1A2E"
BG_PANEL  = "#16213E"
BG_CARD   = "#0F3460"
ACCENT    = "#E94560"
ACCENT2   = "#533483"
TEXT_MAIN = "#EAEAEA"
TEXT_DIM  = "#A0A0B0"
GREEN     = "#00B894"
YELLOW    = "#FDCB6E"
RED       = "#E17055"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_NAV    = ("Segoe UI", 11, "bold")
FONT_NORMAL = ("Segoe UI", 10)


class GroceryIMS(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("🛒  Grocery Inventory Management System")
        self.geometry("1280x750")
        self.minsize(1100, 680)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # Initialise DB (creates sample data if empty)
        self.db = DatabaseManager()

        self._build_header()
        self._build_layout()
        self._build_nav()
        self._build_content_area()

        # Show dashboard by default
        self.show_frame("Dashboard")

    # ── Header ────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=BG_CARD, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(
            hdr,
            text="🛒  INVENTORY MANAGEMENT SYSTEM",
            font=FONT_TITLE, bg=BG_CARD, fg=TEXT_MAIN
        ).pack(side="left", padx=24, pady=12)

        # tk.Label(
        #     hdr,
        #     text="B.Tech CSEG1021 – Python Programming",
        #     font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_DIM
        # ).pack(side="right", padx=24)

    # ── Two-column layout ─────────────────────
    def _build_layout(self):
        self.body = tk.Frame(self, bg=BG_DARK)
        self.body.pack(fill="both", expand=True)

    # ── Left navigation sidebar ───────────────
    def _build_nav(self):
        self.nav_frame = tk.Frame(self.body, bg=BG_PANEL, width=200)
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(False)

        tk.Label(
            self.nav_frame, text="NAVIGATION",
            font=("Segoe UI", 8, "bold"), bg=BG_PANEL, fg=TEXT_DIM
        ).pack(pady=(20, 6), padx=16, anchor="w")

        self.nav_buttons = {}
        nav_items = [
            ("📊", "Dashboard"),
            ("📦", "Products"),
            ("🧾", "Billing"),
            ("⚠️",  "Alerts"),
            ("📈", "Graphs"),
        ]
        for icon, label in nav_items:
            btn = tk.Button(
                self.nav_frame,
                text=f"  {icon}  {label}",
                font=FONT_NAV,
                bg=BG_PANEL, fg=TEXT_MAIN,
                activebackground=ACCENT,
                activeforeground="white",
                relief="flat", anchor="w",
                cursor="hand2",
                command=lambda l=label: self.show_frame(l)
            )
            btn.pack(fill="x", padx=8, pady=2, ipady=10)
            self.nav_buttons[label] = btn

        # Version label at bottom
        # tk.Label(
        #     self.nav_frame,
        #     text="v1.0  |  2024-25",
        #     font=("Segoe UI", 8), bg=BG_PANEL, fg=TEXT_DIM
        # ).pack(side="bottom", pady=12)

    # ── Right content area ────────────────────
    def _build_content_area(self):
        self.content = tk.Frame(self.body, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

        # Instantiate all frames once
        self.frames = {
            "Dashboard": DashboardFrame(self.content, self.db),
            "Products":  ProductFrame(self.content,  self.db),
            "Billing":   BillingFrame(self.content,  self.db),
            "Alerts":    AlertFrame(self.content,    self.db),
            "Graphs":    GraphFrame(self.content,    self.db),
        }
        for frame in self.frames.values():
            frame.place(relwidth=1, relheight=1)

    # ── Navigation logic ──────────────────────
    def show_frame(self, name: str):
        # Highlight active nav button
        for label, btn in self.nav_buttons.items():
            btn.configure(
                bg=ACCENT if label == name else BG_PANEL,
                fg="white" if label == name else TEXT_MAIN
            )
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "refresh"):
            frame.refresh()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = GroceryIMS()
    app.mainloop()
