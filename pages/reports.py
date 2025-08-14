import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

BILLS_FOLDER = "bills"
MENU_FILE = "menu.csv"

def load_menu():
    df = pd.read_csv(MENU_FILE, dtype={'Food_ID': str})
    menu = {}
    for _, row in df.iterrows():
        menu[str(row['Food_ID'])] = {
            "Food_Name": row["Food_Name"],
            "Price": float(row["Price"]),
            "GST": float(row["GST"]),
            "Cost": float(row["Cost"]) if "Cost" in df.columns else None
        }
    return menu

def load_all_bills():
    all_data = []
    for file in os.listdir(BILLS_FOLDER):
        if file.endswith(".csv"):
            try:
                # Extract timestamp from filename: bill_YYYY-MM-DD_HH-MM-SS.csv
                timestamp_str = "_".join(file.replace(".csv", "").split("_")[1:])
                bill_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H-%M-%S")
            except Exception:
                bill_date = None

            df = pd.read_csv(os.path.join(BILLS_FOLDER, file))
            if "Food ID" in df.columns:
                df["Date"] = bill_date
                all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()

def get_reports(df, menu):
    reports = {}
    now = datetime.now()

    periods = {
        "daily": now - timedelta(days=1),
        "weekly": now - timedelta(weeks=1),
        "monthly": now - timedelta(days=30)
    }

    for period_name, start_date in periods.items():
        if "Date" in df.columns and df["Date"].notnull().any():
            filtered = df[df["Date"] >= start_date]
        else:
            filtered = df.copy()  # If no date, show all

        if filtered.empty:
            reports[period_name] = (pd.DataFrame(), pd.DataFrame())
            continue

        sold_summary = (
            filtered.groupby(["Food ID", "Food Name"])["Qty"].sum()
            .reset_index()
            .sort_values(by="Qty", ascending=False)
        )

        if menu[next(iter(menu))]["Cost"] is not None:
            filtered["Profit"] = filtered.apply(
                lambda x: (menu[str(x["Food ID"])]["Price"] - menu[str(x["Food ID"])]["Cost"]) * x["Qty"],
                axis=1
            )
        else:
            filtered["Profit"] = filtered["Total Price"]

        profit_summary = (
            filtered.groupby(["Food ID", "Food Name"])["Profit"].sum()
            .reset_index()
            .sort_values(by="Profit", ascending=False)
        )

        reports[period_name] = (sold_summary, profit_summary)

    return reports

def save_reports(reports):
    report_files = {}
    for period, (sold_df, profit_df) in reports.items():
        sold_file = f"{period}_most_sold.csv"
        profit_file = f"{period}_most_profitable.csv"
        sold_df.to_csv(sold_file, index=False)
        profit_df.to_csv(profit_file, index=False)
        report_files[period] = (sold_file, profit_file)
    return report_files

# ---------------- STREAMLIT APP ----------------
st.title("📊 Restaurant Sales Reports")

menu = load_menu()
all_bills_df = load_all_bills()

if all_bills_df.empty:
    st.warning("⚠ No bills found in folder. Please generate some bills first.")
else:
    reports = get_reports(all_bills_df, menu)
    report_files = save_reports(reports)

    for period, (sold_file, profit_file) in report_files.items():
        st.subheader(f"📅 {period.capitalize()} Reports")
        most_sold, most_profit = reports[period]

        st.write("**Most Sold Items**")
        st.dataframe(most_sold)
        st.download_button(
            label=f"⬇ Download {period.capitalize()} Most Sold CSV",
            data=most_sold.to_csv(index=False),
            file_name=sold_file,
            mime="text/csv"
        )

        st.write("**Most Profitable Items**")
        st.dataframe(most_profit)
        st.download_button(
            label=f"⬇ Download {period.capitalize()} Most Profitable CSV",
            data=most_profit.to_csv(index=False),
            file_name=profit_file,
            mime="text/csv"
        )
