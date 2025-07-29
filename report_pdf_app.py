import streamlit as st
import pandas as pd
import random
from xhtml2pdf import pisa
from io import BytesIO
from jinja2 import Template  # ✅ Only import Template, not Environment/FileSystemLoader
from datetime import datetime
import numpy as np

st.set_page_config(layout="wide")
st.title("📋 S.H Reports")

# Function to convert HTML to PDF using xhtml2pdf
def html_to_pdf(source_html):
    """Convert HTML string to PDF bytes using xhtml2pdf"""
    output = BytesIO()
    pisa_status = pisa.CreatePDF(source_html, dest=output)
    
    if pisa_status.err:
        st.error("Error generating PDF")
        return None
    
    return output.getvalue()

# ===== EMBEDDED CSV DATA =====
def get_default_department_data():
    """Return default department data as a pandas DataFrame"""
    
    # Default department data - you can modify this with your actual data
    default_data = {
        'Dept#': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 100, 9998, 9999],
        'Description': ['CIGARETTES', 'Grocery TAX', 'BEER', 'DAIRY', 'SNACKS', 'AUTO', 'CONDOM', 'WATER', 'TOBACCO', 'COFFEE', 'PILLS', 'MEDICINE', 'ENERGY DRINKS', 'GROCERY', 'Bakery', 'CHEW TOBACCO', 'SODA', 'CANDY', 'CHIPS', 'PHONE ACC', 'NEWS PAPER', 'ICE CREAM', 'PHONE CARDS', 'CIGAR', 'ICE', 'DELI', 'MILK SHAKE', 'GLOVES', 'SANTIZER', 'E-Cigarette', 'JUICE', 'HOT FOOD', 'Honey', 'ICED COFFEE', 'MISC', 'MANUAL FUEL DE', 'FUEL DEPOSIT'],
        'Cust#': [0, 89, 1395, 95, 248, 166, 53, 613, 154, 322, 47, 50, 1026, 48, 127, 720, 628, 842, 341, 67, 150, 96, 26, 134, 120, 90, 90, 42, 25, 0, 213, 44, 62, 127, 218, 5924, 0],
        'Items': [0, 111, 243, 102, 266, 207, 68, 736, 251, 552, 57, 64, 1328, 88, 177, 927, 746, 1124, 410, 73, 162, 145, 37, 165, 202, 123, 113, 54, 43, 0, 678, 56, 74, 152, 277, 6940, 0],
        'Gross': [0.0, 524.06, 26646.77, 584.29, 2907.31, 1806.08, 364.58, 2505.56, 657.28, 1131.98, 323.28, 252.4, 2865.07, 330.65, 1780.11, 1842.39, 2788.85, 772.43, 2001.39, 824.25, 513.52, 1365.78, 93.48, 313.32, 311.2, 421.64, 767.49, 328.7, 81.26, 0.0, 1380.08, 84.34, 886.44, 767.49, 1776.51, 0.0, 0.0],
        'Refunds': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Discounts': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    
    # Create DataFrame
    df = pd.DataFrame(default_data)
    
    # Calculate Net Sales
    df['Net Sales'] = df['Gross'] - df['Refunds'] - df['Discounts']
    
    return df

store_dict = {
    "Shell - Syed Empires": "807606",
    "Shell - Kausar & Sons": "807619",
    "Shell - H & K Mart": "801422",
    "Shell - Hermin Empires": "801927",
    "Gulf  - 33 Chestnut Gasoline": "802214",
    "Shell - KSK Auto Group": "808734",
    "Shell - NSK & Sons": "809715",
    "BP    - S. Michael & Sons": "807594",
    "Gulf  - 688 Freedom Plains": "802975",
    "Gulf  - 100 Route 17": "805873",
    "Gulf  - Kirmani Fresh Market": "809784",
    "Gulf  - Norwich Fresh Market": "803616",
    "Gulf  - 501 Nyack": "807894",
    "76     - One Stop Auto Repair": "803469",
    "Gulf  - Route 22 Dover Plains": "809974",
    "Gulf  - Rockaway Petro Atlantic": "808957",
    "Shell - 220 Northern Bulvd": "806644",
    "Gulf  - Sunrise V.S": "807787",
    "Gulf  - 28 Main Street CT": "808799",
    "Gulf  - 189 Kings Park": "806999",
    "Gulf  - 3389 Route 82": "805858",
    "Gulf  - 600 Tulip Avenue": "804477",
    "Shell - 590 Fordham Road": "802255",
    "Gulf  - 200 23rd Street Enterprise": "806696",
    "Gulf  - 135 Montauk Highway": "805857",
    "Marathon - 32 Germantown Road": "804472",
    "Citgo - 1429 Upper Front Street": "806979"
}

