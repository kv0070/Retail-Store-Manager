"""
database.py – MongoDB CRUD + CSV sync + sample dataset generator
"""

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# ── Try importing pymongo; fall back to CSV-only mode ──────────────────────
try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "inventory.csv")


# ── Sample data definitions ────────────────────────────────────────────────
CATEGORIES = {
    "Grains & Pulses":   ["Rice", "Wheat Flour", "Maida", "Besan", "Moong Dal", "Chana Dal",
                           "Toor Dal", "Masoor Dal", "Rajma", "Poha"],
    "Spices & Masalas":  ["Turmeric Powder", "Red Chilli Powder", "Coriander Powder",
                           "Cumin Seeds", "Mustard Seeds", "Garam Masala", "Black Pepper",
                           "Cardamom", "Cloves", "Bay Leaves"],
    "Dairy Products":    ["Full Cream Milk", "Skimmed Milk", "Paneer", "Butter",
                           "Ghee", "Curd", "Cheese Slices", "Buttermilk"],
    "Oils & Fats":       ["Sunflower Oil", "Mustard Oil", "Coconut Oil", "Olive Oil",
                           "Vanaspati Ghee", "Groundnut Oil"],
    "Snacks & Biscuits": ["Marie Biscuits", "Bourbon Biscuits", "Potato Chips", "Namkeen Mix",
                           "Digestive Biscuits", "Rice Cakes", "Popcorn"],
    "Beverages":         ["Tea Powder", "Coffee Powder", "Green Tea", "Fruit Juice",
                           "Cold Drink 2L", "Mineral Water 1L", "Coconut Water"],
    "Personal Care":     ["Soap Bar", "Shampoo 200ml", "Toothpaste", "Washing Powder",
                           "Dishwash Liquid", "Floor Cleaner", "Toilet Cleaner"],
    "Vegetables":        ["Tomato", "Onion", "Potato", "Capsicum", "Carrot",
                           "Cauliflower", "Spinach", "Brinjal"],
    "Fruits":            ["Banana", "Apple", "Mango", "Grapes", "Orange",
                           "Papaya", "Guava", "Pomegranate"],
    "Packaged Foods":    ["Instant Noodles", "Pasta", "Cornflakes", "Oats",
                           "Tomato Ketchup", "Pickles", "Jam", "Bread"],
}

BRANDS = ["Tata", "Patanjali", "Amul", "Mother Dairy", "Daawat", "Fortune",
          "Britannia", "Nestlé", "ITC", "MDH", "Everest", "Haldirams",
          "Parle", "Maggi", "Saffola", "Godrej", "HUL", "Marico"]

SUPPLIERS = ["FreshMart Wholesale", "AgriSupply Co.", "Daily Needs Dist.",
             "Metro Cash & Carry", "FMCG Direct", "Farm Fresh Pvt Ltd",
             "Organic Valley", "NutriSource Trading", "QuickStock India"]


def _random_date(start_offset: int, end_offset: int) -> str:
    """Return a random date string between today+start_offset and today+end_offset days."""
    base = datetime.today()
    delta = random.randint(start_offset, end_offset)
    return (base + timedelta(days=delta)).strftime("%Y-%m-%d")


def generate_sample_data(n: int = 80) -> pd.DataFrame:
    """Generate n rows of realistic grocery inventory data."""
    random.seed(42)
    np.random.seed(42)

    rows = []
    pid = 1001
    for cat, items in CATEGORIES.items():
        for item in items:
            if len(rows) >= n:
                break
            qty   = int(np.random.choice(
                [0, random.randint(1, 15), random.randint(15, 300)],
                p=[0.05, 0.15, 0.80]
            ))
            price = round(random.uniform(10, 950), 2)
            rows.append({
                "product_id":    f"GRC{pid:04d}",
                "product_name":  item,
                "category":      cat,
                "brand":         random.choice(BRANDS),
                "quantity":      qty,
                "price":         price,
                "supplier":      random.choice(SUPPLIERS),
                "expiry_date":   _random_date(-10, 730),   # some already expired
                "date_added":    _random_date(-365, 0),
                "reorder_level": random.randint(5, 30),
                "discount_pct":  round(random.uniform(0, 25), 1),
                "sales_count":   random.randint(0, 500),
                "unit":          random.choice(["kg", "L", "pcs", "g", "ml", "pack"]),
            })
            pid += 1

    return pd.DataFrame(rows)


