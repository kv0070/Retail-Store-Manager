# 🛒 Grocery Inventory Management System
### B.Tech CSEG1021 – Python Programming Project

---

## 📁 Folder Structure
```
grocery_ims/
├── main.py          ← Run this file to start the app
├── database.py      ← MongoDB + CSV + sample data generator
├── dashboard.py     ← KPI dashboard with stat cards
├── products.py      ← Full CRUD product management
├── billing.py       ← Sales & billing with GST
├── alerts.py        ← Stock & expiry alerts
├── graphs.py        ← Matplotlib charts (5 graphs)
├── analysis.py      ← NumPy statistical analysis
├── requirements.txt ← Python dependencies
├── README.md        ← This file
└── data/
    └── inventory.csv ← Auto-generated on first run
```

---

## ⚙️ Installation Steps

### Step 1: Install Python
- Download Python 3.10+ from https://python.org
- Make sure to check "Add Python to PATH" during installation

### Step 2: Install required packages
Open Command Prompt / Terminal in the project folder and run:
```
pip install pandas numpy matplotlib pymongo
```

### Step 3: (Optional) Install MongoDB
- Download MongoDB Community from https://www.mongodb.com/try/download/community
- Install and start the MongoDB service
- If MongoDB is NOT installed, the app still works using CSV mode

### Step 4: Run the application
```
python main.py
```

---

## 🚀 Features
| Module        | Technology     | What it does                              |
|---------------|----------------|-------------------------------------------|
| Dashboard     | Tkinter        | KPI cards + inventory overview table      |
| Products      | Tkinter+Pandas | Add, Edit, Delete, Search products        |
| Billing       | Tkinter        | Sales billing with GST + receipt          |
| Alerts        | Pandas         | Low stock / expiry / out-of-stock alerts  |
| Graphs        | Matplotlib     | 5 types of charts                         |
| Analysis      | NumPy          | Statistical analysis + reorder prediction |
| Database      | MongoDB+Pandas | CRUD operations + CSV backup              |

---

## 📊 Technologies Used
- **Tkinter** – GUI Frontend
- **Pandas** – Data handling & CSV operations  
- **Matplotlib** – Data visualisation (5 charts)
- **NumPy** – Numerical analysis
- **MongoDB** – NoSQL database (CRUD)

---

## 📝 Notes
- Sample data (80+ products) is auto-generated on first launch
- Data is saved to `data/inventory.csv` automatically
- MongoDB sync works when MongoDB service is running locally
- Press `Delete` key on a billing item to remove it from the bill