# Tax multipliers by station name
tax_multiplier_by_station = {
    # City Stations (8.875%)
    "Shell - Syed Empires": 1.08875,
    "Shell - Kausar & Sons": 1.08875,
    "Shell - H & K Mart": 1.08875,
    "Shell - Hermin Empires": 1.08875,
    "BP    - S. Michael & Sons": 1.08875,
    "Shell - 590 Fordham Road": 1.08875,

    # Long Island Stations (8.625%)
    "Shell - KSK Auto Group": 1.08625,
    "Shell - NSK & Sons": 1.08625,
    "76     - One Stop Auto Repair": 1.08625,
    "Gulf  - Rockaway Petro Atlantic": 1.08625,
    "Shell - 220 Northern Bulvd": 1.08625,
    "Gulf  - Sunrise V.S": 1.08625,
    "Gulf  - 189 Kings Park": 1.08625,
    "Gulf  - 135 Montauk Highway": 1.08625,

    # Upstate (8.125%)
    "Gulf  - 688 Freedom Plains": 1.08125,
    "Gulf  - 100 Route 17": 1.08125,
    "Gulf  - Route 22 Dover Plains": 1.08125,
    "Gulf  - 3389 Route 82": 1.08125,
    "Gulf  - 600 Tulip Avenue": 1.08125,
    "Gulf  - 200 23rd Street Enterprise": 1.08125,

    # Nayak (8.375%)
    "Gulf  - 33 Chestnut Gasoline": 1.08375,
    "Gulf  - 501 Nyack": 1.08375,

    # Pennsylvania (6.00%)
    "Gulf  - Kirmani Fresh Market": 1.06,

    # Connecticut (6.35%)
    "Gulf  - 28 Main Street CT": 1.0635,
    "Marathon - 32 Germantown Road": 1.0635,

    # Big Hampton (8.00%)
    "Gulf  - Norwich Fresh Market": 1.08,
    "Citgo - 1429 Upper Front Street": 1.08
}

store_names = list(store_dict.keys())
col1, col2 = st.columns(2)
store_name = col1.selectbox("Store Name", options=store_names)
store_id = store_dict[store_name]
col2.text_input("Location ID", value=store_id, disabled=True)

open_period_date = col1.date_input("Opening Period Date", value=datetime.today())
close_period_date = col2.date_input("Close Period Date", value=datetime.today())

# ===== FILE UPLOAD SECTION (NOW OPTIONAL) =====
st.markdown("---")
st.subheader("📁 Department Data")

# Option to use default data or upload custom file
data_source = st.radio(
    "Choose data source:",
    ["Use Default Data", "Upload Custom CSV"],
    help="You can use the built-in default data or upload your own CSV file"
)

df = None
if data_source == "Use Default Data":
    df = get_default_department_data()
    st.success("✅ Default department data loaded successfully!")
    
    # Show data preview
    with st.expander("👀 Preview Default Data"):
        st.dataframe(df.head(10), use_container_width=True)
        st.info(f"📊 Loaded {len(df)} departments")

else:  # Upload Custom CSV
    uploaded_file = st.file_uploader(
        "Upload Department CSV File",
        type=["csv"],
        help="Upload your department sales data in CSV format"
    )
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ File uploaded successfully: {uploaded_file.name}")

st.subheader("CIGARETTES")
c1, c2 = st.columns(2)
cig_items = c1.number_input("Number of Packets Sold", value=0, key="cig_items")
cig_gross = c2.number_input("Cigarette Gross", value=0.0)

# Auto-calculate number of customers (80-90% of packets sold)
if cig_items > 0:
    cig_cust = int(cig_items * random.uniform(0.80, 0.90))
    st.info(f"📊 Calculated Number of Customers: {cig_cust}")
else:
    cig_cust = 0

st.subheader("Electronic-CIGARETTES")
e1, e2 = st.columns(2)
ecig_items = e1.number_input("Number of Packets Sold", value=0, key="ecig_items")
ecig_gross = e2.number_input("E-Cigarette Gross", value=0.0)

# Auto-calculate number of customers (80-90% of packets sold)
if ecig_items > 0:
    ecig_cust = int(ecig_items * random.uniform(0.80, 0.90))
    st.info(f"📊 Calculated Number of Customers: {ecig_cust}")
else:
    ecig_cust = 0

desired_merch_sale = st.number_input("Desired Total Merch Sale (excluding Cigarettes, E-Cigarettes & Fuel)", min_value=0.0, value=0.0, step=100.0)

st.markdown("---")
st.subheader("Fuel Product Report")
fuel_data = {}
fuel_products = ["REG", "PLUS", "SUPER", "DIESEL"]

for product in fuel_products:
    col1, col2 = st.columns(2)
    vol = col1.number_input(f"{product} Volume", min_value=0, value=0)
    amt = col2.number_input(f"{product} Amount", min_value=0.0, value=0.0)
    fuel_data[product] = {"volume": vol, "amount": amt}

fuel_total_volume = sum(row["volume"] for row in fuel_data.values())
fuel_total_amount = sum(row["amount"] for row in fuel_data.values())

# NEW SECTION: Manual MOP Entry
st.markdown("---")
st.subheader("💳 Method of Payment (MOP) Entry")
st.write("Enter the Credit, Debit, and Mobile payment amounts. Cash will be calculated automatically after deducting Pay Out.")

mop_col1, mop_col2, mop_col3 = st.columns(3)

with mop_col1:
    manual_credit = st.number_input(
        "Credit Card Amount", 
        min_value=0.0, 
        value=0.0, 
        step=100.0,
        key="manual_credit",
        help="Enter the total credit card sales amount"
    )

