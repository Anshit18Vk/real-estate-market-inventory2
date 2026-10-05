from __future__ import annotations

import folium
import numpy as np
from folium.plugins import HeatMap, MarkerCluster


PROPERTY_COLORS = {
    "Apartment": "blue",
    "Villa": "green",
    "Independent House": "red",
    "Row House": "purple",
    "Penthouse": "orange",
}


def _center(df):
    return [float(df["latitude"].mean()), float(df["longitude"].mean())]


def _popup_html(row) -> str:
    price = f"₹{row['property_price']:,.0f}"
    ppsf = f"₹{row['price_per_sqft']:,.0f}"
    return f"""
    <div style="font-family:Arial; min-width:220px;">
        <h4 style="margin-bottom:8px;">🏠 {row['listing_id']}</h4>
        <b>City:</b> {row['city']}<br>
        <b>Locality:</b> {row['locality']}<br>
        <b>Property:</b> {row['property_type']}<br>
        <b>Bedrooms:</b> {int(row['bedrooms'])} BHK<br>
        <b>Area:</b> {row['area_sqft']:,.0f} sq.ft.<br>
        <b>Price:</b> {price}<br>
        <b>Price/Sq.Ft.:</b> {ppsf}<br>
        <b>Days on Market:</b> {int(row['days_on_market'])}
    </div>
    """


def create_inventory_map(df, map_metric="Inventory"):
    """Create the main interactive Folium map."""
    if df.empty:
        return folium.Map(location=[22.30, 73.18], zoom_start=11)

    fmap = folium.Map(
        location=_center(df),
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    if map_metric == "Inventory":
        cluster = MarkerCluster(name="Individual Listings").add_to(fmap)
        for _, row in df.iterrows():
            color = PROPERTY_COLORS.get(row["property_type"], "cadetblue")
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=folium.Popup(_popup_html(row), max_width=320),
                tooltip=f"{row['locality']} | ₹{row['property_price']:,.0f}",
                icon=folium.Icon(color=color, icon="home", prefix="fa"),
            ).add_to(cluster)

    else:
        # Aggregate by rounded geographic cells to avoid claiming false precision.
        work = df.copy()
        work["lat_cell"] = work["latitude"].round(3)
        work["lon_cell"] = work["longitude"].round(3)

        metric_map = {
            "Average Price": "property_price",
            "Price per Sq.Ft.": "price_per_sqft",
            "Average Days on Market": "days_on_market",
        }
        metric_col = metric_map.get(map_metric, "price_per_sqft")
        agg = (
            work.groupby(["lat_cell", "lon_cell"], as_index=False)[metric_col]
            .mean()
        )

        points = agg[["lat_cell", "lon_cell", metric_col]].dropna().values.tolist()
        if points:
            HeatMap(
                points,
                radius=28,
                blur=22,
                min_opacity=0.35,
                name=map_metric,
            ).add_to(fmap)

        # Keep clickable listing points available for all metric modes.
        cluster = MarkerCluster(name="Listings").add_to(fmap)
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=4,
                color=PROPERTY_COLORS.get(row["property_type"], "cadetblue"),
                fill=True,
                fill_opacity=0.75,
                popup=folium.Popup(_popup_html(row), max_width=320),
                tooltip=f"{row['locality']} | {map_metric}",
            ).add_to(cluster)

    # Simple property-type legend.
    legend_items = "".join(
        f'<div><span style="display:inline-block;width:12px;height:12px;'
        f'background:{color};margin-right:6px;"></span>{ptype}</div>'
        for ptype, color in PROPERTY_COLORS.items()
    )
    legend = f"""
    <div style="position: fixed; bottom: 30px; left: 30px; z-index:9999;
                background:white; border:2px solid #777; border-radius:6px;
                padding:10px; font-size:12px;">
        <b>Property Type</b>
        {legend_items}
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(legend))
    folium.LayerControl().add_to(fmap)
    return fmap


def create_price_heatmap(df):
    """Dedicated price-per-square-foot geographic heatmap."""
    if df.empty:
        return folium.Map(location=[22.30, 73.18], zoom_start=11)
    fmap = folium.Map(location=_center(df), zoom_start=11, tiles="OpenStreetMap")
    points = df[["latitude", "longitude", "price_per_sqft"]].dropna().values.tolist()
    HeatMap(
        points,
        radius=25,
        blur=20,
        min_opacity=0.35,
        name="Price per Sq.Ft.",
    ).add_to(fmap)
    folium.LayerControl().add_to(fmap)
    return fmap
