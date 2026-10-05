from __future__ import annotations

import pandas as pd


def calculate_price_per_sqft(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["price_per_sqft"] = out["property_price"] / out["area_sqft"]
    return out


def calculate_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_listings": 0,
            "average_price": 0,
            "median_price": 0,
            "average_area": 0,
            "average_dom": 0,
            "median_dom": 0,
            "average_ppsf": 0,
            "median_ppsf": 0,
            "localities": 0,
        }

    return {
        "total_listings": int(len(df)),
        "average_price": float(df["property_price"].mean()),
        "median_price": float(df["property_price"].median()),
        "average_area": float(df["area_sqft"].mean()),
        "average_dom": float(df["days_on_market"].mean()),
        "median_dom": float(df["days_on_market"].median()),
        "average_ppsf": float(df["price_per_sqft"].mean()),
        "median_ppsf": float(df["price_per_sqft"].median()),
        "localities": int(df["locality"].nunique()),
    }


def get_inventory_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("locality", as_index=False)
        .agg(listing_count=("listing_id", "count"))
        .sort_values("listing_count", ascending=False)
    )


def get_locality_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["city", "locality"], as_index=False)
        .agg(
            listing_count=("listing_id", "count"),
            average_price=("property_price", "mean"),
            median_price=("property_price", "median"),
            average_days_on_market=("days_on_market", "mean"),
            median_days_on_market=("days_on_market", "median"),
            average_price_per_sqft=("price_per_sqft", "mean"),
            median_price_per_sqft=("price_per_sqft", "median"),
            average_area=("area_sqft", "mean"),
        )
        .sort_values("listing_count", ascending=False)
    )


def get_property_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("property_type", as_index=False)
        .agg(
            listing_count=("listing_id", "count"),
            average_price=("property_price", "mean"),
            average_days_on_market=("days_on_market", "mean"),
            average_price_per_sqft=("price_per_sqft", "mean"),
        )
        .sort_values("listing_count", ascending=False)
    )


def get_bedroom_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("bedrooms", as_index=False)
        .agg(
            listing_count=("listing_id", "count"),
            average_price=("property_price", "mean"),
            average_days_on_market=("days_on_market", "mean"),
        )
        .sort_values("bedrooms")
    )


def get_time_on_market_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"average": 0, "median": 0, "minimum": 0, "maximum": 0}
    return {
        "average": float(df["days_on_market"].mean()),
        "median": float(df["days_on_market"].median()),
        "minimum": int(df["days_on_market"].min()),
        "maximum": int(df["days_on_market"].max()),
    }


def get_top_localities(df: pd.DataFrame) -> dict:
    summary = get_locality_summary(df)
    return {
        "inventory": summary.nlargest(5, "listing_count")[["locality", "listing_count"]],
        "ppsf": summary.nlargest(5, "average_price_per_sqft")[["locality", "average_price_per_sqft"]],
        "dom": summary.nlargest(5, "average_days_on_market")[["locality", "average_days_on_market"]],
    }


def get_inventory_concentration(df: pd.DataFrame) -> pd.DataFrame:
    summary = get_inventory_summary(df).copy()
    total = summary["listing_count"].sum()
    summary["inventory_share_pct"] = (
        summary["listing_count"] / total * 100 if total else 0
    )
    return summary


def generate_insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["No data is available for the selected filters."]

    locality = get_locality_summary(df)
    property_types = get_property_type_summary(df)
    bedroom = get_bedroom_summary(df)

    insights = []

    top_inventory = locality.loc[locality["listing_count"].idxmax()]
    insights.append(
        f"{top_inventory['locality']} has the highest listing inventory "
        f"with {int(top_inventory['listing_count'])} listings."
    )

    top_ppsf = locality.loc[locality["average_price_per_sqft"].idxmax()]
    insights.append(
        f"{top_ppsf['locality']} has the highest average price per square foot "
        f"at ₹{top_ppsf['average_price_per_sqft']:,.0f}/sq.ft."
    )

    top_dom = locality.loc[locality["average_days_on_market"].idxmax()]
    insights.append(
        f"{top_dom['locality']} has the highest average time on market "
        f"at {top_dom['average_days_on_market']:.1f} days."
    )

    top_bedroom = bedroom.loc[bedroom["listing_count"].idxmax()]
    insights.append(
        f"{int(top_bedroom['bedrooms'])} BHK properties represent the largest "
        f"share of listings with {int(top_bedroom['listing_count'])} properties."
    )

    insights.append(
        f"The filtered market has an average price of ₹{df['property_price'].mean():,.0f} "
        f"and an average of {df['days_on_market'].mean():.1f} days on market."
    )
    return insights
