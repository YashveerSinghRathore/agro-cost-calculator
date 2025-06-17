import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import base64
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# -----------------------------------------
# LOGIN SYSTEM & ROLE-BASED ACCESS
# -----------------------------------------
USERS = {
    "admin": {"password": "admin123", "role": "Yash"},
    "user": {"password": "user123", "role": "user"}
}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

def login():
    st.title("🌾 Agro Grain Export Calculator and Estimetor- Login Section")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.success(f"Logged in as {username} ({st.session_state.role})")
        else:
            st.error("Invalid credentials. Please try again.")
if not st.session_state.logged_in:
    login()
    st.stop()

# -----------------------------------------
# APP CONFIGURATION & STYLE
# -----------------------------------------
st.set_page_config(page_title="🌾 Agro Grain Export Calculator and Estimetorr", layout="wide")

def set_bg_base64(img_path):
    try:
        with open(img_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        background_css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(background_css, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading background image: {e}")
set_bg_base64("https://cbeditz.com/public/cbeditz/preview/agriculture-powerpoint-presentation-background-19-11614416076abiktlbxpz.jpg")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    /* Sidebar customization - force text white */
    [data-testid="stSidebar"] {
        background: #2c3e50;
    }
    [data-testid="stSidebar"] * {
        color: #ecf0f1 !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ecf0f1;
    }
    /* Force menu radio text white */
    [data-testid="stSidebar"] label {
         color: #ecf0f1 !important;
    }
    /* Header and card customization */
    .header-title {
        color: #ecf0f1;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: scale(1.02);
    }
    .metric-title {
        color: #34495e;
        font-size: 1.2rem;
        margin-bottom: 10px;
    }
    .metric-value {
        color: #27ae60;
        font-size: 1.8rem;
        font-weight: bold;
    }
    .custom-btn {
        background-color: #27ae60;
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    .custom-btn:hover {
        background-color: #1e8449;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# GLOBAL VARIABLES & SESSION STATE FOR APP DATA
# -----------------------------------------
if 'estimates' not in st.session_state:
    st.session_state.estimates = []
if 'show_download' not in st.session_state:
    st.session_state.show_download = False
if 'calculated_data' not in st.session_state:
    st.session_state.calculated_data = None
if 'products_list' not in st.session_state:
    st.session_state.products_list = {
        "Basmati Rice": {"Category": "Rice", "Unit": "MT"},
        "Finger Millet": {"Category": "Millets", "Unit": "MT"},
        "Red Lentils": {"Category": "Pulses", "Unit": "MT"},
        "Sunflower Oil": {"Category": "Oils", "Unit": "MT"},
        "Black Gram": {"Category": "Pulses", "Unit": "MT"}
    }
PRODUCTS = st.session_state.products_list
COUNTRIES = [
    "United States", "United Arab Emirates", "Saudi Arabia",
    "United Kingdom", "India", "China", "Japan"
]

# -----------------------------------------
# SIDEBAR: UPDATED MENU WITH ADDITIONAL FEATURES
# -----------------------------------------
st.sidebar.markdown("<h2 style='text-align: center;'>Menu</h2>", unsafe_allow_html=True)
nav_options = [
    "Dashboard", "Create Estimate", "Estimates History", "Forecasting", 
    "Product Management", "Current Freight Prices", "Business Intelligence", 
    "User Profile", "Settings"
]
nav_option = st.sidebar.radio("Navigate", nav_options, index=0)

# -----------------------------------------
# DASHBOARD SCREEN (Overview)
# -----------------------------------------
if nav_option == "Dashboard":
    st.markdown('<h1 class="header-title">🌾 Grain Export Calculator</h1>', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Export Pricing Dashboard</h4>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    def metric_card(title, value, icon=""):
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{icon} {title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)
    metric_card("Total Estimates", len(st.session_state.estimates), "📊")
    active = len([e for e in st.session_state.estimates if isinstance(e, dict) and e.get("status") == "active"])
    metric_card("Active Containers", active, "🚢")
    if st.session_state.estimates:
        valid_estimates = [e for e in st.session_state.estimates if isinstance(e, dict) and "results" in e and "margin" in e["results"]]
        avg_margin = sum(e["results"]["margin"] for e in valid_estimates) / len(valid_estimates) if valid_estimates else 0
    else:
        avg_margin = 0
    metric_card("Avg. Margin", f"{avg_margin:.1f}%", "💰")
    if st.session_state.estimates:
        total_value = sum(e["results"]["total_value"] for e in st.session_state.estimates if isinstance(e, dict) and "results" in e and "total_value" in e["results"])
    else:
        total_value = 0
    metric_card("Total Value", f"${total_value/1_000_000:.1f}M", "💲")

# -----------------------------------------
# CREATE ESTIMATE SCREEN
# -----------------------------------------
elif nav_option == "Create Estimate":
    st.header("Container Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        container_id = st.text_input("**Container ID**", f"CONT-{datetime.datetime.now().year}-{len(st.session_state.estimates)+1:03d}")
    with col2:
        destination_country = st.selectbox("**Destination Country**", COUNTRIES)
    with col3:
        estimate_date = st.date_input("**Estimate Date**", datetime.date.today())
    st.subheader("Product Selection")
    products_selected = {}
    for product, details in PRODUCTS.items():
        cols = st.columns([2, 2, 2, 2, 1])
        with cols[0]:
            st.write(f"**{product}**")
        with cols[1]:
            qty = st.number_input(f"Qty ({details['Unit']})", key=f"{product}_qty", min_value=0.0)
        with cols[2]:
            price = st.number_input("Unit Price ($/MT)", key=f"{product}_price", min_value=0.0)
        with cols[3]:
            total = qty * price
            st.write(f"**${total:,.2f}**")
        with cols[4]:
            include = st.checkbox("", key=f"{product}_include")
        if include:
            products_selected[product] = {"quantity": qty, "unit_price": price, "total_value": total}
    st.subheader("Costs")
    col1, col2, col3 = st.columns(3)
    with col1:
        transport_cost = st.number_input("Transport ($)", min_value=0.0)
        packing_cost = st.number_input("Packing ($)", min_value=0.0)
    with col2:
        fumigation_cost = st.number_input("Fumigation ($)", min_value=0.0)
        customs_cost = st.number_input("Customs ($)", min_value=0.0)
    with col3:
        export_duty = st.number_input("Export Duty (%)", min_value=0.0, max_value=100.0, value=5.0)
    st.subheader("Margin & Pricing")
    margin = st.number_input("Default Margin (%)", min_value=0.0, value=15.0)
    distributor_margin = st.number_input("Distributor Margin (%)", min_value=0.0, value=10.0)
    retailer_margin = st.number_input("Retailer Margin (%)", min_value=0.0, value=20.0)
    if st.button("Calculate Estimate", key="calc_estimate", help="Calculate the final pricing based on inputs"):
        total_product_value = sum(p["total_value"] for p in products_selected.values())
        export_cost = (transport_cost + packing_cost + fumigation_cost + customs_cost) + (total_product_value * export_duty / 100)
        fob_price = total_product_value + export_cost
        importer_price = fob_price * (1 + margin / 100)
        distributor_price = importer_price * (1 + distributor_margin / 100)
        retail_price = distributor_price * (1 + retailer_margin / 100)
        results = {
            "total_value": retail_price,
            "margin": ((retail_price - total_product_value) / total_product_value * 100) if total_product_value else 0,
            "fob_price": fob_price,
            "retail_price": retail_price
        }
        st.session_state.estimates.append({
            "container_id": container_id,
            "destination": destination_country,
            "date": estimate_date,
            "products": products_selected,
            "costs": {
                "transport": transport_cost,
                "packing": packing_cost,
                "fumigation": fumigation_cost,
                "customs": customs_cost,
                "duty": export_duty
            },
            "results": results,
            "status": "active"
        })
        st.success("Estimate calculated successfully!")
        st.metric("Retail Price", f"${retail_price:,.2f}")
        st.metric("Total Margin", f"{results['margin']:.2f}%")
        st.session_state.calculated_data = {
            "container_id": container_id,
            "results": results,
            "products": products_selected,
        }
        st.session_state.show_download = True

# -----------------------------------------
# ESTIMATES HISTORY SCREEN
# -----------------------------------------
elif nav_option == "Estimates History":
    st.header("Estimates History")
    if st.session_state.estimates:
        for est in st.session_state.estimates:
            if isinstance(est, dict):
                st.subheader(f"Container ID: {est['container_id']}")
                st.write(f"Destination: {est['destination']} | Date: {est['date']}")
                st.write("**Products:**")
                for prod, details in est["products"].items():
                    st.write(f"- {prod} : {details['quantity']} @ ${details['unit_price']}/MT = ${details['total_value']:,.2f}")
                st.write("**Results:**")
                st.write(est["results"])
                st.markdown("---")
    else:
        st.info("No estimates available yet.")

# -----------------------------------------
# FORECASTING SCREEN (Admin Only)
# -----------------------------------------
elif nav_option == "Forecasting" and st.session_state.role == "admin":
    st.header("Forecasting")
    st.markdown("Below is a simple forecasting model based on historical data.")
    if st.session_state.estimates:
        df_forecast = pd.DataFrame([est for est in st.session_state.estimates if isinstance(est, dict)])
        df_forecast['date'] = pd.to_datetime(df_forecast['date'], errors='coerce')
        retail_prices = df_forecast['results'].apply(lambda r: r["retail_price"] if isinstance(r, dict) else None)
        average_price = retail_prices.mean() if not retail_prices.empty else 0
        projected_price = average_price * 1.05  # Dummy projection with a 5% increase.
        st.metric("Average Retail Price", f"${average_price:,.2f}")
        st.metric("Forecasted Retail Price Next Quarter", f"${projected_price:,.2f}")
        forecast_df = pd.DataFrame({
            "Date": pd.to_datetime(df_forecast['date']),
            "Retail Price": retail_prices
        }).sort_values("Date")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df["Date"], y=forecast_df["Retail Price"],
                                  mode='lines+markers', name='Retail Price'))
        fig.update_layout(title="Historical Retail Prices",
                          xaxis_title="Date", yaxis_title="Retail Price",
                          template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for forecasting yet.")

# -----------------------------------------
# PRODUCT MANAGEMENT SCREEN
# -----------------------------------------
elif nav_option == "Product Management":
    st.header("Product Management")
    st.markdown("Manage your products below. You can update details or add a new product.")
    
    # Display current products using st.dataframe (non-editable)
    df_products = pd.DataFrame(st.session_state.products_list).transpose().reset_index()
    df_products.rename(columns={"index": "Product", "Category": "Category", "Unit": "Unit"}, inplace=True)
    st.dataframe(df_products)
    
    st.markdown("### Add a New Product")
    with st.form("new_product_form"):
        new_product_name = st.text_input("Product Name")
        new_category = st.text_input("Category")
        new_unit = st.text_input("Unit")
        submitted = st.form_submit_button("Add Product")
        if submitted and new_product_name and new_category and new_unit:
            st.session_state.products_list[new_product_name] = {"Category": new_category, "Unit": new_unit}
            st.success(f"Product '{new_product_name}' added successfully!")
            st.experimental_rerun()

# -----------------------------------------
# CURRENT FREIGHT PRICES SCREEN
# -----------------------------------------
elif nav_option == "Current Freight Prices":
    st.header("Current Freight Prices")
    st.markdown("Below are the current freight prices (dummy data).")
    df_freight = pd.DataFrame({
        "Route": ["India-US", "India-UK", "India-Emirates", "India-Saudi Arabia", "India-China"],
        "Freight Cost ($/MT)": [120, 150, 100, 90, 130],
        "Last Updated": [datetime.date.today() for _ in range(5)]
    })
    st.table(df_freight)
    st.markdown("*(Dynamic freight pricing integration coming soon...)*")

# -----------------------------------------
# BUSINESS INTELLIGENCE SCREEN
# -----------------------------------------
elif nav_option == "Business Intelligence":
    st.header("Business Intelligence")
    st.markdown("Explore advanced analytics and dashboards here.")
    # Revenue Trend Chart
    if st.session_state.estimates:
        df = pd.DataFrame([est for est in st.session_state.estimates if isinstance(est, dict)])
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.sort_values("date", inplace=True)
        fig_trend = px.line(df, x="date", y=df["results"].apply(lambda r: r["retail_price"] if isinstance(r, dict) else 0),
                            labels={"x": "Date", "y": "Retail Price"},
                            title="Revenue Trend Over Time")
        st.plotly_chart(fig_trend, use_container_width=True)
        # Product Performance Analysis: Total revenue per product
        product_revenues = {}
        for est in st.session_state.estimates:
            if isinstance(est, dict):
                for prod, details in est["products"].items():
                    revenue = details.get("total_value", 0)
                    product_revenues[prod] = product_revenues.get(prod, 0) + revenue
        if product_revenues:
            df_products_revenue = pd.DataFrame(list(product_revenues.items()), columns=["Product", "Total Revenue"])
            fig_bar = px.bar(df_products_revenue, x="Product", y="Total Revenue",
                             title="Total Revenue by Product", labels={"Total Revenue": "Revenue ($)"})
            st.plotly_chart(fig_bar, use_container_width=True)
        # Margin Distribution Example (Pie chart)
        margins = {}
        for est in st.session_state.estimates:
            if isinstance(est, dict):
                for prod, details in est["products"].items():
                    margin_contrib = est["results"].get("margin", 0)
                    margins[prod] = margins.get(prod, 0) + margin_contrib
        if margins:
            df_margin = pd.DataFrame(list(margins.items()), columns=["Product", "Margin Contribution"])
            fig_pie = px.pie(df_margin, names="Product", values="Margin Contribution",
                             title="Margin Distribution by Product")
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data available for business intelligence analytics yet.")

# -----------------------------------------
# USER PROFILE SCREEN
# -----------------------------------------
elif nav_option == "User Profile":
    st.header("User Profile")
    st.markdown(f"**Username:** {st.session_state.username}")
    st.markdown(f"**Role:** {st.session_state.role}")
    st.markdown("Customize your profile settings here. (Feature coming soon...)")

# -----------------------------------------
# SETTINGS SCREEN
# -----------------------------------------
elif nav_option == "Settings":
    st.header("Settings")
    st.markdown("Customize app preferences, including UI themes and notifications here. (Feature coming soon...)")

# -----------------------------------------
# PDF DOWNLOAD SECTION (Common for all Screens)
# -----------------------------------------
if st.session_state.show_download and st.session_state.calculated_data:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"Export Estimate Report - {st.session_state.calculated_data['container_id']}", styles['Title']),
        Spacer(1, 12),
        Paragraph(f"Prepared by: {st.session_state.username}", styles['Normal']),
        Spacer(1, 12)
    ]
    table_data = [["Product", "Qty", "Unit Price", "Total Value"]]
    for k, v in st.session_state.calculated_data["products"].items():
        table_data.append([k, v["quantity"], f"${v['unit_price']:,.2f}", f"${v['total_value']:,.2f}"])
    table_data.append(["", "", "Retail Price", f"${st.session_state.calculated_data['results']['retail_price']:,.2f}"])
    from reportlab.platypus import Table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    st.download_button(
        "📥 Download PDF Report",
        data=buffer,
        file_name=f"{st.session_state.calculated_data['container_id']}_report.pdf",
        mime="application/pdf"
    )