with mop_col2:
    manual_debit = st.number_input(
        "Debit Card Amount", 
        min_value=0.0, 
        value=0.0, 
        step=100.0,
        key="manual_debit",
        help="Enter the total debit card sales amount"
    )

with mop_col3:
    manual_mobile = st.number_input(
        "Mobile Payment Amount", 
        min_value=0.0, 
        value=0.0, 
        step=10.0,
        key="manual_mobile",
        help="Enter the total mobile payment sales amount"
    )

# Calculate total manual entries
manual_total = manual_credit + manual_debit + manual_mobile

# NEW SECTION: Ending Inventory of Fuel
st.markdown("---")
st.subheader("Ending Inventory of Fuel")
st.write("Enter the ending inventory values for the accountant's report:")

inv1, inv2, inv3 = st.columns(3)
with inv1:
    inventory_regular = st.number_input(
        "Regular Inventory", 
        min_value=0, 
        value=0, 
        step=1,
        key="regular_inventory",
        help="Enter the regular fuel inventory amount"
    )
with inv2:
    inventory_super = st.number_input(
        "Super Inventory", 
        min_value=0, 
        value=0, 
        step=1,
        key="super_inventory",
        help="Enter the super fuel inventory amount"
    )
with inv3:
    inventory_diesel = st.number_input(
        "Diesel Inventory", 
        min_value=0, 
        value=0, 
        step=1,
        key="diesel_inventory",
        help="Enter the diesel fuel inventory amount"
    )

excluded_keywords = ["FUEL", "FUEL DEPOSIT", "MANUAL FUEL"]
cig_keyword = "CIGARETTES"
ecig_keyword = "E-CIGARETTE"