# ── Main DB class ──────────────────────────────────────────────────────────
class DatabaseManager:
    """
    Handles all data operations.
    Uses MongoDB when available; falls back to CSV-only mode.
    """

    def __init__(self):
        self.mongo_ok = False
        self.collection = None
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

        # 1. Try MongoDB
        if MONGO_AVAILABLE:
            try:
                client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
                client.server_info()                          # raises if not running
                db = client["grocery_ims"]
                self.collection = db["inventory"]
                self.mongo_ok = True
            except Exception:
                self.mongo_ok = False

        # 2. Seed data if empty
        if os.path.exists(CSV_PATH):
            self._df = pd.read_csv(CSV_PATH)
            if self._df.empty:
                self._df = generate_sample_data()
                self._save_csv()
        else:
            self._df = generate_sample_data()
            self._save_csv()

        # 3. Push to Mongo if needed
        if self.mongo_ok and self.collection.count_documents({}) == 0:
            records = self._df.to_dict("records")
            self.collection.insert_many(records)

    # ── Internal helpers ───────────────────────────────────────────────────
    def _save_csv(self):
        self._df.to_csv(CSV_PATH, index=False)

    def _reload(self):
        """Re-read from Mongo (if available) or from CSV."""
        if self.mongo_ok:
            docs = list(self.collection.find({}, {"_id": 0}))
            self._df = pd.DataFrame(docs) if docs else pd.DataFrame()
        else:
            self._df = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame()

    # ── Public CRUD ────────────────────────────────────────────────────────
    def get_all(self) -> pd.DataFrame:
        self._reload()
        return self._df.copy()

    def search(self, query: str, field: str = "product_name") -> pd.DataFrame:
        self._reload()
        mask = self._df[field].str.contains(query, case=False, na=False)
        return self._df[mask].copy()

    def insert(self, record: dict) -> bool:
        try:
            self._reload()
            new_row = pd.DataFrame([record])
            self._df = pd.concat([self._df, new_row], ignore_index=True)
            self._save_csv()
            if self.mongo_ok:
                self.collection.insert_one(record)
            return True
        except Exception as e:
            print(f"Insert error: {e}")
            return False

    def update(self, product_id: str, updates: dict) -> bool:
        try:
            self._reload()
            idx = self._df.index[self._df["product_id"] == product_id]
            if idx.empty:
                return False
            for k, v in updates.items():
                self._df.loc[idx, k] = v
            self._save_csv()
            if self.mongo_ok:
                self.collection.update_one({"product_id": product_id}, {"$set": updates})
            return True
        except Exception as e:
            print(f"Update error: {e}")
            return False

    def delete(self, product_id: str) -> bool:
        try:
            self._reload()
            self._df = self._df[self._df["product_id"] != product_id]
            self._save_csv()
            if self.mongo_ok:
                self.collection.delete_one({"product_id": product_id})
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def reduce_stock(self, product_id: str, qty: int) -> bool:
        self._reload()
        idx = self._df.index[self._df["product_id"] == product_id]
        if idx.empty:
            return False
        current = int(self._df.loc[idx[0], "quantity"])
        if current < qty:
            return False
        new_qty     = current - qty
        sales_prev  = int(self._df.loc[idx[0], "sales_count"])
        updates = {"quantity": new_qty, "sales_count": sales_prev + qty}
        return self.update(product_id, updates)

    # ── Analytics helpers (used by Graphs + Analysis frames) ──────────────
    def get_summary(self) -> dict:
        df = self.get_all()
        if df.empty:
            return {}
        today = datetime.today().date()
        exp_dates = pd.to_datetime(df["expiry_date"], errors="coerce").dt.date
        return {
            "total_products":   len(df),
            "total_categories": df["category"].nunique(),
            "low_stock":        int((df["quantity"] < df["reorder_level"]).sum()),
            "out_of_stock":     int((df["quantity"] == 0).sum()),
            "expiring_soon":    int(((exp_dates - today) <= timedelta(days=30)).sum()),
            "total_value":      round(float((df["quantity"] * df["price"]).sum()), 2),
        }

    def get_low_stock(self) -> pd.DataFrame:
        df = self.get_all()
        return df[df["quantity"] < df["reorder_level"]].copy()

    def get_expired(self) -> pd.DataFrame:
        df = self.get_all()
        today = datetime.today().date()
        exp_dates = pd.to_datetime(df["expiry_date"], errors="coerce").dt.date
        return df[exp_dates <= today].copy()

    def get_expiring_soon(self, days: int = 30) -> pd.DataFrame:
        df = self.get_all()
        today = datetime.today().date()
        exp_dates = pd.to_datetime(df["expiry_date"], errors="coerce").dt.date
        mask = (exp_dates > today) & ((exp_dates - today) <= timedelta(days=days))
        return df[mask].copy()

    def next_product_id(self) -> str:
        df = self.get_all()
        if df.empty:
            return "GRC1001"
        ids = df["product_id"].str.extract(r"(\d+)")[0].astype(int)
        return f"GRC{ids.max() + 1}"
