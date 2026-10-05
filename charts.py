from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _empty_fig(title: str):
    fig = go.Figure()
    fig.update_layout(title=title, template="plotly_white")
    fig.add_annotation(
        text="No data available for the selected filters.",
        x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False
    )
    return fig


def create_inventory_chart(df: pd.DataFrame, group_col="locality"):
    if df.empty:
        return _empty_fig("Listings by Locality")
    summary = df.groupby(group_col, as_index=False).size().rename(columns={"size": "listings"})
    summary = summary.sort_values("listings", ascending=True)
    return px.bar(
        summary, x="listings", y=group_col, orientation="h",
        title="Listings by Locality",
        labels={"listings": "Number of Listings", group_col: "Locality"},
        text="listings"
    ).update_layout(template="plotly_white")


def create_property_type_chart(df: pd.DataFrame):
    if df.empty:
        return _empty_fig("Listings by Property Type")
    summary = df["property_type"].value_counts().reset_index()
    summary.columns = ["property_type", "listings"]
    return px.pie(
        summary, names="property_type", values="listings",
        hole=0.45, title="Listings by Property Type"
    ).update_layout(template="plotly_white")


def create_bedroom_chart(df: pd.DataFrame):
    if df.empty:
        return _empty_fig("Listings by Bedrooms")
    summary = df.groupby("bedrooms", as_index=False).size().rename(columns={"size": "listings"})
    return px.bar(
        summary, x="bedrooms", y="listings", text="listings",
        title="Listings by Bedroom Count",
        labels={"bedrooms": "Bedrooms", "listings": "Listings"}
    ).update_layout(template="plotly_white")


def create_dom_chart(df: pd.DataFrame):
    if df.empty:
        return _empty_fig("Average Days on Market by Locality")
    summary = (
        df.groupby("locality", as_index=False)["days_on_market"]
        .mean()
        .sort_values("days_on_market", ascending=True)
    )
    return px.bar(
        summary, x="days_on_market", y="locality", orientation="h",
        title="Average Days on Market by Locality",
        labels={"days_on_market": "Average Days", "locality": "Locality"},
        text=summary["days_on_market"].round(1)
    ).update_layout(template="plotly_white")


def create_dom_histogram(df: pd.DataFrame):
    if df.empty:
        return _empty_fig("Days on Market Distribution")
    return px.histogram(
        df, x="days_on_market", nbins=20,
        title="Days on Market Distribution",
        labels={"days_on_market": "Days on Market", "count": "Listings"}
    ).update_layout(template="plotly_white")


def create_price_area_scatter(df: pd.DataFrame):
    if df.empty:
        return _empty_fig("Property Price vs Area")
    return px.scatter(
        df, x="area_sqft", y="property_price", color="property_type",
        hover_data=["city", "locality", "bedrooms", "days_on_market", "price_per_sqft"],
        title="Property Price vs Area",
        labels={"area_sqft": "Area (sq.ft.)", "property_price": "Property Price (₹)"}
    ).update_layout(template="plotly_white")


def create_ppsf_locality_chart(df: pd.DataFrame):
    if df.empty:
        return _empty_fig("Price per Sq.Ft. by Locality")
    summary = (
        df.groupby("locality", as_index=False)["price_per_sqft"]
        .mean()
        .sort_values("price_per_sqft", ascending=True)
    )
    return px.bar(
        summary, x="price_per_sqft", y="locality", orientation="h",
        title="Average Price per Sq.Ft. by Locality",
        labels={"price_per_sqft": "₹ / sq.ft.", "locality": "Locality"},
        text=summary["price_per_sqft"].round(0)
    ).update_layout(template="plotly_white")


def create_ppsf_histogram(df: pd.DataFrame):
    if df.empty:
        return _empty_fig("Price per Sq.Ft. Distribution")
    return px.histogram(
        df, x="price_per_sqft", nbins=20,
        title="Price per Sq.Ft. Distribution",
        labels={"price_per_sqft": "₹ / sq.ft."}
    ).update_layout(template="plotly_white")


def create_price_dom_scatter(df: pd.DataFrame):
    if df.empty:
        return _empty_fig("Price vs Days on Market")
    return px.scatter(
        df, x="property_price", y="days_on_market", color="property_type",
        hover_data=["city", "locality", "bedrooms", "area_sqft", "price_per_sqft"],
        title="Property Price vs Days on Market",
        labels={"property_price": "Property Price (₹)", "days_on_market": "Days on Market"}
    ).update_layout(template="plotly_white")


def create_inventory_price_chart(df: pd.DataFrame):
    if df.empty:
        return _empty_fig("Inventory vs Average Price by Locality")
    summary = (
        df.groupby("locality", as_index=False)
        .agg(listings=("listing_id", "count"), average_price=("property_price", "mean"))
        .sort_values("listings", ascending=False)
    )
    fig = px.bar(
        summary, x="locality", y="listings",
        title="Inventory vs Average Price by Locality",
        labels={"listings": "Listings", "locality": "Locality"},
        hover_data={"average_price": ":,.0f"}
    )
    fig.add_trace(
        go.Scatter(
            x=summary["locality"], y=summary["average_price"],
            name="Average Price", mode="lines+markers",
            yaxis="y2"
        )
    )
    fig.update_layout(
        template="plotly_white",
        yaxis=dict(title="Listings"),
        yaxis2=dict(title="Average Price (₹)", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )
    return fig
