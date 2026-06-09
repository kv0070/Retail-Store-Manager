const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, PageBreak, VerticalAlign
} = require("docx");
const fs = require("fs");

const ACCENT = "E94560";
const DARK   = "1A1A2E";
const CARD   = "0F3460";
const GREEN  = "00B894";
const YELLOW = "FDCB6E";

// ── Helpers ────────────────────────────────────────────────────────────────
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, font: "Arial", size: 32, bold: true, color: ACCENT })],
    spacing: { before: 360, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT } },
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: CARD })],
    spacing: { before: 240, after: 80 },
  });
}
function h3(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: DARK })],
    spacing: { before: 180, after: 60 },
  });
}
function para(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Arial", size: 20, ...opts })],
    spacing: { after: 100 },
  });
}
function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, font: "Arial", size: 20 })],
    spacing: { after: 60 },
  });
}
function gap() { return new Paragraph({ children: [new TextRun("")], spacing: { after: 100 } }); }

// ── Cover page ─────────────────────────────────────────────────────────────
const cover = [
  gap(), gap(), gap(),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "🛒", font: "Segoe UI Emoji", size: 80 })],
    spacing: { after: 200 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({
      text: "GROCERY INVENTORY MANAGEMENT SYSTEM",
      font: "Arial", size: 40, bold: true, color: ACCENT,
    })],
    spacing: { after: 120 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({
      text: "A Python-Based Desktop Application",
      font: "Arial", size: 26, italics: true, color: CARD,
    })],
    spacing: { after: 400 },
  }),
  // Info table
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3000, 6360],
    rows: [
      ["Course",     "B.Tech CSEG1021 – Python Programming"],
      ["Student",    "___________________________________"],
      ["Roll No.",   "___________________________________"],
      ["Department", "Computer Science & Engineering"],
      ["Session",    "2024–2025"],
      ["Deadline",   "20th April 2025"],
      ["Max Marks",  "40 (Mid:10 + End:10 + Report:10 + Viva:10)"],
    ].map(([k, v]) => new TableRow({
      children: [
        new TableCell({
          borders: { top:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, bottom:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, left:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, right:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"} },
          width: { size: 3000, type: WidthType.DXA },
          shading: { fill: CARD, type: ShadingType.CLEAR },
          margins: { top:80, bottom:80, left:120, right:120 },
          children: [new Paragraph({ children: [new TextRun({ text: k, font:"Arial", size:20, bold:true, color:"EAEAEA" })] })],
        }),
        new TableCell({
          borders: { top:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, bottom:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, left:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, right:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"} },
          width: { size: 6360, type: WidthType.DXA },
          margins: { top:80, bottom:80, left:120, right:120 },
          children: [new Paragraph({ children: [new TextRun({ text: v, font:"Arial", size:20 })] })],
        }),
      ],
    })),
  }),
  gap(), gap(),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Submitted to:", font:"Arial", size:22, bold:true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Department of Computer Science & Engineering", font:"Arial", size:20, italics:true })],
    spacing: { after: 120 },
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ── Chapter content ────────────────────────────────────────────────────────
const abstract = [
  h1("Abstract"),
  para("This project presents the design and development of a Grocery Inventory Management System (GIMS) built entirely in Python. The application is a full-featured desktop solution that enables grocery store owners and managers to efficiently track stock, manage products, generate bills, receive automated alerts, and gain data-driven insights from embedded charts and statistical analyses."),
  gap(),
  para("The system integrates five core Python technologies mandated by the CSEG1021 curriculum: Tkinter for the graphical user interface, Pandas for tabular data manipulation, Matplotlib for real-time data visualisation, NumPy for numerical stock analysis, and MongoDB for persistent database storage with complete CRUD operations."),
  gap(),
  para("The application ships with an auto-generated dataset of 80+ realistic grocery products covering 10 categories, ranging from staples and spices to personal care items and beverages. All data is modifiable through the GUI at runtime and is synchronised to both a CSV flat-file and a MongoDB collection, ensuring durability and portability."),
  new Paragraph({ children: [new PageBreak()] }),
];

