# Real Estate Market Inventory Map

## Project Description

**Real Estate Market Inventory Map** is a B.Tech IT mini-project that normalizes local housing listings and analyzes real estate supply, average time-on-market, and price-per-square-foot geographic distributions.

The project is designed as a practical data analytics dashboard using Python, Pandas, Plotly, Folium and Streamlit. It can run completely locally without paid APIs.

## Problem Statement

Real-estate listing data is often inconsistent, distributed across locations, and difficult to compare directly. A simple dashboard can transform raw housing listings into useful market indicators such as inventory concentration, average property price, price per square foot and time on market.

## Objectives

- Clean and normalize housing listing data.
- Remove duplicates and invalid records.
- Standardize city, locality and property type values.
- Calculate price per square foot.
- Analyze inventory by locality, property type and bedrooms.
- Analyze time on market.
- Visualize geographic distributions using Folium.
- Provide interactive filtering.
- Generate simple, data-driven market insights.

## Features

- Six KPI cards.
- Interactive sidebar filters.
- Upload your own CSV.
- Automatic fallback to bundled sample data.
- Column alias mapping for common CSV naming variations.
- Interactive inventory map.
- Property-type marker styling.
- Heatmap modes for price, price/sq.ft. and DOM.
- Ten interactive Plotly charts.
- Locality-level analytics.
- Automated insights.
- Data-quality and normalization report.
- Filtered CSV download.

## Technology Used

| Technology | Purpose |
|---|---|
| Python 3 | Core programming |
| Streamlit | Web dashboard |
| Pandas | Data cleaning and analysis |
| NumPy | Numerical operations |
| Plotly | Interactive charts |
| Folium | Geographic maps |
| streamlit-folium | Folium inside Streamlit |
| Scikit-learn | Included for future student analytics extensions |
| OpenStreetMap | Free map tiles |

No paid API key is required.

## System Requirements

- Windows, Linux or macOS
- Python 3.10 or newer recommended
- VS Code
- Internet connection is useful for OpenStreetMap map tiles, but no paid service is required.
- At least 4 GB RAM recommended.

## Project Structure

```text
real_estate_market_inventory/
│
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── real_estate_listings.csv
│
├── src/
│   ├── __init__.py
│   ├── data_cleaning.py
│   ├── analytics.py
│   ├── maps.py
│   └── charts.py
│
└── assets/
    └── project_info.txt
```

## Dataset Description

The bundled sample contains Indian real-estate listings from:

- Ahmedabad
- Vadodara
- Surat

Important fields:

- `listing_id`
- `city`
- `locality`
- `property_type`
- `bedrooms`
- `bathrooms`
- `area_sqft`
- `property_price`
- `days_on_market`
- `latitude`
- `longitude`
- `listing_date`
- `status`

`price_per_sqft` is intentionally calculated by the application rather than stored as a primary input field.

## Data Cleaning Process

The application:

1. Converts column names to snake_case.
2. Maps common aliases such as `price`, `sale_price`, `area`, `location`, `dom`, etc.
3. Removes duplicate rows.
4. Removes duplicate listing IDs.
5. Standardizes city and locality names.
6. Standardizes property type labels.
7. Converts price, area, DOM and bedroom fields to numeric.
8. Parses listing dates.
9. Handles optional missing values.
10. Validates latitude and longitude.
11. Removes invalid price/area/DOM/coordinate values.
12. Calculates `price_per_sqft`.

## Methodology

```text
CSV / User Upload
       ↓
Column Normalization
       ↓
Duplicate Removal
       ↓
Missing / Invalid Value Handling
       ↓
Geographic Validation
       ↓
Price per Sq.Ft. Calculation
       ↓
Filtering
       ↓
EDA + Statistical Summaries
       ↓
Plotly Charts + Folium Maps
       ↓
Automated Market Insights
```

## Algorithms / Calculations

### Price per Square Foot

```text
price_per_sqft = property_price / area_sqft
```

### Inventory

