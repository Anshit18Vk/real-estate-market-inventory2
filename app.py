from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from src.data_cleaning import clean_and_normalize_data
from src.analytics import (
    calculate_metrics,
    get_inventory_summary,
    get_locality_summary,
    get_property_type_summary,
    get_time_on_market_summary,
    get_inventory_concentration,
    generate_insights,
)
from src.charts import (
    create_inventory_chart,
    create_property_type_chart,
    create_bedroom_chart,
    create_dom_chart,
    create_dom_histogram,
    create_price_area_scatter,
    create_ppsf_locality_chart,
    create_ppsf_histogram,
    create_price_dom_scatter,
    create_inventory_price_chart,
)
from src.maps import create_inventory_map, create_price_heatmap


st.set_page_config(
    page_title="Real Estate Market Inventory Map",
    page_icon="🏠",
    layout="wide",
)


DATA_PATH = Path(__file__).parent / "data" / "real_estate_listings.csv"


def load_data_from_source(uploaded_file=None):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Default dataset not found: {DATA_PATH}")
    return pd.read_csv(DATA_PATH)


def money(value):
    return f"₹{value:,.0f}"


def apply_filters(df: pd.DataFrame, selections: dict) -> pd.DataFrame:
    out = df.copy()

    if selections["city"] != "All":
        out = out[out["city"] == selections["city"]]
    if selections["locality"] != "All":
        out = out[out["locality"] == selections["locality"]]
    if selections["property_type"] != "All":
        out = out[out["property_type"] == selections["property_type"]]

    out = out[
        out["property_price"].between(selections["min_price"], selections["max_price"]) &
        out["area_sqft"].between(selections["min_area"], selections["max_area"]) &
        out["days_on_market"].between(selections["min_dom"], selections["max_dom"])
    ]

    if selections["bedrooms"] != "All":
        out = out[out["bedrooms"] == int(selections["bedrooms"])]

    return out


# Header
st.title("🏠 Real Estate Market Inventory Map")
st.caption(
    "GTU B.Tech IT Mini Project • Local housing inventory, time-on-market, "
    "price-per-square-foot and geographic analysis"
)

with st.sidebar:
    st.header("📂 Data Source")
    uploaded_file = st.file_uploader(
        "Upload your own CSV",
        type=["csv"],
        help="If no file is uploaded, the bundled sample dataset is used."
    )

try:
    raw_df = load_data_from_source(uploaded_file)
    cleaned_df, quality = clean_and_normalize_data(raw_df)
except Exception as exc:
    st.error(f"Could not load or clean the dataset: {exc}")
    st.info(
        "Required fields include city, locality, property type, bedrooms, "
        "area, price, days on market, latitude and longitude."
    )
    st.stop()

if cleaned_df.empty:
    st.error("The cleaned dataset contains no valid records.")
    st.stop()

with st.sidebar:
    st.header("🔎 Interactive Filters")

    cities = ["All"] + sorted(cleaned_df["city"].unique().tolist())
    selected_city = st.selectbox("City", cities)

    locality_pool = cleaned_df
    if selected_city != "All":
        locality_pool = locality_pool[locality_pool["city"] == selected_city]
    localities = ["All"] + sorted(locality_pool["locality"].unique().tolist())
    selected_locality = st.selectbox("Locality", localities)

    property_types = ["All"] + sorted(cleaned_df["property_type"].unique().tolist())
    selected_property_type = st.selectbox("Property Type", property_types)

    price_min = int(cleaned_df["property_price"].min())
    price_max = int(cleaned_df["property_price"].max())
    min_price, max_price = st.slider(
        "Price Range (₹)",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max),
        step=1000,
        format="₹%d",
    )

    area_min = int(cleaned_df["area_sqft"].min())
    area_max = int(cleaned_df["area_sqft"].max())
    min_area, max_area = st.slider(
        "Area Range (sq.ft.)",
        min_value=area_min,
        max_value=area_max,
        value=(area_min, area_max),
        step=10,
    )

    dom_min = int(cleaned_df["days_on_market"].min())
    dom_max = int(cleaned_df["days_on_market"].max())
    min_dom, max_dom = st.slider(
        "Time on Market (days)",
        min_value=dom_min,
        max_value=dom_max,
        value=(dom_min, dom_max),
    )

    bedroom_options = ["All"] + [str(x) for x in sorted(cleaned_df["bedrooms"].unique())]
    selected_bedrooms = st.selectbox("Number of Bedrooms", bedroom_options)

    map_metric = st.selectbox(
        "Map Display",
        ["Inventory", "Average Price", "Price per Sq.Ft.", "Average Days on Market"]
    )

selections = {
    "city": selected_city,
    "locality": selected_locality,
    "property_type": selected_property_type,
    "min_price": min_price,
    "max_price": max_price,
    "min_area": min_area,
    "max_area": max_area,
    "min_dom": min_dom,
    "max_dom": max_dom,
    "bedrooms": selected_bedrooms,
}
filtered_df = apply_filters(cleaned_df, selections)

if filtered_df.empty:
    st.warning("No listings match the selected filters. Relax one or more filters.")
    st.stop()

# KPI section
metrics = calculate_metrics(filtered_df)
st.subheader("📊 Market KPIs")
kpis = st.columns(6)
kpis[0].metric("Total Listings", f"{metrics['total_listings']:,}")
kpis[1].metric("Average Price", money(metrics["average_price"]))
kpis[2].metric("Avg. Price / Sq.Ft.", money(metrics["average_ppsf"]))
kpis[3].metric("Avg. Time on Market", f"{metrics['average_dom']:.1f} days")
kpis[4].metric("Median Price", money(metrics["median_price"]))
kpis[5].metric("Localities", f"{metrics['localities']:,}")