const intro = [
  h1("1. Introduction"),
  h2("1.1 Background"),
  para("Inventory management is one of the most critical operations in any retail business. A grocery store handles hundreds of products with varying shelf lives, prices, and stock levels. Manual tracking using notebooks or spreadsheets is error-prone, time-consuming, and insufficient for modern business demands."),
  para("The Grocery Inventory Management System (GIMS) automates these operations through a clean, modern desktop application. It provides a centralised platform for all inventory-related tasks while demonstrating the power of Python's data-science and GUI ecosystem."),
  h2("1.2 Objectives"),
  bullet("Build a fully functional, visually appealing desktop application using Tkinter."),
  bullet("Integrate Pandas for reading, filtering, and exporting inventory data to CSV."),
  bullet("Embed interactive Matplotlib charts for real-time data visualisation."),
  bullet("Apply NumPy for statistical analysis: mean, median, standard deviation, z-score."),
  bullet("Implement MongoDB CRUD operations to persist all inventory changes."),
  bullet("Auto-generate a realistic sample grocery dataset of 80+ products."),
  bullet("Support full product lifecycle: Add, Read, Update, Delete (CRUD)."),
  bullet("Provide a billing module with GST calculation and bill generation."),
  bullet("Detect and alert for low stock, out-of-stock, and expiring products."),
  h2("1.3 Scope"),
  para("The system is designed for small-to-medium grocery stores. It operates as a local desktop application and can connect to a MongoDB instance on the same machine or a local network. The project covers the full software development lifecycle from design through testing."),
  new Paragraph({ children: [new PageBreak()] }),
];

