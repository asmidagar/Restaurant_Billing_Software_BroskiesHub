import csv
from calculator import calculate_total
import sqlite3
from save_to_db import save_to_db, save_bill_csv
import os

def load_menu(filename):
    menu = {}
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            fid = row['Food_ID'].upper()
            menu[fid] = {
                'Food_ID': fid,
                'Food_Name': row['Food_Name'].title(),
                'Price': float(row['Price']),
                'GST': float(row['GST'])
            }
    return menu

def display_menu(menu):
    print("\n----MENU----")
    print(f"{'Food_ID':<8} {'Item':<20} {'Price (Rs)':<12}")
    print("-" * 45)
    for fid, details in menu.items():
        print(f"{fid:<8} {details['Food_Name']:<20} Rs. {details['Price']:<.2f}")
    print("-" * 45 + "\n")

def select_eating_mode():
    print("Select eating mode:")
    print("1. Dine-in")
    print("2. Takeaway")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == '1':
            return "Dine-in"
        elif choice == '2':
            return "Takeaway"
        else:
            print("Invalid choice. Please enter 1 or 2.")

def take_order(menu):
    order = {}
    print("\nStart placing order with FOOD ID (Type 'done' when finished):\n")

    while True:
        fid = input("Enter Food ID: ").upper()

        if fid.lower() == 'done':
            if not order:
                print("No items ordered, kindly order something.")
                continue
            break

        if fid not in menu:
            print("Food ID not found. Please try again.")
            continue

        try:
            qty = int(input(f"Enter quantity for {menu[fid]['Food_Name']}: "))
            if qty <= 0:
                print("Quantity must be positive.")
                continue
        except ValueError:
            print("Invalid quantity. Enter a number.")
            continue

        if fid in order:
            order[fid] += qty
        else:
            order[fid] = qty

    return order

def select_payment_mode():
    print("Select payment mode:")
    print("1. Cash")
    print("2. UPI")
    print("3. Card")

    while True:
        choice = input("Enter 1, 2 or 3: ").strip()
        if choice == '1':
            return "Cash"
        elif choice == '2':
            return "UPI"
        elif choice == '3':
            return "Card"
        else:
            print("Invalid Choice. Please enter 1,2 or 3.")


def print_bill(timestamp):
    menu = load_menu("menu.csv")

    conn = sqlite3.connect("bill.db")
    cursor = conn.cursor()
    cursor.execute("""
            SELECT food_id, food_name, qty, unit_price_gst, total_price_gst, service_mode
            FROM bill
            WHERE timestamp = ?
    """, (timestamp,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("Bill not found")
        return
    
    total_amount = sum(row[4] for row in rows)
    service_mode = rows[0][5]

    conn_txn = sqlite3.connect("transactions.db")
    cursor_txn = conn_txn.cursor()
    cursor_txn.execute("SELECT payment_mode, discount_percent FROM transactions WHERE timestamp = ? LIMIT 1", (timestamp,))
    result = cursor_txn.fetchone()
    conn_txn.close()

    payment_mode = result[0] if result else "N/A"
    discount_applied = float(result[1]) if result and result[-1] else 0.0

    print("\n" + "-"*50)
    print("               BILL RECEIPT")
    print("-"*50)
    print(f"Service Mode     : {service_mode}")
    print(f"Payment Mode     : {payment_mode}")
    print(f"Timestamp        : {timestamp}")
    print(f"Discount Applied : {discount_applied}%")
    print("-"*50)
    print(f"{'Food ID':<8} {'Item':<18} {'Qty':<4} {'Unit Price':<10} {'GST%':<5} {'Total'}")
    print("-" * 50)

    for row in rows:
        fid, name, qty, unit_price_gst, total_price_gst, _ = row
        unit_price = menu[fid]['Price']
        gst = menu[fid]['GST']
        print(f"{fid:<8} {name:<18} {qty:<4} Rs.{unit_price:<9.2f} {gst:<5.1f} Rs.{total_price_gst:.2f}")

    print("-" * 50)
    print(f"Total Amount     : Rs. {total_amount:.2f}")
    print("-" * 50)
    print("        Thank you, visit again!")
    print("-" * 50 + "\n")

    return {
        'timestamp': timestamp,
        'service_mode': service_mode,
        'payment_mode': payment_mode,
        'total_amount': round(total_amount, 2),
        'discount_applied': discount_applied,
        'items': rows
    }

def main():
    print("Welcome to the restaurant!")
    menu = load_menu("menu.csv")
    display_menu(menu)

    eating_mode = select_eating_mode()
    print(f"Selected Eating Mode: {eating_mode}")
    order = take_order(menu)

    if not order:
        print("No items selected. Order Cancelled.\n")
        return

    payment_mode = select_payment_mode()

    try:
        discount_percent = float(input("Enter discount % (or 0 if none): ").strip())
        if discount_percent < 0 or discount_percent > 100:
            print("Invalid discount. Setting to 0.")
            discount_percent = 0
    except ValueError:
        print("Invalid input. Discount set to 0.")
        discount_percent = 0

    # Prepare order items for DB
    bill_items = []
    for fid, qty in order.items():
        food = menu[fid]
        unit_price = food['Price']
        gst = food['GST']

        # Calculate prices
        from calculator import calculate_total
        total_price, unit_price_gst, total_price_gst = calculate_total(unit_price, gst, qty, discount_percent)

        bill_items.append({
            'food_id': fid,
            'food_name': food['Food_Name'],
            'qty': qty,
            'unit_price_gst': unit_price_gst,
            'total_price_gst': total_price_gst,
            'service_mode': eating_mode
        })

    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to database
    from save_to_db import save_transaction, save_bill, save_bill_csv
    save_transaction(timestamp, payment_mode, discount_percent)
    save_bill(timestamp, bill_items)

    # Print and save bill
    bill_info = print_bill(timestamp)
    if bill_info:
        save_bill_csv(bill_info)

if __name__ == "__main__":
    main()
