from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pandas as pd
from typing import List, Optional
import os
import re

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

def parse_maturity(val: str):
    """
    Helper to sort time-to-maturity strings.
    Returns (start, end) tuple.
    """
    if not val:
        return (float('inf'), float('inf'))
    
    s = val.lower()
    nums = re.findall(r'\d+', s)
    if not nums:
        return (float('inf'), float('inf'))
    
    # Check for years (if 'year' appears, treat all numbers as years, else months)
    # This is a simplification but works for this dataset where units aren't mixed like "1 year 6 months"
    is_years = 'year' in s
    factor = 12.0 if is_years else 1.0
    
    start = float(nums[0]) * factor
    end = float(nums[1]) * factor if len(nums) > 1 else start
    
    return (start, end)

def parse_lifespan(val: str):
    """
    Helper to sort lifespan strings.
    Returns tuple (start, end) for robust sorting.
    """
    if not val:
        return (float('inf'), float('inf'))
    
    s = val.lower()
    
    # Special cases
    if 'annual' in s:
        return (0.1, 0.1)
    if 'biennial' in s:
        return (0.2, 0.2)
    if 'perennial' in s:
        return (0.3, 0.3)
        
    # Find all numbers
    nums = re.findall(r'\d+', s)
    if not nums:
        # If no numbers (e.g. "Perennial"), treat as very long
        return (9999.0, 9999.0)
    
    # Determine unit
    is_months = 'month' in s and 'year' not in s
    factor = 1.0/12.0 if is_months else 1.0
    
    start = float(nums[0]) * factor
    end = float(nums[1]) * factor if len(nums) > 1 else start
    
    # Handle "Up to" - usually implies 0 to X, but for sorting we might want it near X or 0?
    # If we treat "Up to 30" as start=30, it sorts with 30-40. 
    # If we treat as start=0, it sorts with 0-1.
    # Let's keep existing behavior (start=number found) but add secondary sort.
    
    return (start, end)

def parse_strata(val: str):
    """
    Custom sort order for Strata: Emergent, Low, Medium, High
    """
    order = {
        "Emergent": 0,
        "Low": 1,
        "Medium": 2,
        "High": 3
    }
    return order.get(val, 99)

def parse_spacing(val: str):
    """
    Helper to sort spacing strings.
    Converts 'X m', 'X cm', 'X-Y m' into meters for comparison.
    Handles mixed units like '50 cm - 1 m'.
    """
    if not val:
        return (float('inf'), float('inf'))
        
    s = val.lower()
    
    # Find all numeric values with their optional units
    # Matches: "50", "cm" | "1", "m" | "10", ""
    matches = re.findall(r'([\d\.]+)\s*(cm|m)?', s)
    
    if not matches:
        return (float('inf'), float('inf'))
        
    parsed_values = []
    current_unit = 'm' # Default unit if not specified (though usually it inherits from context)
    
    # Iterate backwards to infer unit if missing? 
    # E.g. "10-20 cm" -> 10 has no unit, 20 has cm. Both are cm.
    
    # Let's simplify: if string contains 'cm' anywhere, treat numbers as cm unless they have explicit 'm'?
    # Too complex.
    
    # Strategy: Find global unit if exists.
    global_is_cm = 'cm' in s
    global_factor = 0.01 if global_is_cm else 1.0
    
    # If explicit units are attached to numbers, use them.
    # "50cm - 1 m"
    # match 1: 50, cm -> 0.5m
    # match 2: 1, m -> 1.0m
    
    vals = []
    for num_str, unit in matches:
        if not num_str: continue
        val = float(num_str)
        
        if unit == 'cm':
            val *= 0.01
        elif unit == 'm':
            val *= 1.0
        else:
            # No unit on this number. Use global preference.
            # But wait, "50cm - 1m". 1 has m. 50 has cm.
            # "10-20 cm". 10 has empty. 20 has cm.
            # If we used global_factor for empty, "50cm - 1m": 50->cm, 1->m. Correct.
            # "10-20 cm": 10->cm (global), 20->cm. Correct.
            # "1-2 m": 1->m (global), 2->m. Correct.
            val *= global_factor
            
        vals.append(val)
        
    if not vals:
        return (float('inf'), float('inf'))
        
    start = vals[0]
    end = vals[1] if len(vals) > 1 else start
    
    return (start, end)

@app.get("/api/filters")
def get_filters():
    print("CALLED GET_FILTERS")
    """Return unique values for all filterable columns"""
    filters = {
        "plant_family": sorted(df_plants["Plant Family"].unique().tolist()),
        "strata": sorted(df_plants["Strata"].unique().tolist(), key=parse_strata),
        "lifecycle": sorted(df_plants["Lifecycle"].unique().tolist()),
        "time_to_maturity": sorted(df_plants["Time-to-Maturity"].unique().tolist(), key=parse_maturity),
        "lifespan": sorted(df_plants["Lifespan"].unique().tolist(), key=parse_lifespan),
        "zone": sorted(df_plants["Zone"].unique().tolist()),
        "origin": sorted(df_plants["Origin"].unique().tolist()),
        "function": sorted(df_plants["Function"].unique().tolist()),
        "spacing": sorted(df_plants["Spacing"].unique().tolist(), key=parse_spacing),
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