const problemStatement = [
  h1("2. Problem Statement & Design"),
  h2("2.1 Problem Statement"),
  para("A local grocery store owner faces the following challenges:"),
  bullet("Difficulty tracking 500+ products manually on paper or in basic spreadsheets."),
  bullet("No automated alerts when products fall below minimum stock levels or approach expiry."),
  bullet("Time-consuming manual billing with no GST calculation support."),
  bullet("No visual reports to understand which categories need restocking."),
  bullet("No centralised database, causing data inconsistency across staff."),
  gap(),
  para("The proposed GIMS solves all of the above through automation, a modern GUI, and database integration."),
  h2("2.2 System Design"),
  h3("2.2.1 Architecture"),
  para("The application follows a layered MVC-like architecture:"),
  bullet("Model Layer: database.py – handles all data operations (MongoDB + CSV)."),
  bullet("View Layer: Tkinter frames (dashboard.py, products.py, billing.py, alerts.py, graphs.py, analysis.py)."),
  bullet("Controller: main.py – coordinates navigation and frame switching."),
  h3("2.2.2 Database Schema (MongoDB Collection: inventory)"),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2500, 2000, 4860],
    rows: [
      ["Field", "Type", "Description"],
      ["product_id", "String", "Unique identifier (e.g. GRC1001)"],
      ["product_name", "String", "Name of the grocery product"],
      ["category", "String", "Product category (Grains, Dairy, etc.)"],
      ["brand", "String", "Brand name"],
      ["quantity", "Integer", "Current stock quantity"],
      ["price", "Float", "Selling price in INR"],
      ["supplier", "String", "Supplier / vendor name"],
      ["expiry_date", "String", "Expiry date (YYYY-MM-DD)"],
      ["date_added", "String", "Date product was first added"],
      ["reorder_level", "Integer", "Minimum quantity before restocking alert"],
      ["discount_pct", "Float", "Discount percentage offered"],
      ["sales_count", "Integer", "Total units sold (lifetime)"],
      ["unit", "String", "Unit of measurement (kg, L, pcs...)"],
    ].map((row, i) => new TableRow({
      tableHeader: i === 0,
      children: row.map((cell, j) => new TableCell({
        borders: { top:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, bottom:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, left:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, right:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"} },
        width: { size: [2500,2000,4860][j], type: WidthType.DXA },
        shading: i === 0 ? { fill: CARD, type: ShadingType.CLEAR } : undefined,
        margins: { top:80, bottom:80, left:120, right:120 },
        children: [new Paragraph({ children: [new TextRun({ text: cell, font:"Arial", size:18, bold: i===0, color: i===0?"EAEAEA":"000000" })] })],
      })),
    })),
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

const methodology = [
  h1("3. Methodology"),
  h2("3.1 Development Approach"),
  para("The project was built using an iterative, module-by-module approach. Each module was developed and tested independently before integration into the main application."),
  h2("3.2 Module Descriptions"),
  h3("3.2.1 database.py – Data Layer"),
  para("This is the backbone of the application. It uses Pandas to generate a 80+ row synthetic grocery dataset using Python's random and numpy.random modules. The dataset is seeded (seed=42) for reproducibility. The class exposes insert(), update(), delete(), get_all(), search(), and analytics helper methods. MongoDB is connected using PyMongo with a 2-second timeout; if MongoDB is unavailable, the system falls back gracefully to CSV-only mode."),
  h3("3.2.2 dashboard.py – KPI Overview"),
  para("Displays six StatCard widgets showing: Total Products, Categories, Low Stock Items, Out-of-Stock Items, Expiring Soon, and Total Inventory Value. Below the cards a Treeview table shows the first 15 products colour-coded by stock status (green / yellow / red)."),
  h3("3.2.3 products.py – CRUD Interface"),
  para("A split-panel layout: left side has a form with Entry and Combobox widgets for all 13 product fields; right side shows the full inventory in a sortable, searchable Treeview. Buttons trigger add, update, delete, and clear operations. A live search box filters the table as the user types."),
  h3("3.2.4 billing.py – Sales & Receipt"),
  para("Allows the user to search for products, select quantities, and add items to a bill. The billing engine calculates per-item discounts, a 5% GST on the subtotal, and prints a formatted receipt. On bill generation, stock levels are automatically reduced in the database via reduce_stock()."),
  h3("3.2.5 alerts.py – Stock Monitoring"),
  para("A tabbed interface with four tabs: Out of Stock, Low Stock, Expiring Soon (within 30 days), and Expired. Each tab refreshes from the database and displays the affected products. Row colours indicate urgency."),
  h3("3.2.6 graphs.py – Matplotlib Charts"),
  para("Five interactive charts are embedded directly in the Tkinter window using FigureCanvasTkAgg: (1) Category-wise stock bar chart, (2) Top 10 sellers horizontal bar, (3) Stock level pie chart, (4) Price distribution histogram with mean line, (5) Inventory value by category. All charts use a dark theme matching the application palette."),
  h3("3.2.7 analysis.py – NumPy Statistics"),
  para("Computes and displays: mean/median/std of prices, z-score stock analysis, reorder deficit using np.maximum(), estimated days until stock-out, and a 20% margin profit estimate. The reorder prediction table highlights products needing immediate attention."),
  new Paragraph({ children: [new PageBreak()] }),
];

const tools = [
  h1("4. Tools & Technologies Used"),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2200, 2200, 4960],
    rows: [
      ["Technology", "Version", "Purpose in Project"],
      ["Python", "3.10+", "Core programming language"],
      ["Tkinter", "Built-in", "GUI framework – all windows, widgets, frames"],
      ["Pandas", "1.5+", "DataFrame operations, CSV read/write, filtering, groupby"],
      ["NumPy", "1.23+", "Mean, median, std, z-score, maximum, sum calculations"],
      ["Matplotlib", "3.6+", "5 embedded charts: bar, horizontal bar, pie, histogram"],
      ["PyMongo", "4.0+", "MongoDB driver – insert, find, update_one, delete_one"],
      ["MongoDB", "6.0+", "NoSQL database for persistent inventory storage"],
      ["random", "Built-in", "Sample data generation (product names, prices, dates)"],
      ["datetime", "Built-in", "Expiry date handling and stock-out day estimation"],
      ["os / sys", "Built-in", "File path management and module imports"],
    ].map((row, i) => new TableRow({
      tableHeader: i === 0,
      children: row.map((cell, j) => new TableCell({
        borders: { top:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, bottom:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, left:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"}, right:{style:BorderStyle.SINGLE,size:1,color:"CCCCCC"} },
        width: { size: [2200,2200,4960][j], type: WidthType.DXA },
        shading: i === 0 ? { fill: CARD, type: ShadingType.CLEAR } : undefined,
        margins: { top:80, bottom:80, left:120, right:120 },
        children: [new Paragraph({ children: [new TextRun({ text: cell, font:"Arial", size:18, bold: i===0, color: i===0?"EAEAEA":"000000" })] })],
      })),
    })),
  }),
  gap(),
  h2("4.1 IDE & Tools"),
  bullet("Visual Studio Code / PyCharm – code editor"),
  bullet("MongoDB Compass – GUI for MongoDB inspection"),
  bullet("pip – Python package manager"),
  bullet("Git – version control"),
  new Paragraph({ children: [new PageBreak()] }),
];