# Process data if available (either default or uploaded)
if df is not None:
    cig_mask = df["Description"].str.upper().str.contains(cig_keyword, na=False)
    ecig_mask = df["Description"].str.upper().str.contains(ecig_keyword, na=False)
    fuel_mask = df["Description"].str.upper().apply(lambda x: any(k in x for k in excluded_keywords))
    non_fuel_mask = ~fuel_mask

    cig_only_mask = cig_mask & non_fuel_mask
    ecig_only_mask = ecig_mask & non_fuel_mask
    scalable_mask = ~fuel_mask & ~cig_mask & ~ecig_mask

    df.loc[cig_only_mask, "Cust#"] = cig_cust
    df.loc[cig_only_mask, "Items"] = cig_items
    df.loc[cig_only_mask, "Gross"] = cig_gross

    df.loc[ecig_only_mask, "Cust#"] = ecig_cust
    df.loc[ecig_only_mask, "Items"] = ecig_items
    df.loc[ecig_only_mask, "Gross"] = ecig_gross

    df["Net Sales"] = df["Gross"] - df["Refunds"] - df["Discounts"]
    cig_ecig_net_sales = df.loc[cig_only_mask | ecig_only_mask, "Net Sales"].sum()
    original_net_sales_scalable = df.loc[scalable_mask, "Net Sales"].copy()

    if desired_merch_sale > 0:
        target_net_sales_scalable = desired_merch_sale - cig_ecig_net_sales
        original_net_sum = original_net_sales_scalable.sum()
        if original_net_sum > 0 and target_net_sales_scalable > 0:
            scale_factor = target_net_sales_scalable / original_net_sum
            df.loc[scalable_mask, "Gross"] = (
                (df.loc[scalable_mask, "Gross"] - df.loc[scalable_mask, "Refunds"] - df.loc[scalable_mask, "Discounts"])
                * scale_factor
                + df.loc[scalable_mask, "Refunds"]
                + df.loc[scalable_mask, "Discounts"]
            ).round(2)

    # Remaining pipeline logic continues here (manual fuel rows, random cust/items, PDF rendering, etc.)
    manual_fuel_mask = df["Description"].str.upper().str.contains("MANUAL FUEL DE", na=False)
    df.loc[manual_fuel_mask, "Gross"] = fuel_total_amount
    df.loc[manual_fuel_mask, "Net Sales"] = fuel_total_amount
    df.loc[manual_fuel_mask, "Refunds"] = 0
    df.loc[manual_fuel_mask, "Discounts"] = 0

    df["Net Sales"] = df["Gross"] - df["Refunds"] - df["Discounts"]
    merch_mask = ~fuel_mask
    total_merch_gross = df.loc[merch_mask, "Gross"].sum()
    df["% of Sales"] = 0.0
    df.loc[merch_mask, "% of Sales"] = round((df.loc[merch_mask, "Gross"] / total_merch_gross) * 100, 2)

    df.loc[scalable_mask, "Cust#"] += np.random.randint(11, 31, size=scalable_mask.sum())
    df.loc[scalable_mask, "Items"] += np.random.randint(11, 31, size=scalable_mask.sum())

    total_merch_sale = df.loc[merch_mask, "Net Sales"].sum()
    multiplier = tax_multiplier_by_station.get(store_name, 1.08265)  # fallback multiplier
    tax_rate = round((multiplier - 1) * 100, 3)  # Convert multiplier to percent rate
    sales_tax = round(total_merch_sale * (tax_rate / 100), 2)

    tot_taxes = sales_tax
    incl_taxes = round(total_merch_sale + sales_tax, 2)

    summary_row = pd.DataFrame({
        "Dept#": [""],
        "Description": ["Total Merch Sale"],
        "Cust#": [""],
        "Items": [""],
        "% of Sales": [""],
        "Gross": [""],
        "Refunds": [""],
        "Discounts": [""],
        "Net Sales": [round(total_merch_sale, 2)]
    })

    df_final = pd.concat([df, summary_row], ignore_index=True)
    st.dataframe(df_final)

    # Calculate total MOP sales
    total_mop_sales = total_merch_sale + fuel_total_amount + tot_taxes

    # Generate Pay Out value (reduced range from 3000-9000)
    pay_out = round(random.uniform(3000, 9000), 2)

    # NEW: Calculate Cash after deducting Pay Out
    manual_mop_values = {
        "credit": manual_credit,
        "debit": manual_debit,
        "mobile": manual_mobile,
        "cash": max(0, total_mop_sales - manual_total - pay_out)  # Subtract pay_out from available cash
    }

    # Show MOP calculations
    st.markdown("---")
    st.subheader("💰 MOP Calculations Summary")

    mop_info_col1, mop_info_col2, mop_info_col3, mop_info_col4, mop_info_col5 = st.columns(5)

    with mop_info_col1:
        st.metric("Manual Entries Total", f"${manual_total:,.2f}")

    with mop_info_col2:
        st.metric("Pay Out", f"${pay_out:,.2f}")

    with mop_info_col3:
        calculated_cash = manual_mop_values["cash"]
        st.metric("Calculated Cash", f"${calculated_cash:,.2f}")

    with mop_info_col4:
        actual_total = sum(manual_mop_values.values())
        st.metric("Total MOP (excl. Pay Out)", f"${actual_total:,.2f}")

    with mop_info_col5:
        expected_after_payout = total_mop_sales - pay_out
        st.metric("Expected (after Pay Out)", f"${expected_after_payout:,.2f}")

    # Validation check
    if abs(actual_total - expected_after_payout) > 0.01:  # Allow for small rounding differences
        st.warning(f"⚠️ MOP total (${actual_total:,.2f}) doesn't match expected after pay out (${expected_after_payout:,.2f})")
        st.info("The cash amount has been adjusted to balance the total.")
    else:
        st.success("✅ MOP amounts balance correctly after pay out deduction!")

    # Show detailed breakdown
    with st.expander("📊 Detailed MOP Breakdown"):
        # Show the calculation formula
        st.write("**Calculation Formula:**")
        st.write(f"Cash = Total MOP Sales - Credit - Debit - Mobile - Pay Out")
        st.write(f"Cash = ${total_mop_sales:,.2f} - ${manual_credit:,.2f} - ${manual_debit:,.2f} - ${manual_mobile:,.2f} - ${pay_out:,.2f}")
        st.write(f"Cash = ${calculated_cash:,.2f}")
        
        st.markdown("---")
        
        mop_breakdown = pd.DataFrame({
            'Payment Method': ['Credit Card', 'Debit Card', 'Mobile Payment', 'Cash', 'Pay Out', 'TOTAL MOP SALES'],
            'Amount': [f"${manual_credit:,.2f}", f"${manual_debit:,.2f}", f"${manual_mobile:,.2f}", 
                      f"${calculated_cash:,.2f}", f"${pay_out:,.2f}", f"${total_mop_sales:,.2f}"],
            'Note': ['Manual Entry', 'Manual Entry', 'Manual Entry', 
                    'Auto-calculated', 'Deducted from Cash', 'Fuel + Merch Sales']
        })
        st.dataframe(mop_breakdown, use_container_width=True)
        
        # Show verification
        st.write("**Verification:**")
        verification_total = manual_credit + manual_debit + manual_mobile + calculated_cash + pay_out
        st.write(f"Credit + Debit + Mobile + Cash + Pay Out = ${verification_total:,.2f}")
        st.write(f"Total MOP Sales = ${total_mop_sales:,.2f}")
        if abs(verification_total - total_mop_sales) < 0.01:
            st.success("✅ All amounts balance correctly!")
        else:
            st.error(f"❌ Difference: ${abs(verification_total - total_mop_sales):,.2f}")

    # MAIN REPORT FUNCTION (Fixed and Complete)
    def build_main_report(manual_mop_vals, total_mop_sales_val, df_final_param, merch_mask_param, total_merch_sale_param, sales_tax_param, tot_taxes_param, incl_taxes_param, total_merch_gross_param, total_discounts_param, total_refunds_param, total_percent_param, pay_out_val):
        
        # Complete professional template with all sections
        template_str = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Department Full Report</title>
    <style>
        body {
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
            line-height: 1.3;
            margin: 0.5in;
            padding: 0;
            color: #000;
            background: #fff;
        }
        .header {
            text-align: center;
            margin-bottom: 15px;
        }
        .section {
            margin-bottom: 15px;
            page-break-inside: avoid;
        }
        .section-title {
            font-weight: bold;
            margin-bottom: 5px;
            text-decoration: underline;
            font-size: 16px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 8px;
        }
        td, th {
            padding: 2px 4px;
            text-align: left;
            vertical-align: top;
            border: none;
        }
        .right { text-align: right; }
        .center { text-align: center; }
        .line {
            border-bottom: 1px solid #000;
            margin: 8px 0;
            height: 1px;
        }
        .bold { font-weight: bold; }
        .dept-table td {
            border-bottom: 1px dotted #999;
            padding: 3px 5px;
        }
        .dept-table .bold {
            border-bottom: 1px solid #000;
        }
        .summary-line {
            margin: 3px 0;
            font-weight: bold;
        }
        .fuel-table td {
            padding: 2px 5px;
        }
        .fuel-table .bold {
            font-weight: bold;
            border-top: 1px solid #000;
        }
    </style>
