import streamlit as st
import pandas as pd
from calculator import calculate_total
from save_to_db import save_to_db, save_bill_csv

st.markdown("""
    <style>
    /* Main background */
    .main {
       background-color: #f8f9fa;
       padding: 20px;
    }
    /* Title */
    h1 {
        color: #2C3E50;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
    }
    /* Section headers */
    h3 {
        color: #2980B9;
        font-family: 'Arial', sans-serif;
        margin-top: 20px;
    }
    /* Buttons */
    div.stButton > button {
        background-color: #27AE60;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-size: 16px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #219150;
        transform: scale(1.02);
    }
    /* Table styles */
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th {
        background-color: #3498DB;
        color: white;
        padding: 8px;
    }
    td {
        padding: 8px;
    }
    /* Success Box */
    .stSuccess {
        background-color: #D4EDDA !important;
        color: #155724 !important;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_menu():
    df = pd.read_csv("menu.csv", dtype={'Food_ID': str})
    menu = {}
    for _, row in df.iterrows():
        fid = str(row['Food_ID'])
        menu[fid] = {
            'Food_Name': row['Food_Name'],
            'Price': float(row['Price']),
            'GST': float(row['GST'])
        }
    return menu, df


menu, menu_df = load_menu()

st.title("Restaurant Billing System")

st.markdown('### Menu')
st.dataframe(menu_df.style.set_properties(**{
    'background-color': '#ECF0F1',
    'color': 'black',
    'border-color': 'black'
}))

st.markdown('### Take Order')
order = {}
# Use unique keys for number_input so Streamlit keeps state correctly
for fid in menu:
    qty = st.number_input(
        f"{menu[fid]['Food_Name']} (ID: {fid}) - Qty",
        min_value=0, step=1, key=f"qty_{fid}"
    )
    if qty > 0:
        order[fid] = qty

st.markdown("### Service Mode")
mode = st.radio("", ["Dine-in", "Takeaway"], horizontal=True)

st.markdown("### Payment Mode")
payment_mode = st.radio("", ["Cash", "Card", "UPI"], horizontal=True)

apply_discount = st.checkbox("Apply Discount")
discount_percent = 0
if apply_discount:
    discount_percent = st.slider("Discount Percentage", min_value=0, max_value=100, value=10)

# ==== Generate bill and perform all actions inside the button handler ====
if st.button("Generate Bill"):
    if not order:
        st.warning("Please select at least one item.")
    else:
        total_amount = 0.0
        bill_items = []
        # Build bill items and compute totals
        for fid, qty in order.items():
            food_name = menu[fid]['Food_Name']
            price = menu[fid]['Price']
            gst = menu[fid]['GST']
            unit_price_gst, total_price = calculate_total(price, gst, qty, discount_percent)
            total_amount += total_price
            bill_items.append([fid, food_name, qty, unit_price_gst, total_price])

        # Save to databases (returns timestamp string)
        timestamp = save_to_db(order, menu, mode, payment_mode, discount_percent)

        # Prepare bill_info and save CSV (save_bill_csv will create folder if needed)
        bill_info = {
            'timestamp': timestamp.replace("_", " "),
            'service_mode': mode,
            'payment_mode': payment_mode,
            'items': bill_items,
            'total_amount': round(total_amount, 2)
        }
        save_bill_csv(bill_info)

        # Show results
        st.success("Order saved successfully!")
        st.markdown('### Bill Summary')
        st.write(f"**Timestamp:** {bill_info['timestamp']}")
        st.write(f"**Service Mode:** {mode}")
        st.write(f"**Payment Mode:** {payment_mode}")
        st.write(f"**Discount Applied:** {discount_percent}%")
        st.write(f"**Total Bill:** ₹ {round(total_amount, 2)}")

        st.table(pd.DataFrame(bill_items, columns=[
            "Food ID", "Food Name", "Qty", "Unit Price (with GST)", "Total Price"
        ]))

        # ---- Download button (downloads exactly what's displayed) ----
        bill_df = pd.DataFrame(bill_items, columns=[
            "Food ID", "Food Name", "Qty", "Unit Price (with GST)", "Total Price"
        ])

        bill_header = pd.DataFrame({
            "Field": ["Timestamp", "Service Mode", "Payment Mode", "Discount (%)", "Total Amount"],
            "Value": [
                bill_info['timestamp'],
                mode,
                payment_mode,
                discount_percent,
                round(total_amount, 2)
            ]
        })

        combined_csv = bill_header.to_csv(index=False) + "\n" + bill_df.to_csv(index=False)

        st.download_button(
            label="Download Bill (CSV)",
            data=combined_csv,
            file_name=f"bill_{timestamp}.csv",
            mime="text/csv"
        )