const results = [
  h1("5. Results & Screenshots Description"),
  h2("5.1 Module-wise Output"),
  h3("Dashboard"),
  para("Six animated KPI cards display live totals. The inventory table below shows colour-coded stock status: green (in stock), yellow (low), red (out of stock)."),
  h3("Product Management"),
  para("The dual-panel CRUD screen allows adding new grocery items in under 10 seconds. Searching 'rice' instantly filters to all rice variants. Clicking a table row pre-fills the form for quick edits."),
  h3("Billing Module"),
  para("A complete bill with GST and product-level discounts is generated in one click. Stock is automatically deducted on generation. The receipt is formatted for easy reading."),
  h3("Alerts Tab"),
  para("Out-of-stock items are highlighted in red, low-stock in yellow. Expiry warnings catch products within 30 days of expiry, helping reduce food waste."),
  h3("Charts"),
  para("The category stock bar chart shows which categories dominate inventory. The top-10 sellers chart reveals the most popular products for procurement planning."),
  h3("NumPy Analysis"),
  para("The statistics panel shows inventory health at a glance. The reorder prediction table estimates how many days of stock remain per product, enabling proactive purchasing."),
  h2("5.2 Dataset Statistics (Auto-generated)"),
  bullet("Total Products: 80+"),
  bullet("Categories: 10"),
  bullet("Price Range: ₹10 – ₹950"),
  bullet("Stock Range: 0 – 300 units"),
  bullet("Suppliers: 9 unique vendors"),
  bullet("Brands: 18 popular Indian brands"),
  new Paragraph({ children: [new PageBreak()] }),
];

const conclusion = [
  h1("6. Conclusion & Future Scope"),
  h2("6.1 Conclusion"),
  para("The Grocery Inventory Management System successfully demonstrates the integration of five Python technologies into a cohesive, production-ready desktop application. The system automates stock tracking, billing, expiry monitoring, and data analysis, solving real-world pain points for grocery store operators."),
  para("The project satisfies all requirements of B.Tech CSEG1021: it uses Tkinter for GUI, Pandas for data handling, Matplotlib for visualisation, NumPy for numerical computing, and MongoDB for CRUD database operations. The codebase is modular, well-commented, and beginner-friendly."),
  h2("6.2 Future Scope"),
  bullet("Barcode Scanner Integration: Use OpenCV or a USB scanner to add/sell products by scanning barcodes."),
  bullet("Cloud Database: Migrate from local MongoDB to MongoDB Atlas for multi-branch access."),
  bullet("Mobile App: Build a companion React Native or Flutter app using a REST API backend."),
  bullet("Machine Learning Forecasting: Use scikit-learn to predict weekly demand and auto-suggest purchase quantities."),
  bullet("PDF Billing: Generate PDF invoices using ReportLab with store logo and GST number."),
  bullet("User Authentication: Add staff login with role-based access (admin vs. cashier)."),
  bullet("Email / SMS Alerts: Send automated low-stock alerts to the store manager via email."),
  bullet("Multi-Currency Support: Add support for different tax regimes and currencies."),
  new Paragraph({ children: [new PageBreak()] }),
];

