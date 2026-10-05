from __future__ import annotations

import re
from typing import Dict, Tuple

import numpy as np
import pandas as pd


COLUMN_ALIASES = {
    "listing_id": ["listing_id", "id", "property_id", "propertyid", "listingid"],
    "city": ["city", "town"],
    "locality": ["locality", "location", "area_name", "neighborhood", "neighbourhood"],
    "property_type": ["property_type", "propertytype", "type", "property_category"],
    "bedrooms": ["bedrooms", "bhk", "beds", "bedroom_count"],
    "bathrooms": ["bathrooms", "bathroom", "baths", "bath_count"],
    "area_sqft": ["area_sqft", "area", "square_feet", "sqft", "built_up_area", "builtup_area"],
    "property_price": ["property_price", "price", "sale_price", "listing_price", "amount"],
    "days_on_market": ["days_on_market", "dom", "days", "days_listed", "time_on_market"],
    "latitude": ["latitude", "lat"],
    "longitude": ["longitude", "lng", "lon", "long"],
    "listing_date": ["listing_date", "date", "listed_date", "posted_date"],
    "status": ["status", "listing_status", "availability"],
}

REQUIRED_COLUMNS = [
    "listing_id", "city", "locality", "property_type", "bedrooms",
    "area_sqft", "property_price", "days_on_market", "latitude", "longitude"
]


def normalize_column_name(name: str) -> str:
    """Convert a column name to snake_case."""
    name = str(name).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def _clean_text(value) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def _clean_numeric_series(series: pd.Series) -> pd.Series:
    """Convert common currency/number formats such as ₹85,00,000 or 1200 sq ft."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(r"[^\d.\-]", "", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def map_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Map reasonable input column variations to the canonical schema."""
    out = df.copy()
    out.columns = [normalize_column_name(c) for c in out.columns]

    mapping = {}
    existing = set(out.columns)

    for canonical, aliases in COLUMN_ALIASES.items():
        if canonical in existing:
            mapping[canonical] = canonical
            continue
        for alias in aliases:
            alias = normalize_column_name(alias)
            if alias in existing:
                out = out.rename(columns={alias: canonical})
                mapping[canonical] = alias
                break

    return out, mapping


