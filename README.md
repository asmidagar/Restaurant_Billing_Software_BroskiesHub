# Restaurant Billing & Sales Analysis System

## 📌 Overview
This project is a **Restaurant Billing Software** built using **Python** and **Streamlit**.  
It allows restaurant staff to take orders, calculate bills, save them to a database, generate reports, and analyze sales performance.  
The software is designed for **real-time order management** and **detailed analytics** including daily, weekly, and monthly sales reports.

This project is part of my **Python Internship** under **BroskiesHub**.

---

## 🚀 Features
- 📋 **Menu Loading** from a CSV file.
- 🍽 **Order Taking** with Food ID & Quantity.
- 🏷 **Eating Mode Selection** (Dine-in / Takeaway).
- 💰 **Automatic Bill Calculation** with GST.
- 🗂 **Separate Billing Table** for order details.
- 📂 **Real-time Bill Storage** in SQLite databases (`transactions.db` and `bill.db`).
- 📄 **Downloadable Bill** directly from the Streamlit frontend.
- 📊 **Daily, Weekly, and Monthly Reports**:
  - Most Sold Items
  - Most Profitable Items

---

## 🛠 Tech Stack
- **Python**
- **Streamlit** (Frontend)
- **SQLite** (Database)
- **Pandas** (Data Handling)
- **CSV** for Menu Storage

---

## 📂 Project Structure
restaurant-billing/
│-- app.py # Main Streamlit app
│-- calculator.py # Billing calculation logic
│-- save_to_db.py # Database saving functions
│-- menu.csv # Menu data
│-- transactions.db # Transaction database
│-- bill.db # Billing database
│-- reports.py # Sales analysis logic
│-- .gitignore # Ignore unnecessary files
│-- README.md # Project documentation

---

## 📊 Report Generation
- **Daily Report** → `daily_report.csv`
- **Weekly Report** → `weekly_report.csv`
- **Monthly Report** → `monthly_report.csv`

Each report includes:
- **Most Sold Items**
- **Items with Highest Profit**

---

## ▶️ How to Run
1. Clone the repository:
   git clone <repo-link>
2. Navigate to the project folder:
   cd restaurant-billing
3. Install dependencies:
  pip install -r requirements.txt 
4. Run the Streamlit app:
  streamlit run app.py

## 📝 Internship Credit
This project is a part of my Python Internship at BroskiesHub.

## 📜 License
This project is for educational purposes. You can modify it for personal or commercial use.
