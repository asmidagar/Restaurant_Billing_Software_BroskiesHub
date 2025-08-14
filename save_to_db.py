import sqlite3
from datetime import datetime
from calculator import calculate_total
import re
import os
import csv

def save_to_db(order, menu, mode, payment_mode,discount_percent):
    conn_tran = sqlite3.connect("transactions.db")
    cursor_tran = conn_tran.cursor()

    conn_bill = sqlite3.connect("bill.db")
    cursor_bill = conn_bill.cursor()

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    cursor_tran.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_mode TEXT NOT NULL,
            discount_percent INTEGER,
            total_amount REAL NOT NULL,
            timestamp TEXT NOT NULL,
            payment_mode TEXT NOT NULL
        )
    """)

    cursor_bill.execute("""
        CREATE TABLE IF NOT EXISTS bill (
            order_id INTEGER,
            food_id TEXT,
            food_name TEXT,
            qty INTEGER,
            unit_price_gst REAL,
            total_price_gst REAL,
            discount_percent INTEGER,
            service_mode TEXT,
            timestamp TEXT
        )
    """)

    grand_total = 0
    for fid, qty in order.items():
        price = menu[fid]['Price']
        gst = menu[fid]['GST']
        unit_price_gst, total_price = calculate_total(price, gst, qty, discount_percent)
        grand_total += total_price

    cursor_tran.execute("""
        INSERT INTO transactions (service_mode, discount_percent, total_amount, timestamp, payment_mode)
        VALUES (?, ?, ?, ?, ?)
    """, (mode, discount_percent, grand_total, now, payment_mode))

    order_id = cursor_tran.lastrowid

    for fid, qty in order.items():
        food_name = menu[fid]['Food_Name']
        price = menu[fid]['Price']
        gst = menu[fid]['GST']

        cursor_bill.execute("""
            INSERT INTO bill (order_id, food_id, food_name, qty, unit_price_gst,
                              total_price_gst, discount_percent, service_mode, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, fid, food_name, qty, unit_price_gst,
              total_price, discount_percent, mode, now))

    conn_tran.commit()
    conn_bill.commit()
    conn_tran.close()
    conn_bill.close()

    print("\nOrder saved successfully to database.")
    return now


def save_bill_csv(bill_info, folder='bills'):
    os.makedirs(folder, exist_ok = True)

    timestamp_str = bill_info['timestamp'].replace(" ","_").replace(":","-")
    filename = os.path.join(folder, f"bill_{timestamp_str}.csv")

    with open(filename, mode = 'w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([
            'Timestamp', 'Service Mode', 'Payment Mode', 'Food ID', 'Food Name',
            'Qty', 'Unit Price (with GST)', 'Total Price', 'Total Bill Amount'
        ])

        for item in bill_info['items']:
            writer.writerow([
                bill_info['timestamp'],
                bill_info['service_mode'],
                bill_info['payment_mode'],
                item[0], item[1], item[2], item[3], item[4],
                bill_info['total_amount']
            ])

    print(f"Bill saved to: {filename}")
