import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Set page layout to wide
st.set_page_config(
    page_title="Agriculture Data Dashboard",
    page_icon="🌾",
    layout="wide"
)

# 1. Load Dataset Safely
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "agriculture_dataset.csv")

@st.cache_data
def load_data(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

data = load_data(csv_path)

if data is None:
    st.error(f"❌ Could not find `agriculture_dataset.csv` in `{base_dir}`.")
    st.info("Please make sure your CSV file is placed in the exact same folder as `app.py`.")
    st.stop()

# 2. Header
st.markdown(
    """
    <h1 style='text-align:center; color:white; background:#1976D2; padding:15px; border-radius:12px;'>
        🌾 Agriculture Data Dashboard
    </h1>
    """, 
    unsafe_allow_html=True
)
st.write("")

# 3. Sidebar Filters
st.sidebar.header("Filter Options")

# Convert numpy arrays to standard python lists
seasons_list = list(data["Season"].unique())
crops_list = list(data["Crop_Type"].unique())

selected_season = st.sidebar.multiselect(
    "Select Season:",
    options=seasons_list,
    default=seasons_list
)

selected_crop = st.sidebar.multiselect(
    "Select Crop Type:",
    options=crops_list,
    default=crops_list
)

# Handle empty selection safety
if not selected_season or not selected_crop:
    st.warning("⚠️ Please select at least one Season and one Crop Type from the sidebar.")
    st.stop()

# Filter dataframe based on selections
filtered_data = data[
    (data["Season"].isin(selected_season)) & 
    (data["Crop_Type"].isin(selected_crop))
]

if filtered_data.empty:
    st.warning("⚠️ No data available matching the selected filter criteria.")
    st.stop()

# Quick Summary Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Farms", len(filtered_data))
col2.metric("Total Yield (Tons)", f"{filtered_data['Yield(tons)'].sum():,.2f}")

avg_area = filtered_data['Farm_Area(acres)'].mean()
col3.metric("Avg Farm Area (Acres)", f"{avg_area:,.2f}" if pd.notnull(avg_area) else "0.00")

col4.metric("Total Water Usage (m³)", f"{filtered_data['Water_Usage(cubic meters)'].sum():,.2f}")

st.divider()

# 4. Generate Figures

# Figure 1: Crop Distribution per Season
top = filtered_data.groupby("Season")["Crop_Type"].value_counts().reset_index(name='Count')
fig1 = px.bar(
    top, x="Season", y="Count", color="Crop_Type", text="Count", 
    title="Distribution of Crop Types per Season", template="plotly_dark"
)

# Figure 2: Yield vs Farm Area
fig2 = px.scatter(
    filtered_data, x="Farm_Area(acres)", y="Yield(tons)", 
    color="Crop_Type", size="Fertilizer_Used(tons)", 
    hover_data=["Irrigation_Type", "Soil_Type"], 
    title="Yield vs. Farm Area (Bubble = Fertilizer Used)", template="plotly_dark"
)

# Figure 3: Farm Area Distribution Pie
fig3 = px.pie(
    filtered_data, values="Farm_Area(acres)", names="Soil_Type", 
    color="Soil_Type", title="Farm Area Distribution by Soil Type", hole=0.6,
    template="plotly_dark"
)

# Figure 4: Fertilizer per Irrigation Method
daily = filtered_data.groupby("Irrigation_Type")["Fertilizer_Used(tons)"].sum().reset_index()
fig4 = px.line(
    daily, x="Irrigation_Type", y="Fertilizer_Used(tons)", 
    markers=True, title="Fertilizer Usage per Irrigation Method", template="plotly_dark"
)

# Figure 5: Farm Area Histogram
fig5 = px.histogram(
    filtered_data, x="Farm_Area(acres)", color="Crop_Type", 
    nbins=40, title="Farm Area Distribution", template="plotly_dark"
)

# Figure 6: Yield Box Plot
fig6 = px.box(
    filtered_data, y="Yield(tons)", title="Yield Distribution Box Plot", template="plotly_dark"
)

# 5. Display Dashboard Charts in Streamlit Columns
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.plotly_chart(fig1, use_container_width=True)
with row1_col2:
    st.plotly_chart(fig2, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.plotly_chart(fig3, use_container_width=True)
with row2_col2:
    st.plotly_chart(fig4, use_container_width=True)

row3_col1, row3_col2 = st.columns(2)
with row3_col1:
    st.plotly_chart(fig5, use_container_width=True)
with row3_col2:
    st.plotly_chart(fig6, use_container_width=True)

# 6. Raw Data Table Preview
with st.expander("🔍 View Raw Dataset"):
    st.dataframe(filtered_data)

# Footer
st.markdown(
    """
    <hr>
    <h3 style='text-align:center; background:#a8329b; color:#8feb34; padding:15px; border-radius:20px;'>
        Dashboard Created using Pandas + Plotly + Streamlit
    </h3>
    """, 
    unsafe_allow_html=True
)