</head>
<body>

<div class="header">
    <div class="bold">{{ store_number }}</div>
    <div>Store ID: {{ store_id }}</div>
    <div>Period: {{ period }} to {{ close_period }}</div>
    <div>Department Full Report</div>
</div>

<div class="line"></div>

<div class="section">
    <div class="section-title">DEPARTMENT REPORT</div>
    <table class="dept-table">
        <tr>
            <td class="bold">Dept#</td>
            <td class="bold">Description</td>
            <td class="bold right">Cust#</td>
            <td class="bold right">Items</td>
            <td class="bold right">% Sales</td>
            <td class="bold right">Gross</td>
            <td class="bold right">Refunds</td>
            <td class="bold right">Discounts</td>
            <td class="bold right">Net Sales</td>
        </tr>
        {{ table_rows|safe }}
    </table>
    <div class="line"></div>
    <div class="summary-line">Total Discounts: {{ total_discounts }}</div>
    <div class="summary-line">Total Refunds:   {{ total_refunds }}</div>
    <div class="summary-line">Total Gross:     {{ total_gross }}</div>
    <div class="summary-line">Total Net Sales: {{ total_net_sales }}</div>
</div>

<div class="line"></div>

<div class="section">
    <div class="section-title">MOP SALES</div>
    <table>
        <tr><td>MOP Sales Total</td><td class="right">{{ total_mop_sales }}</td></tr>
        <tr><td>Credit - Card Based</td><td class="right">{{ mop_credit }}</td></tr>
        <tr><td>Debit - Card Based</td><td class="right">{{ mop_debit }}</td></tr>
        <tr><td>Mobile - Card Based</td><td class="right">{{ mop_mobile }}</td></tr>
        <tr><td>Cash</td><td class="right">{{ mop_cash }}</td></tr>
    </table>
</div>

<div class="line"></div>

<div class="section">
    <div class="section-title">FUEL TIER / PRODUCT REPORT</div>
    <table class="fuel-table">
        <tr>
            <td class="bold">Product</td>
            <td class="bold right">Volume</td>
            <td class="bold right">Amount</td>
        </tr>
        {% for product, data in fuel_data.items() %}
        <tr>
            <td>{{ product }}</td>
            <td class="right">{{ "{:,.0f}".format(data.volume) }}</td>
            <td class="right">{{ "{:,.2f}".format(data.amount) }}</td>
        </tr>
        {% endfor %}
        <tr class="bold">
            <td>Total</td>
            <td class="right">{{ "{:,.0f}".format(fuel_total_volume) }}</td>
            <td class="right">{{ "{:,.2f}".format(fuel_total_amount) }}</td>
        </tr>
    </table>
</div>

<div class="line"></div>

<div class="section">
    <div class="section-title">MOP CANCEL/REFUND</div>
    <table>
        <tr><td>MOP Cancel Refund</td><td class="right">{{ mop_cancel_refund }}</td></tr>
        <tr><td>Other Refund</td><td class="right">{{ other_refund }}</td></tr>
        <tr><td>Payment Out</td><td class="right">0.00</td></tr>
        <tr><td>Payment In</td><td class="right">0.00</td></tr>
        <tr><td>Total to Account For</td><td class="right">{{ total_to_account_for }}</td></tr>
        <tr><td>CREDIT - Card Based</td><td class="right">{{ credit_card_based }}</td></tr>
        <tr><td>CASH</td><td class="right">{{ cash_based }}</td></tr>
        <tr><td>Tot MOP Cancel/Refunds</td><td class="right">{{ total_to_account_for }}</td></tr>
    </table>
</div>

<div class="line"></div>

<div class="section">
    <div class="section-title">PAYMENT OUT</div>
    <table>
        <tr><td>Cash Back</td><td class="right">0</td></tr>
        <tr><td>Pay Out</td><td class="right">{{ pay_out }}</td></tr>
        <tr><td>Adjust for Vendor Payments</td><td class="right">0.00</td></tr>
        <tr><td>Change/Check</td><td class="right">0.00</td></tr>
        <tr><td>In House</td><td class="right">0.00</td></tr>
        <tr><td>Safe Drops</td><td class="right">{{ safe_drops }}</td></tr>
        <tr><td>CASH</td><td class="right">{{ safe_drops }}</td></tr>
        <tr><td>Tot Payment Out</td><td class="right">{{ total_payment_out }}</td></tr>
    </table>
</div>

<div class="line"></div>

