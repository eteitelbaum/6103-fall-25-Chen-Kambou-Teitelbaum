"""
Data loading utilities for the FLFP Data Explorer app
"""

import pandas as pd
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "flfp_dataset.parquet"

# Global variable to cache the loaded data
_cached_data = None

def load_flfp_data():
    """
    Load the FLFP dataset from parquet file.
    Uses caching to avoid reloading on every call.
    
    Returns:
        pd.DataFrame: The loaded dataset
    """
    global _cached_data
    
    if _cached_data is None:
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"Data file not found at {DATA_PATH}")
        
        _cached_data = pd.read_parquet(DATA_PATH)
        # Standardize region names
        _cached_data['region'] = _cached_data['region'].apply(_standardize_region_name)
        print(f"Loaded dataset: {_cached_data.shape[0]:,} rows × {_cached_data.shape[1]} columns")
    
    return _cached_data.copy()


def _standardize_region_name(region_name):
    """
    Standardize region names to shorter versions.
    
    Args:
        region_name: Original region name
        
    Returns:
        str: Standardized region name
    """
    if pd.isna(region_name):
        return region_name
    
    # Replace long region names with shorter versions
    replacements = {
        "Middle East, North Africa, Afghanistan & Pakistan": "MENA + AfPak"
    }
    
    return replacements.get(region_name, region_name)

def get_data_summary():
    """
    Get a summary of the dataset structure.
    
    Returns:
        dict: Summary information about the dataset
    """
    df = load_flfp_data()
    
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
        "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
        "years": sorted(df['year'].unique().tolist()) if 'year' in df.columns else [],
        "countries": sorted(df['country_name'].unique().tolist()) if 'country_name' in df.columns else [],
        "regions": sorted(df['region'].dropna().unique().tolist()) if 'region' in df.columns else [],
        "indicators": get_indicator_options(),
    }

def get_indicator_options():
    """
    Get list of available indicators (numeric columns) for visualization.
    Excludes 'year' and metadata columns.
    
    Returns:
        list: List of indicator column names with human-readable labels
    """
    df = load_flfp_data()
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Exclude year column
    indicators = [col for col in numeric_cols if col != 'year']
    
    # Custom label mapping for better readability
    label_mapping = {
        "flfp_15_64": "FLFP Rates (ages 15-64)",
        "dependency_ratio": "Dependency Ratio",
        "fertility_adolescent": "Adolescent Fertility Rate",
        "fertility_rate": "Total Fertility Rate",
        "gdp_growth": "GDP Growth (%)",
        "gdp_per_capita_const": "GDP per Capita (constant)",
        "gender_parity_primary": "Gender Parity (primary education)",
        "gender_parity_secondary": "Gender Parity (secondary education)",
        "industry_gdp": "Industry Share of GDP (%)",
        "infant_mortality": "Infant Mortality Rate",
        "labor_force_total": "Total Labor Force",
        "life_exp_female": "Female Life Expectancy",
        "population_total": "Total Population",
        "rule_of_law": "Rule of Law Index",
        "secondary_enroll_fe": "Female Secondary Enrollment (%)",
        "services_gdp": "Services Share of GDP (%)",
        "tertiary_enroll_fe": "Female Tertiary Enrollment (%)",
        "unemployment_female": "Female Unemployment (%)",
        "unemployment_total": "Total Unemployment (%)",
        "urban_population": "Urban Population (%)"
    }
    
    # Create indicator options with custom labels
    indicator_options = []
    for col in indicators:
        label = label_mapping.get(col, col.replace('_', ' ').title())
        indicator_options.append({
            "value": col,
            "label": label
        })
    
    # Sort by label, but put flfp_15_64 first as default
    indicator_options.sort(key=lambda x: x["label"])
    
    # Move flfp_15_64 to the front if it exists
    flfp_idx = next((i for i, opt in enumerate(indicator_options) if opt["value"] == "flfp_15_64"), None)
    if flfp_idx is not None:
        flfp_option = indicator_options.pop(flfp_idx)
        indicator_options.insert(0, flfp_option)
    
    return indicator_options