def clean_and_normalize_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Clean, standardize and validate real-estate listing data.

    Returns:
        cleaned_dataframe, quality_report
    """
    if df is None or df.empty:
        raise ValueError("The dataset is empty.")

    original_rows = len(df)
    work, column_mapping = map_columns(df)

    missing_required = [c for c in REQUIRED_COLUMNS if c not in work.columns]
    if missing_required:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_required) +
            ". Please provide city, locality, property type, bedrooms, "
            "area, price, days on market and valid latitude/longitude."
        )

    # Add optional columns when absent.
    if "bathrooms" not in work.columns:
        work["bathrooms"] = np.nan
    if "listing_date" not in work.columns:
        work["listing_date"] = pd.NaT
    if "status" not in work.columns:
        work["status"] = "Active"

    duplicate_before = len(work)
    work = work.drop_duplicates()
    duplicate_rows = duplicate_before - len(work)

    if work["listing_id"].duplicated().any():
        before_id = len(work)
        work = work.drop_duplicates(subset=["listing_id"], keep="first")
        duplicate_rows += before_id - len(work)

    # Standardize text.
    for col in ["listing_id", "city", "locality", "property_type", "status"]:
        work[col] = work[col].map(_clean_text)

    work["city"] = work["city"].str.title()
    work["locality"] = work["locality"].str.replace(r"\s+", " ", regex=True).str.title()
    work["property_type"] = (
        work["property_type"].str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .replace({
            "flat": "Apartment",
            "flats": "Apartment",
            "apartment": "Apartment",
            "apartments": "Apartment",
            "villa": "Villa",
            "bungalow": "Villa",
            "independent house": "Independent House",
            "independenthouse": "Independent House",
            "house": "Independent House",
            "row house": "Row House",
            "rowhouse": "Row House",
            "penthouse": "Penthouse",
        })
        .str.title()
    )
    work["status"] = work["status"].replace("", "Active").str.title()

    # Numeric conversions.
    numeric_cols = [
        "bedrooms", "bathrooms", "area_sqft", "property_price",
        "days_on_market", "latitude", "longitude"
    ]
    invalid_numeric_before = work[numeric_cols].isna().sum().sum()

    for col in numeric_cols:
        work[col] = _clean_numeric_series(work[col])

    # Parse dates if supplied.
    work["listing_date"] = pd.to_datetime(work["listing_date"], errors="coerce")

    # Fill non-critical missing text/optional values.
    missing_handled = int(work.isna().sum().sum())
    work["bathrooms"] = work["bathrooms"].fillna(work["bedrooms"] + 1)
    work["status"] = work["status"].fillna("Active")

    # Required numeric/text rows cannot be reliably analyzed.
    required_valid = (
        work["listing_id"].ne("") &
        work["city"].ne("") &
        work["locality"].ne("") &
        work["property_type"].ne("") &
        work["bedrooms"].notna() &
        work["area_sqft"].notna() &
        work["property_price"].notna() &
        work["days_on_market"].notna() &
        work["latitude"].notna() &
        work["longitude"].notna()
    )

    invalid_value_mask = (
        (work["bedrooms"] < 0) |
        (work["area_sqft"] <= 0) |
        (work["property_price"] <= 0) |
        (work["days_on_market"] < 0) |
        (work["latitude"] < -90) | (work["latitude"] > 90) |
        (work["longitude"] < -180) | (work["longitude"] > 180)
    )

    invalid_records = int((~required_valid | invalid_value_mask).sum())
    work = work.loc[required_valid & ~invalid_value_mask].copy()

    # Derived metric.
    work["price_per_sqft"] = work["property_price"] / work["area_sqft"]
    invalid_ppsf = work["price_per_sqft"] <= 0
    invalid_records += int(invalid_ppsf.sum())
    work = work.loc[~invalid_ppsf].copy()

    work["bedrooms"] = work["bedrooms"].round().astype(int)
    work["bathrooms"] = work["bathrooms"].round(1)
    work["area_sqft"] = work["area_sqft"].round(2)
    work["property_price"] = work["property_price"].round(2)
    work["days_on_market"] = work["days_on_market"].round().astype(int)
    work["price_per_sqft"] = work["price_per_sqft"].round(2)

    work = work.sort_values(["city", "locality", "property_price"]).reset_index(drop=True)

    quality = {
        "original_rows": original_rows,
        "duplicate_rows_removed": duplicate_rows,
        "missing_values_handled": int(missing_handled),
        "invalid_numeric_values_detected": int(invalid_numeric_before),
        "invalid_records_removed": invalid_records,
        "final_rows": len(work),
        "valid_coordinates": int(len(work)),
        "localities": int(work["locality"].nunique()),
        "property_types": int(work["property_type"].nunique()),
        "cities": int(work["city"].nunique()),
        "column_mapping": column_mapping,
    }
    return work, quality


def validate_data(df: pd.DataFrame) -> Dict:
    """Return validation details without modifying the dataframe."""
    checks = {}
    for col in REQUIRED_COLUMNS:
        checks[col] = col in df.columns

    if all(checks.values()) and not df.empty:
        checks["non_empty"] = True
        checks["coordinates_valid"] = bool(
            df["latitude"].between(-90, 90).all() and
            df["longitude"].between(-180, 180).all()
        )
        checks["positive_price"] = bool((df["property_price"] > 0).all())
        checks["positive_area"] = bool((df["area_sqft"] > 0).all())
    else:
        checks["non_empty"] = not df.empty
        checks["coordinates_valid"] = False
        checks["positive_price"] = False
        checks["positive_area"] = False
    return checks


def load_data(path: str | None = None) -> pd.DataFrame:
    """Load a CSV file and normalize it."""
    if not path:
        path = "data/real_estate_listings.csv"
    raw = pd.read_csv(path)
    cleaned, _ = clean_and_normalize_data(raw)
    return cleaned