<div class="section">
    <div class="section-title">PAYMENT IN</div>
    <table>
        <tr><td>Cash Back Cancel</td><td class="right">0</td></tr>
        <tr><td>Pay In</td><td class="right">0</td></tr>
        <tr><td>In House</td><td class="right">0</td></tr>
        <tr><td>Safe Loans</td><td class="right">0</td></tr>
        <tr><td>Tot Payment In</td><td class="right">0</td></tr>
    </table>
</div>

<div class="line"></div>

<div class="section">
    <div class="section-title">MEMO ITEMS (LEFT)</div>
    <table>
        <tr>
            <td class="bold">Category</td>
            <td class="bold right">Count</td>
            <td class="bold right">Amount</td>
        </tr>
        <tr><td>Items</td><td class="right">{{ total_items }}</td><td class="right"></td></tr>
        <tr><td>Customer</td><td class="right">{{ total_customers }}</td><td class="right"></td></tr>
        <tr><td>Void Lines</td><td class="right">{{ void_lines_count }}</td><td class="right">{{ void_lines_amount }}</td></tr>
        <tr><td>Void Tickets</td><td class="right">{{ void_tickets_count }}</td><td class="right">{{ void_tickets_amount }}</td></tr>
        <tr><td>Positive</td><td class="right">{{ positive_count }}</td><td class="right">{{ positive_amount }}</td></tr>
        <tr><td>Negative</td><td class="right">{{ negative_count }}</td><td class="right">{{ negative_amount }}</td></tr>
        <tr><td>Prepaid Recharge</td><td class="right">0</td><td class="right">0</td></tr>
    </table>
</div>

<div class="line"></div>

<div class="section">
    <div class="section-title">MEMO ITEMS (RIGHT)</div>
    <table>
        <tr>
            <td class="bold">Category</td>
            <td class="bold right">Count</td>
            <td class="bold right">Amount</td>
        </tr>
        <tr><td>Suspended</td><td class="right">{{ suspended_count }}</td><td class="right">{{ suspended_amount }}</td></tr>
        <tr><td>Suspend/Void</td><td class="right">{{ suspend_void_count }}</td><td class="right">{{ suspend_void_amount }}</td></tr>
        <tr><td>Coin Dispenser</td><td class="right">0</td><td class="right">0.00</td></tr>
        <tr><td>Vendor Payments</td><td class="right">0</td><td class="right">0.00</td></tr>
        <tr><td>Safe Drop Cancels</td><td class="right">0</td><td class="right">0.00</td></tr>
        <tr><td>Prepaid Activation</td><td class="right">0</td><td class="right">0.00</td></tr>
    </table>
</div>

<div class="line"></div>

<div class="section">
    <div class="section-title">TOTALS</div>
    <table>
        <tr><td>Cash Back Fee</td><td class="right">0</td></tr>
        <tr><td>Cancel/Refund Cash Back Fee</td><td class="right">0</td></tr>
        <tr><td>Debit Fee</td><td class="right">0</td></tr>
        <tr><td>Fuel Sales</td><td class="right">{{ fuel_sales }}</td></tr>
        <tr><td>Merch Sales</td><td class="right">{{ merch_sales }}</td></tr>
        <tr><td>FUEL DISCOUNT</td><td class="right">0</td></tr>
        <tr><td>Refund Taxes</td><td class="right">0</td></tr>
        <tr><td>Sales Taxes</td><td class="right">{{ sales_taxes }}</td></tr>
        <tr><td>Tot Taxes</td><td class="right">{{ tot_taxes }}</td></tr>
        <tr><td>Incl Taxes</td><td class="right">{{ incl_taxes }}</td></tr>
    </table>
</div>

<div class="line"></div>

<div class="center">
    <div>*** END OF REPORT ***</div>
</div>

