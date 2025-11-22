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
        print(f"Loaded dataset: {_cached_data.shape[0]:,} rows × {_cached_data.shape[1]} columns")
    
    return _cached_data.copy()

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
    
    # Create human-readable labels
    indicator_options = []
    for col in indicators:
        # Convert snake_case to Title Case
        label = col.replace('_', ' ').title()
        indicator_options.append({
            "value": col,
            "label": label
        })
    
    # Sort by label
    indicator_options.sort(key=lambda x: x["label"])
    
    return indicator_options