const viva = [
  h1("7. Viva Questions & Answers"),
  ...[
    ["Q1: Why did you choose Python for this project?",
     "Python offers a rich ecosystem of libraries (Tkinter, Pandas, NumPy, Matplotlib) that are ideal for rapid development of data-centric desktop applications. Its syntax is clean and beginner-friendly, making it perfect for a college project."],
    ["Q2: What is Tkinter and how did you use it?",
     "Tkinter is Python's standard GUI toolkit. We used it to build all screens: the main window, navigation sidebar, KPI dashboard cards, product form, billing interface, alert tabs, and chart containers using Frame, Label, Button, Entry, Combobox, Treeview, and Spinbox widgets."],
    ["Q3: How does Pandas help in this project?",
     "Pandas DataFrames are used as the in-memory data store. We use read_csv() and to_csv() for persistence, groupby() for chart data, Boolean masking for filtering, and concat() for inserting new rows."],
    ["Q4: What NumPy functions did you use?",
     "np.mean(), np.median(), np.std(), np.max(), np.min(), np.sum(), np.maximum() (for deficit calculation), and z-score normalisation (qty - mean) / std. NumPy arrays are also used for all chart data passed to Matplotlib."],
    ["Q5: Explain MongoDB CRUD operations in your project.",
     "Create: collection.insert_one(record) or insert_many(records). Read: collection.find({}, {'_id':0}). Update: collection.update_one({'product_id': pid}, {'$set': updates}). Delete: collection.delete_one({'product_id': pid}). We connect via MongoClient with a 2-second timeout."],
    ["Q6: What is the purpose of the reorder_level field?",
     "It defines the minimum quantity at which a product must be restocked. When quantity < reorder_level, the product appears in the Low Stock alert tab and the reorder prediction table with an estimated number of days until stock-out."],
    ["Q7: How do you calculate GST in the billing module?",
     "We apply a flat 5% GST on the net subtotal (after item-level discounts). GST = subtotal × 0.05. Grand Total = subtotal + GST. The per-item discount is: amount = unit_price × qty × (1 - discount_pct / 100)."],
    ["Q8: What happens if MongoDB is not running?",
     "The DatabaseManager detects the connection failure using a 2-second serverSelectionTimeoutMS timeout. It sets mongo_ok = False and falls back to CSV-only mode, so the application continues to work fully using Pandas and the local CSV file."],
    ["Q9: How is the sample data generated?",
     "The generate_sample_data() function uses random.seed(42) and np.random.seed(42) for reproducibility. It iterates over a dictionary of 10 categories with product name lists, assigns random prices (₹10-₹950), quantities (0-300), brands, suppliers, and dates using the datetime and timedelta classes."],
    ["Q10: What is FigureCanvasTkAgg?",
     "It is a Matplotlib backend adapter that converts a Matplotlib Figure into a Tkinter-compatible widget. We use canvas = FigureCanvasTkAgg(fig, master=frame) and then canvas.get_tk_widget().pack() to embed live charts directly inside the Tkinter window."],
  ].flatMap(([q, a]) => [
    new Paragraph({ children: [new TextRun({ text: q, font:"Arial", size:20, bold:true, color: ACCENT })], spacing:{before:180, after:60} }),
    para(a),
    gap(),
  ]),
];

const references = [
  h1("8. References"),
  bullet("Python Documentation – https://docs.python.org/3/"),
  bullet("Tkinter Reference – https://docs.python.org/3/library/tkinter.html"),
  bullet("Pandas Documentation – https://pandas.pydata.org/docs/"),
  bullet("NumPy Documentation – https://numpy.org/doc/"),
  bullet("Matplotlib Documentation – https://matplotlib.org/stable/"),
  bullet("PyMongo Documentation – https://pymongo.readthedocs.io/"),
  bullet("MongoDB Manual – https://www.mongodb.com/docs/manual/"),
  bullet("Effbot Tkinter Guide – https://effbot.org/tkinterbook/"),
];

// ── Build document ─────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{ level:0, format:LevelFormat.BULLET, text:"•", alignment:AlignmentType.LEFT,
                 style:{ paragraph:{ indent:{ left:720, hanging:360 } } } }],
    }],
  },
  styles: {
    default: { document: { run: { font:"Arial", size:20 } } },
    paragraphStyles: [
      { id:"Heading1", name:"Heading 1", basedOn:"Normal", next:"Normal", quickFormat:true,
        run:{ size:32, bold:true, font:"Arial", color:ACCENT },
        paragraph:{ spacing:{before:360,after:120}, outlineLevel:0 } },
      { id:"Heading2", name:"Heading 2", basedOn:"Normal", next:"Normal", quickFormat:true,
        run:{ size:26, bold:true, font:"Arial", color:DARK },
        paragraph:{ spacing:{before:240,after:80}, outlineLevel:1 } },
    ],
  },
  sections: [{
    properties: {
      page: { size:{ width:12240, height:15840 }, margin:{ top:1080, right:1080, bottom:1080, left:1080 } },
    },
    children: [
      ...cover,
      ...abstract,
      ...intro,
      ...problemStatement,
      ...methodology,
      ...tools,
      ...results,
      ...conclusion,
      ...viva,
      ...references,
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/home/claude/grocery_ims/Project_Report.docx", buf);
  console.log("Report generated!");
});
