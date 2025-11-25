"""
Preprocess test set data for model visualizations
Filters to test years (2021-2023), gets most recent year per country,
applies median imputation, and saves to data/test_set_latest.csv
"""

import pandas as pd
import numpy as np
import json

print("=" * 60)
print("PREPROCESSING TEST SET DATA FOR VISUALIZATIONS")
print("=" * 60)

# Load the full FLFP dataset
print("\n1. Loading full dataset...")
flfp_df = pd.read_parquet('data/flfp_dataset.parquet')
flfp_df['region'] = flfp_df['region'].str.strip()
print(f"   Loaded {len(flfp_df):,} observations")

# Filter to observations with FLFP data
modeling_df = flfp_df[flfp_df['flfp_15_64'].notna()].copy()
print(f"   Filtered to {len(modeling_df):,} observations with FLFP data")

# Define train and test years
print("\n2. Defining time splits...")
years = np.sort(modeling_df['year'].unique())
n_years = len(years)
train_end_idx = int(np.floor(0.8 * n_years))
val_end_idx = int(np.floor(0.9 * n_years))

train_years = years[:train_end_idx]
test_years = years[val_end_idx:]

print(f"   Train years: {train_years[0]}-{train_years[-1]} ({len(train_years)} years)")
print(f"   Test years: {test_years[0]}-{test_years[-1]} ({len(test_years)} years)")

# Filter to train and test sets
train_df = modeling_df[modeling_df['year'].isin(train_years)].copy()
test_df = modeling_df[modeling_df['year'].isin(test_years)].copy()

print(f"   Train: {len(train_df):,} observations")
print(f"   Test: {len(test_df):,} observations")

# Filter out 'Not classified' income observations
print("\n3. Filtering out 'Not classified' income levels...")
initial_test = len(test_df)
test_df = test_df[test_df['income_level'] != 'Not classified'].copy()
print(f"   Test: {initial_test:,} → {len(test_df):,} (-{initial_test - len(test_df)})")

# Get most recent year per country in test set
print("\n4. Getting most recent year per country...")
test_latest = test_df.loc[test_df.groupby('country_name')['year'].idxmax()].copy()
print(f"   {len(test_latest)} countries with data in test period")

# Show year distribution
year_counts = test_latest['year'].value_counts().sort_index()
print(f"   Year distribution:")
for year, count in year_counts.items():
    print(f"     {year}: {count} countries")

# Create label-encoded income
print("\n5. Creating label-encoded income...")
income_mapping = {
    'Low income': 0,
    'Lower middle income': 1,
    'Upper middle income': 2,
    'High income': 3
}
test_latest['income_level_encoded'] = test_latest['income_level'].map(income_mapping)

# Create one-hot encoded region
print("\n6. Creating one-hot encoded region...")
region_name_mapping = {
    'East Asia & Pacific': 'region_eap',
    'Europe & Central Asia': 'region_eca',
    'Latin America & Caribbean': 'region_lac',
    'Middle East, North Africa, Afghanistan & Pakistan': 'region_mena_afpak',
    'North America': 'region_namerica',
    'South Asia': 'region_sasia',
    'Sub-Saharan Africa': 'region_ssa'
}

# Create dummies
region_dummies = pd.get_dummies(test_latest['region'], prefix='region', drop_first=False)

# Rename columns
for original, clean in region_name_mapping.items():
    old_col = f'region_{original}'
    if old_col in region_dummies.columns:
        region_dummies.rename(columns={old_col: clean}, inplace=True)

# Drop reference category
reference_region = 'region_mena_afpak'
if reference_region in region_dummies.columns:
    region_dummies.drop(columns=[reference_region], inplace=True)

# Add to dataframe
test_latest = pd.concat([test_latest, region_dummies], axis=1)
region_cols = [col for col in test_latest.columns if col.startswith('region_')]
print(f"   Created {len(region_cols)} region dummy variables")

# Log-transform population_total
print("\n7. Applying log transformation to population_total...")
test_latest['population_total'] = np.log(test_latest['population_total'])

# Define variables to impute (same as in notebook)
variables_to_impute = [
    'secondary_enroll_fe', 'urban_population', 'infant_mortality',
    'gdp_per_capita_const', 'gdp_growth', 'services_gdp',
    'industry_gdp', 'rule_of_law'
]

