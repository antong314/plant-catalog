from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pandas as pd
from typing import List, Optional
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Data
CSV_PATH = "../tropical-plants.csv"
IMG_DIR = "../img"

# Mount static images
app.mount("/images", StaticFiles(directory=IMG_DIR), name="images")

def load_data():
    if not os.path.exists(CSV_PATH):
        return []
    
    df = pd.read_csv(CSV_PATH)
    # Fill NaN with empty string to avoid JSON errors
    df = df.fillna("")
    return df

df_plants = load_data()

@app.get("/api/filters")
def get_filters():
    """Return unique values for all filterable columns"""
    filters = {
        "plant_family": sorted(df_plants["Plant Family"].unique().tolist()),
        "strata": sorted(df_plants["Strata"].unique().tolist()),
        "lifecycle": sorted(df_plants["Lifecycle"].unique().tolist()),
        "time_to_maturity": sorted(df_plants["Time-to-Maturity"].unique().tolist()),
        "lifespan": sorted(df_plants["Lifespan"].unique().tolist()),
        "zone": sorted(df_plants["Zone"].unique().tolist()),
        "origin": sorted(df_plants["Origin"].unique().tolist()),
        "function": sorted(df_plants["Function"].unique().tolist()),
        "spacing": sorted(df_plants["Spacing"].unique().tolist()),
    }
    # Remove empty strings from filters if any
    for key in filters:
        filters[key] = [x for x in filters[key] if x]
    return filters

@app.get("/api/plants")
def get_plants(
    q: Optional[str] = None,
    ids: Optional[List[str]] = Query(None),
    plant_family: Optional[List[str]] = Query(None),
    strata: Optional[List[str]] = Query(None),
    lifecycle: Optional[List[str]] = Query(None),
    time_to_maturity: Optional[List[str]] = Query(None),
    lifespan: Optional[List[str]] = Query(None),
    zone: Optional[List[str]] = Query(None),
    origin: Optional[List[str]] = Query(None),
    function: Optional[List[str]] = Query(None),
    spacing: Optional[List[str]] = Query(None),
):
    filtered_df = df_plants.copy()

    # Filter by IDs (Favorites)
    if ids:
        filtered_df = filtered_df[filtered_df["Botanical Name"].isin(ids)]

    # Search (Case insensitive partial match on English or Botanical Name)
    if q:
        mask = (
            filtered_df["English Name"].str.contains(q, case=False, na=False) | 
            filtered_df["Botanical Name"].str.contains(q, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    # Filters (OR logic within category, AND across categories)
    # Since we are filtering sequentially, we achieve AND across categories.
    # For each category, we check if the value is in the provided list (OR logic).
    
    filter_map = {
        "Plant Family": plant_family,
        "Strata": strata,
        "Lifecycle": lifecycle,
        "Time-to-Maturity": time_to_maturity,
        "Lifespan": lifespan,
        "Zone": zone,
        "Origin": origin,
        "Function": function,
        "Spacing": spacing,
    }

    for col, values in filter_map.items():
        if values:
            filtered_df = filtered_df[filtered_df[col].isin(values)]

    # Convert to list of dicts
    result = filtered_df.to_dict(orient="records")
    
    # Map keys to be more frontend friendly if needed, generally raw CSV headers are okay 
    # but let's stick to raw headers to avoid confusion, frontend can handle mapping.
    
    return result