</body>
</html>
        '''
        
        # Generate other Payment Out values (keep existing logic for other items)
        safe_drops = round(random.uniform(30000, 49000), 2)
        total_payment_out = round(pay_out_val + safe_drops, 2)

        # Generate random MOP Cancel/Refund values
        mop_cancel_refund = round(random.uniform(89, 199), 2)
        other_refund = round(random.uniform(12, 99), 2)
        total_to_account_for = round(mop_cancel_refund + other_refund, 2)
        
        credit_percentage = random.uniform(0.2, 0.8)
        credit_card_based = round(total_to_account_for * credit_percentage, 2)
        cash_based = round(total_to_account_for - credit_card_based, 2)

        # Generate random values for Memo Items
        def safe_sum_numeric(series):
            try:
                numeric_series = pd.to_numeric(series, errors='coerce')
                return int(numeric_series.sum()) if not numeric_series.isna().all() else 0
            except:
                return 0

        memo_data = {
            "total_items": safe_sum_numeric(df_final_param['Items']) if 'Items' in df_final_param.columns else 0,
            "total_customers": safe_sum_numeric(df_final_param['Cust#']) if 'Cust#' in df_final_param.columns else 0,
            "void_lines_count": np.random.randint(50, 251),
            "void_lines_amount": round(np.random.uniform(2000, 5000), 2),
            "void_tickets_count": np.random.randint(15, 96),
            "void_tickets_amount": round(np.random.uniform(500, 2000), 2),
            "positive_count": np.random.randint(10, 61),
            "positive_amount": round(np.random.uniform(300, 900), 2),
            "negative_count": np.random.randint(10, 61),
            "negative_amount": round(np.random.uniform(300, 900), 2),
            "suspended_count": np.random.randint(3, 100),
            "suspended_amount": round(np.random.uniform(119, 799), 2),
            "suspend_void_count": np.random.randint(1, 30),
            "suspend_void_amount": round(np.random.uniform(11, 199), 2)
        }

        def generate_random_time():
            hour = random.randint(22, 23)
            if hour == 22:
                minute = random.randint(1, 59)
            else:
                minute = random.randint(0, 49)
            return f"{hour:02d}:{minute:02d}"
        
        open_time = generate_random_time()
        close_time = generate_random_time()

        # Build table rows HTML
        table_html = ""
        for _, row in df_final_param.iterrows():
            table_html += f"""
            <tr class="dept-table">
                <td>{row['Dept#'] if pd.notna(row['Dept#']) else ''}</td>
                <td>{row['Description']}</td>
                <td class="right">{int(row['Cust#']) if pd.notna(row['Cust#']) and str(row['Cust#']).replace('.0', '').isdigit() else ''}</td>
                <td class="right">{int(row['Items']) if pd.notna(row['Items']) and str(row['Items']).replace('.0', '').isdigit() else ''}</td>
                <td class="right">{row['% of Sales'] if pd.notna(row['% of Sales']) else ''}</td>
                <td class="right">{row['Gross'] if pd.notna(row['Gross']) else ''}</td>
                <td class="right">{row['Refunds'] if pd.notna(row['Refunds']) else ''}</td>
                <td class="right">{row['Discounts'] if pd.notna(row['Discounts']) else ''}</td>
                <td class="right">{row['Net Sales'] if pd.notna(row['Net Sales']) else ''}</td>
            </tr>
            """

        context = {
            "store_number": store_name,
            "store_id": store_id,
            "period": f"{open_period_date.strftime('%Y-%m-%d')} {open_time}",
            "close_period": f"{close_period_date.strftime('%Y-%m-%d')} {close_time}",
            "table_rows": table_html,
            "total_gross": f"{total_merch_gross_param:,.2f}",
            "total_net_sales": f"{total_merch_sale_param:,.2f}",
            "total_discounts": f"{total_discounts_param:,.2f}",
            "total_refunds": f"{total_refunds_param:,.2f}",
            "fuel_data": fuel_data,
            "fuel_total_volume": fuel_total_volume,
            "fuel_total_amount": fuel_total_amount,
            "total_mop_sales": f"{total_mop_sales_val:,.2f}",
            "fuel_sales": f"{fuel_total_amount:,.2f}",
            "merch_sales": f"{total_merch_sale_param:,.2f}",
            "sales_taxes": f"{sales_tax_param:,.2f}",
            "tot_taxes": f"{tot_taxes_param:,.2f}",
            "incl_taxes": f"{incl_taxes_param:,.2f}",
            "pay_out": f"{pay_out_val:,.2f}",
            "safe_drops": f"{safe_drops:,.2f}",
            "total_payment_out": f"{total_payment_out:,.2f}",
            "mop_cancel_refund": f"{mop_cancel_refund:.2f}",
            "other_refund": f"{other_refund:.2f}",
            "total_to_account_for": f"{total_to_account_for:.2f}",
            "credit_card_based": f"{credit_card_based:.2f}",
            "cash_based": f"{cash_based:.2f}",
            "mop_credit": f"{manual_mop_vals['credit']:,.2f}",
            "mop_debit": f"{manual_mop_vals['debit']:,.2f}",
            "mop_mobile": f"{manual_mop_vals['mobile']:,.2f}",
            "mop_cash": f"{manual_mop_vals['cash']:,.2f}",
            **memo_data
        }

        # Render the template
        template = Template(template_str)
        html_content = template.render(context)
        return html_content

    # ACCOUNTANT REPORT FUNCTION (Updated to use xhtml2pdf)
    def build_accountant_report():
        # Calculate other sales (excluding cigarettes and e-cigarettes)
        other_sales = total_merch_sale - cig_gross - ecig_gross
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Accountant Report - {store_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .store-info {{ margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
                th {{ background-color: #f0f0f0; }}
                .right {{ text-align: right; }}
                .section {{ margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Accountant's Report</h1>
                <h2>{store_name}</h2>
                <p>Store ID: {store_id}</p>
                <p>Report Period: {open_period_date.strftime('%Y-%m-%d')} to {close_period_date.strftime('%Y-%m-%d')}</p>
            </div>
            
            <div class="section">
                <h3>Fuel Sales Summary</h3>
                <table>
                    <tr><th>Product</th><th>Gallons</th><th>Amount</th></tr>
                    <tr><td>Regular</td><td class="right">{fuel_data["REG"]["volume"]:,}</td><td class="right">${fuel_data["REG"]["amount"]:,.2f}</td></tr>
                    <tr><td>Plus</td><td class="right">{fuel_data["PLUS"]["volume"]:,}</td><td class="right">${fuel_data["PLUS"]["amount"]:,.2f}</td></tr>
                    <tr><td>Super</td><td class="right">{fuel_data["SUPER"]["volume"]:,}</td><td class="right">${fuel_data["SUPER"]["amount"]:,.2f}</td></tr>
                    <tr><td>Diesel</td><td class="right">{fuel_data["DIESEL"]["volume"]:,}</td><td class="right">${fuel_data["DIESEL"]["amount"]:,.2f}</td></tr>
                    <tr style="font-weight: bold;"><td>TOTAL</td><td class="right">{fuel_total_volume:,}</td><td class="right">${fuel_total_amount:,.2f}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h3>Store Sales Summary</h3>
                <table>
                    <tr><th>Category</th><th>Details</th><th>Amount</th></tr>
                    <tr><td>Cigarettes</td><td class="right">{cig_items} packets</td><td class="right">${cig_gross:,.2f}</td></tr>
                    <tr><td>E-Cigarettes</td><td class="right">{ecig_items} packets</td><td class="right">${ecig_gross:,.2f}</td></tr>
                    <tr><td>Other Sales</td><td class="right">-</td><td class="right">${other_sales:,.2f}</td></tr>
                    <tr style="font-weight: bold;"><td>TOTAL STORE SALES</td><td class="right">-</td><td class="right">${total_merch_sale:,.2f}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h3>Ending Inventory - {close_period_date.strftime('%m/%d/%Y')}</h3>
                <table>
                    <tr><th>Fuel Type</th><th>Gallons</th></tr>
                    <tr><td>Regular</td><td class="right">{inventory_regular:,}</td></tr>
                    <tr><td>Super</td><td class="right">{inventory_super:,}</td></tr>
                    <tr><td>Diesel</td><td class="right">{inventory_diesel:,}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h3>Summary</h3>
                <table>
                    <tr><td>Total Fuel Sales</td><td class="right">${fuel_total_amount:,.2f}</td></tr>
                    <tr><td>Total Merchandise Sales</td><td class="right">${total_merch_sale:,.2f}</td></tr>
                    <tr><td>Total Gallons Sold</td><td class="right">{fuel_total_volume:,}</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html_template

    # UPDATED BUTTONS SECTION
    st.markdown("---")
    st.subheader("📄 Generate Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Generate Main Report", use_container_width=True):
            # Calculate the CORRECT totals - FIXED TO EXCLUDE FUEL
            # Create a new merch_mask for df_final (which includes the summary row)
            df_final_fuel_mask = df_final["Description"].str.upper().apply(lambda x: any(k in str(x) for k in excluded_keywords) if pd.notna(x) else False)
            df_final_merch_mask = ~df_final_fuel_mask
            
            # Filter out the summary row and empty descriptions for clean calculations
            clean_mask = df_final_merch_mask & df_final["Description"].notna() & (df_final["Description"] != "Total Merch Sale")
            
            total_gross_merch_only = pd.to_numeric(df_final.loc[clean_mask, 'Gross'], errors='coerce').sum()
            total_net_sales_merch_only = pd.to_numeric(df_final.loc[clean_mask, 'Net Sales'], errors='coerce').sum()
            total_discounts_merch_only = pd.to_numeric(df_final.loc[clean_mask, 'Discounts'], errors='coerce').sum()
            total_refunds_merch_only = pd.to_numeric(df_final.loc[clean_mask, 'Refunds'], errors='coerce').sum()
            
            # Generate HTML content
            html_content = build_main_report(
                manual_mop_values, 
                total_mop_sales, 
                df_final, 
                merch_mask, 
                total_merch_sale,  # This is already merchandise only
                sales_tax, 
                tot_taxes, 
                incl_taxes, 
                total_gross_merch_only,  # NOW CONSISTENT - merchandise only
                total_discounts_merch_only,  # merchandise only
                total_refunds_merch_only,  # merchandise only
                0,
                pay_out  # Pass the pay_out value
            )
            
            # Convert HTML to PDF
            pdf_bytes = html_to_pdf(html_content)
            
            if pdf_bytes:
                st.success("✅ Main Report created successfully!")
                download_filename = f"Main_{store_name.replace(' ', '_').replace('-', '_')}_{open_period_date.strftime('%Y_%m_%d')}.pdf"
                st.download_button(
                    label="⬇️ Download Main Report",
                    data=pdf_bytes,
                    file_name=download_filename,
                    mime="application/pdf"
                )
            else:
                st.error("❌ Failed to generate PDF. Please check your data and try again.")

    with col2:
        if st.button("📋 Generate Accountant's Report", use_container_width=True):
            # Generate HTML content
            html_content = build_accountant_report()
            
            # Convert HTML to PDF
            pdf_bytes = html_to_pdf(html_content)
            
            if pdf_bytes:
                st.success("✅ Accountant's Report created successfully!")
                download_filename = f"Accountant_{store_name.replace(' ', '_').replace('-', '_')}_{open_period_date.strftime('%Y_%m_%d')}.pdf"
                st.download_button(
                    label="⬇️ Download Accountant's Report",
                    data=pdf_bytes,
                    file_name=download_filename,
                    mime="application/pdf"
                )
            else:
                st.error("❌ Failed to generate PDF. Please check your data and try again.")