st.divider()

# Map
st.subheader("🗺️ Real Estate Inventory Map")
st.write(
    f"Map metric: **{map_metric}**. Individual listings remain clickable; "
    "heat-style views aggregate nearby coordinates."
)
inventory_map = create_inventory_map(filtered_df, map_metric)
st_folium(inventory_map, use_container_width=True, height=560)

st.divider()

# Inventory analysis
st.subheader("📦 Supply / Inventory Analysis")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(create_inventory_chart(filtered_df), use_container_width=True)
with c2:
    st.plotly_chart(create_property_type_chart(filtered_df), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(create_bedroom_chart(filtered_df), use_container_width=True)
with c4:
    concentration = get_inventory_concentration(filtered_df).head(10)
    st.markdown("**Inventory Concentration by Locality**")
    st.dataframe(
        concentration.style.format({"inventory_share_pct": "{:.1f}%"}),
        use_container_width=True,
        hide_index=True,
    )

# Time on market
st.subheader("⏱️ Time-on-Market Analysis")
dom_summary = get_time_on_market_summary(filtered_df)
d1, d2, d3, d4 = st.columns(4)
d1.metric("Average DOM", f"{dom_summary['average']:.1f}")
d2.metric("Median DOM", f"{dom_summary['median']:.1f}")
d3.metric("Minimum DOM", f"{dom_summary['minimum']}")
d4.metric("Maximum DOM", f"{dom_summary['maximum']}")

t1, t2 = st.columns(2)
with t1:
    st.plotly_chart(create_dom_histogram(filtered_df), use_container_width=True)
with t2:
    st.plotly_chart(create_dom_chart(filtered_df), use_container_width=True)

st.plotly_chart(create_price_dom_scatter(filtered_df), use_container_width=True)
st.info(
    "Interpretation: higher time-on-market can indicate slower-moving inventory, "
    "although DOM can also be affected by pricing, property condition, seasonality "
    "and local demand."
)

# Price per sqft
st.subheader("💰 Price per Square Foot Analysis")
p1, p2 = st.columns(2)
with p1:
    st.metric("Average Price / Sq.Ft.", money(metrics["average_ppsf"]))
with p2:
    st.metric("Median Price / Sq.Ft.", money(metrics["median_ppsf"]))

p3, p4 = st.columns(2)
with p3:
    st.plotly_chart(create_ppsf_locality_chart(filtered_df), use_container_width=True)
with p4:
    st.plotly_chart(create_ppsf_histogram(filtered_df), use_container_width=True)

st.plotly_chart(create_price_area_scatter(filtered_df), use_container_width=True)

st.subheader("📈 Inventory vs Average Price")
st.plotly_chart(create_inventory_price_chart(filtered_df), use_container_width=True)

# Geographic distribution
st.subheader("🌍 Geographic Price Distribution")
st.write("The heatmap uses geographic intensity to show where selected metrics are concentrated.")
heatmap = create_price_heatmap(filtered_df)
st_folium(heatmap, use_container_width=True, height=500)

# Automated insights
st.subheader("💡 Automated Market Insights")
for insight in generate_insights(filtered_df):
    st.success(insight)

# Locality summary
st.subheader("🏘️ Locality Analytics")
locality_summary = get_locality_summary(filtered_df)
display_summary = locality_summary.copy()
for col in ["average_price", "median_price", "average_price_per_sqft", "median_price_per_sqft"]:
    display_summary[col] = display_summary[col].round(0)
display_summary["average_days_on_market"] = display_summary["average_days_on_market"].round(1)
display_summary["median_days_on_market"] = display_summary["median_days_on_market"].round(1)
st.dataframe(display_summary, use_container_width=True, hide_index=True)

# Data quality
st.subheader("🧹 Data Cleaning & Normalization")
q1, q2, q3, q4 = st.columns(4)
q1.metric("Original Rows", quality["original_rows"])
q2.metric("Final Rows", quality["final_rows"])
q3.metric("Duplicates Removed", quality["duplicate_rows_removed"])
q4.metric("Invalid Records Removed", quality["invalid_records_removed"])

q5, q6, q7, q8 = st.columns(4)
q5.metric("Missing Values Handled", quality["missing_values_handled"])
q6.metric("Valid Coordinates", quality["valid_coordinates"])
q7.metric("Localities", quality["localities"])
q8.metric("Property Types", quality["property_types"])

st.markdown(
    """
**Normalization pipeline used in this project:**
1. Column names are converted to `snake_case`.
2. Common input column variations such as `price`, `sale_price`, `area`, `location`
   and `dom` are mapped to the project schema.
3. Duplicate rows and duplicate listing IDs are removed.
4. City, locality, property type and status text are standardized.
5. Currency, area, bedroom and DOM fields are converted to numeric values.
6. Missing optional values are handled; unusable required rows are removed.
7. Latitude/longitude are validated.
8. Impossible values such as non-positive price or area are removed.
9. `price_per_sqft = property_price / area_sqft` is calculated dynamically.
"""
)

with st.expander("Column mapping detected"):
    st.json(quality["column_mapping"])

with st.expander("Cleaned data preview"):
    st.dataframe(filtered_df.head(25), use_container_width=True, hide_index=True)

# Raw / filtered data + download
st.subheader("📥 Filtered Dataset")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Filtered Data as CSV",
    data=csv_bytes,
    file_name="filtered_real_estate_listings.csv",
    mime="text/csv",
)

st.caption(
    "GTU Mini Project: Real Estate Market Inventory Map | "
    "Python • Pandas • Plotly • Folium • Streamlit"
)
