# 📊 Daily Sales Report & Inventory Management System

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-CSS3-E34F26?style=for-the-badge&logo=html5&logoColor=white)

A full-stack web application designed to streamline daily retail operations[cite: 2, 3]. This tool allows users to manage product inventory, record real-time sales transactions, validate stock levels, and automatically generate timestamped `.csv` sales reports with summary analytics[cite: 2, 3].

## ✨ Key Features

* **Dynamic Inventory Management:** Add multiple products with unique Product IDs, names, unit prices, and initial stock quantities[cite: 2, 3].
* **Real-Time Sales Recording:** Live-synced product dropdowns automatically update as inventory items are added or modified.
* **Strict Stock & Input Validation:** Both client-side and server-side checks prevent negative values, duplicate Product IDs, and sales exceeding available stock[cite: 2, 3].
* **Automated Analytics Engine:** Instantly computes:
  * **Total Revenue** across all recorded transactions[cite: 2, 3].
  * **Average Sale Value** per unit sold[cite: 2, 3].
  * **Best-Selling Product** (Maximum Sold) and **Lowest-Selling Product** (Minimum Sold)[cite: 2, 3].
* **Automatic CSV Report Archiving:** Automatically generates UTF-8 encoded `.csv` reports (`sales_report_YYYY-MM-DD_HH-MM-SS.csv`) inside a dedicated `reports/` directory and provides one-click browser downloads.
* **Dual-Mode Execution (Server + Offline Fallback):** Runs seamlessly with the Flask backend to store reports on the server, while featuring a built-in client-side fallback that generates and downloads CSV reports directly in the browser if the server is offline.

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3 (Responsive Grid Layout), Vanilla JavaScript (`fetch` API, DOM Manipulation, Blob CSV Generation)
* **Backend:** Python 3, Flask
* **Data Storage & Export:** Python `csv` module, `pathlib` file management, UTF-8-SIG encoding for Microsoft Excel compatibility

## 📂 Project Structure

```text
daily-sales-report/
├── Dail_sales_report.py      # Flask backend server & CSV report generator
├── Dail_sales_report.html    # Responsive frontend UI & client-side logic
├── reports/                  # Auto-generated directory storing timestamped CSV files
│   └── sales_report_YYYY-MM-DD_HH-MM-SS.csv
└── README.md                 # Project documentation