```text
inventory(locality) = count(listing_id)
```

### Average Time on Market

```text
average_dom = sum(days_on_market) / number_of_listings
```

### Inventory Concentration

```text
inventory_share(%) =
    locality_listings / total_listings × 100
```

## Installation

Open the project folder in VS Code.

### 1. Create a virtual environment (recommended)

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

The browser should open the Streamlit dashboard automatically. If it does not, open the local URL shown in the terminal.

## How to Use

1. Start the application.
2. The sample dataset loads automatically.
3. Use the sidebar filters.
4. Change the map metric.
5. Explore inventory charts.
6. Explore DOM and price/sq.ft. charts.
7. Read the automated insights.
8. Open the Data Cleaning & Normalization section.
9. Download the filtered dataset if required.
10. Upload another compatible CSV to test the pipeline.

## Screenshots

Add your own screenshots after running the project:

```text
screenshots/
├── dashboard.png
├── inventory_map.png
├── analytics.png
└── data_cleaning.png
```

## Expected Output

The dashboard should show:

- KPI cards for total listings, average price, average price/sq.ft., average DOM, median price and locality count.
- A Folium geographic map.
- Inventory charts.
- Time-on-market charts.
- Price-per-square-foot charts.
- Geographic heatmap.
- Automated market observations.
- Data-quality statistics.
- Filtered data table and download button.

## Advantages

- Completely local and free.
- Easy to demonstrate during a GTU viva.
- Uses real data-analytics workflow.
- Modular source code.
- Supports custom CSV uploads.
- Interactive geographic visualization.
- Does not require a paid API.

## Limitations

- The bundled dataset is a student demonstration dataset, not a live property feed.
- Map tiles require network access to load normally.
- Market insights are descriptive and do not represent professional investment advice.
- No live property listing API is used.

## Future Scope

- Connect to a permitted live listing data source.
- Add time-series price trends.
- Add district boundaries.
- Add predictive price modeling.
- Add clustering of localities.
- Add user authentication.
- Add database storage.
- Add advanced geospatial layers.

## GTU Viva Questions

### 1. What is the objective of this project?
To clean real-estate listing data and analyze housing inventory, time on market, price per square foot and geographic distributions.

### 2. Why is Pandas used?
Pandas is used for reading CSV files, cleaning data, grouping records, filtering and calculating statistics.

### 3. What is data normalization in this project?
It means converting inconsistent raw listing data into a consistent schema and valid numeric/geographic values.

### 4. Why are duplicates removed?
Duplicate listings can inflate inventory counts and produce misleading statistics.

### 5. How is price per square foot calculated?
`property_price / area_sqft`.

### 6. Why is Streamlit used?
Streamlit provides a simple way to convert Python analytics code into an interactive web dashboard.

### 7. Why is Plotly used?
Plotly provides interactive charts with hover information, zooming and filtering-friendly visuals.

### 8. Why is Folium used?
Folium is used to display geographic information on interactive web maps.

### 9. What is time on market?
It is the number of days a property listing has remained on the market.

### 10. What can high DOM indicate?
High DOM can indicate slower-moving inventory, although it may also depend on pricing, property condition and demand.

### 11. How are invalid coordinates handled?
Latitude and longitude are checked against their valid ranges and invalid rows are removed.

### 12. Why calculate median price?
Median is less affected by unusually expensive properties than the average.

### 13. What is inventory concentration?
It shows what percentage of total listings belongs to each locality.

### 14. Can the project accept another CSV?
Yes. The dashboard has a CSV uploader and maps common column-name variations.

### 15. What are the main modules?
Data cleaning, analytics, charts, maps and the Streamlit application interface.

## Conclusion

This project demonstrates an end-to-end B.Tech IT data analytics workflow: data collection through CSV, cleaning and normalization, exploratory analysis, statistical calculations, geographic visualization and an interactive Streamlit dashboard. It is intentionally kept understandable for a GTU mini-project and viva while still presenting a professional interface.