# Calculate imputation statistics from TRAINING data only
print("\n8. Calculating imputation statistics from training data...")
print("   (Using training years 2000-2018 to avoid data leakage)")

# Apply same preprocessing to training data
train_df_proc = train_df[train_df['income_level'] != 'Not classified'].copy()
train_df_proc['population_total'] = np.log(train_df_proc['population_total'])

train_country_medians = {}
train_year_medians = {}
train_global_medians = {}

for var in variables_to_impute:
    train_country_medians[var] = train_df_proc.groupby('country_name')[var].median()
    train_year_medians[var] = train_df_proc.groupby('year')[var].median()
    train_global_medians[var] = train_df_proc[var].median()

# Apply imputation to test set using training statistics
print("\n9. Applying median imputation to test set...")
test_imputed = test_latest.copy()

missing_before = test_imputed[variables_to_impute].isna().sum().sum()

for var in variables_to_impute:
    if var in test_imputed.columns:
        # Use training-based country medians
        for country in test_imputed['country_name'].unique():
            country_mask = test_imputed['country_name'] == country
            country_median = train_country_medians[var].get(country, np.nan)
            
            # Fill using country median where available
            test_imputed.loc[country_mask, var] = test_imputed.loc[country_mask, var].fillna(country_median)
        
        # Fill remaining NaNs using year medians (from training data)
        year_values = test_imputed.loc[:, 'year']
        missing_mask = test_imputed[var].isna()
        if missing_mask.any():
            years_to_fill = year_values[missing_mask]
            # For test years not in training, use the most recent training year median
            fill_values = years_to_fill.map(train_year_medians[var])
            # If year not in training data, use global training median
            fill_values = fill_values.fillna(train_global_medians[var])
            test_imputed.loc[missing_mask, var] = fill_values
        
        # Fall back to training-global median if still missing
        test_imputed[var] = test_imputed[var].fillna(train_global_medians[var])

missing_after = test_imputed[variables_to_impute].isna().sum().sum()
print(f"   Missing values: {missing_before} → {missing_after}")

# Select columns to save
predictor_cols = [
    'fertility_rate', 'fertility_adolescent', 'urban_population',
    'dependency_ratio', 'life_exp_female', 'infant_mortality',
    'population_total', 'secondary_enroll_fe', 'gdp_per_capita_const',
    'gdp_growth', 'services_gdp', 'industry_gdp', 'rule_of_law',
    'income_level_encoded'
] + region_cols

columns_to_save = ['country_name', 'iso3c', 'year', 'flfp_15_64'] + predictor_cols

test_final = test_imputed[columns_to_save].copy()

# Save to CSV
print("\n10. Saving processed test set...")
output_path = 'data/test_set_latest.csv'
test_final.to_csv(output_path, index=False)
print(f"    Saved to: {output_path}")
print(f"    Shape: {test_final.shape}")
print(f"    Columns: {len(test_final.columns)}")

# Create summary statistics
print("\n11. Creating summary...")
summary = {
    'total_countries': len(test_final),
    'year_range': f"{test_final['year'].min()}-{test_final['year'].max()}",
    'flfp_range': f"{test_final['flfp_15_64'].min():.1f}-{test_final['flfp_15_64'].max():.1f}",
    'flfp_mean': float(test_final['flfp_15_64'].mean()),
    'flfp_median': float(test_final['flfp_15_64'].median()),
    'missing_values': int(test_final[predictor_cols].isna().sum().sum()),
    'predictor_count': len(predictor_cols)
}

print(f"\n    Total countries: {summary['total_countries']}")
print(f"    Year range: {summary['year_range']}")
print(f"    FLFP range: {summary['flfp_range']}%")
print(f"    FLFP mean: {summary['flfp_mean']:.1f}%")
print(f"    FLFP median: {summary['flfp_median']:.1f}%")
print(f"    Missing values: {summary['missing_values']}")
print(f"    Predictor features: {summary['predictor_count']}")

# Check Madagascar data
print("\n12. Checking Madagascar data...")
madagascar = test_final[test_final['country_name'] == 'Madagascar']
if len(madagascar) > 0:
    print(f"    Madagascar found: Year {madagascar['year'].values[0]}, FLFP {madagascar['flfp_15_64'].values[0]:.1f}%")
else:
    print("    Madagascar not found in test set (may need to use training data for default)")

print("\n" + "=" * 60)
print("PREPROCESSING COMPLETE!")
print("=" * 60)
