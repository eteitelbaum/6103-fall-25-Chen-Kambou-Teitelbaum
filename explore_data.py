"""
FLFP Dataset Explorer
Quick exploration script to verify the downloaded dataset looks correct
"""

import pandas as pd
import numpy as np

def explore_flfp_data():
    """Explore the FLFP dataset with basic checks and summaries"""
    
    print("🔍 FLFP Dataset Exploration")
    print("=" * 50)
    
    # Load the data
    try:
        df = pd.read_parquet("data/flfp_dataset.parquet")
        print(f"✅ Successfully loaded dataset")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Basic info
    print(f"\n📊 Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    # Column names
    print(f"\n📋 Column Names:")
    print(f"Columns: {list(df.columns)}")
    
    # Data types and info
    print(f"\n📈 Dataset Info:")
    df.info()
    
    # First few rows
    print(f"\n👀 First 5 rows:")
    print(df.head().to_string())
    
    # Basic statistics for numeric columns
    print(f"\n📊 Descriptive Statistics (numeric columns only):")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print(df[numeric_cols].describe())
    else:
        print("No numeric columns found")
    
    # Missing data analysis
    print(f"\n❓ Missing Data Analysis:")
    missing_data = df.isnull().sum()
    total_rows = len(df)
    
    print(f"{'Column':<25} {'Missing':<10} {'%':<10}")
    print("-" * 45)
    for col in df.columns:
        missing_count = missing_data[col]
        missing_pct = (missing_count / total_rows) * 100
        print(f"{col:<25} {missing_count:<10} {missing_pct:<10.1f}")
    
    # Year range
    if 'year' in df.columns:
        print(f"\n📅 Time Coverage:")
        print(f"Year range: {df['year'].min()}-{df['year'].max()}")
        print(f"Years available: {sorted(df['year'].unique())}")
        
        # Data by year
        year_counts = df.groupby('year').size()
        print(f"\nObservations per year:")
        print(f"Min: {year_counts.min()}, Max: {year_counts.max()}, Mean: {year_counts.mean():.1f}")
    
    # Country coverage
    if 'country_name' in df.columns:
        print(f"\n🌍 Geographic Coverage:")
        print(f"Countries: {df['country_name'].nunique()}")
        print(f"Total country-year observations: {len(df):,}")
        
        # Top countries by data availability
        country_counts = df.groupby('country_name').size().sort_values(ascending=False)
        print(f"\nTop 10 countries by observations:")
        print(country_counts.head(10).to_string())
    
    # Region analysis if available
    if 'region' in df.columns:
        print(f"\n🌎 Regional Coverage:")
        region_counts = df['region'].value_counts()
        print(region_counts.to_string())
        
        print(f"\nCountries per region:")
        countries_per_region = df.groupby('region')['country_name'].nunique().sort_values(ascending=False)
        print(countries_per_region.to_string())
    
    # Key indicator analysis
    key_indicators = ['flfp_total', 'gdp_per_capita', 'fertility_rate', 'secondary_enroll_fe']
    available_key_indicators = [col for col in key_indicators if col in df.columns]
    
    if available_key_indicators:
        print(f"\n📈 Key Indicators Summary:")
        for indicator in available_key_indicators:
            non_null = df[indicator].notna().sum()
            mean_val = df[indicator].mean()
            min_val = df[indicator].min()
            max_val = df[indicator].max()
            
            print(f"\n{indicator}:")
            print(f"  Non-null observations: {non_null:,} ({(non_null/total_rows)*100:.1f}%)")
            print(f"  Mean: {mean_val:.2f}")
            print(f"  Range: {min_val:.2f} to {max_val:.2f}")
    
    # Sample of recent data
    if 'year' in df.columns:
        print(f"\n📋 Sample of Recent Data (2020-2023):")
        recent_data = df[df['year'].between(2020, 2023)]
        if len(recent_data) > 0:
            sample_cols = ['country_name', 'year']
            sample_cols.extend([col for col in ['flfp_total', 'gdp_per_capita', 'fertility_rate'] if col in df.columns])
            print(recent_data[sample_cols].head(10).to_string(index=False))
        else:
            print("No recent data found")
    
    # Data quality checks
    print(f"\n✅ Data Quality Checks:")
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    print(f"• Duplicate rows: {duplicates}")
    
    # Check year range
    if 'year' in df.columns:
        year_range = df['year'].max() - df['year'].min() + 1
        expected_years = 24  # 2000-2023
        print(f"• Year coverage: {year_range}/{expected_years} years")
    
    # Check for negative values in indicators that shouldn't be negative
    negative_checks = ['flfp_total', 'gdp_per_capita', 'fertility_rate']
    for col in negative_checks:
        if col in df.columns:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                print(f"• Warning: {negative_count} negative values in {col}")
            else:
                print(f"• ✓ No negative values in {col}")
    
    # Check for reasonable ranges
    range_checks = {
        'flfp_total': (0, 100),
        'fertility_rate': (0, 10),
        'urban_population': (0, 100)
    }
    
    for col, (min_expected, max_expected) in range_checks.items():
        if col in df.columns:
            out_of_range = ((df[col] < min_expected) | (df[col] > max_expected)).sum()
            if out_of_range > 0:
                print(f"• Warning: {out_of_range} out-of-range values in {col}")
            else:
                print(f"• ✓ All {col} values in expected range ({min_expected}-{max_expected})")
    
    print(f"\n🎉 Dataset exploration complete!")
    print(f"💡 The dataset appears to be in clean long format - perfect for analysis!")

if __name__ == "__main__":
    explore_flfp_data()