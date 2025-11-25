"""
Line Chart for Dashboard
Displays temporal trends for regions or countries based on selection state
"""

import plotly.graph_objects as go
from dash import dcc
import pandas as pd
import plotly.express as px

# Generate color sequence from Turbo colorscale
TURBO_COLORS = px.colors.sample_colorscale("Turbo", [i/15 for i in range(16)])


def create_line_chart(df_filtered, selected_indicator, mode, selected_region=None, selected_countries=None):
    """
    Create a line chart showing trends over time based on selection mode.
    
    Args:
        df_filtered: Filtered pandas DataFrame
        selected_indicator: Name of the indicator column to visualize
        mode: Display mode - "all_regions", "region_only", "single_country", "multi_country"
        selected_region: Selected region name (if mode is "region_only" or "single_country")
        selected_countries: List of selected country names (if mode is "single_country" or "multi_country")
        
    Returns:
        dcc.Graph: Plotly graph component with line chart
    """
    if df_filtered.empty or selected_indicator not in df_filtered.columns:
        return _create_empty_chart(selected_indicator)
    
    # Create line chart based on mode
    if mode == "all_regions":
        fig = _create_regional_trends(df_filtered, selected_indicator)
        title = f"Regional Trends: {_format_label(selected_indicator)}"
        
    elif mode == "region_only":
        # Show all countries in selected region
        df_region = df_filtered[df_filtered['region'] == selected_region]
        fig = _create_country_trends(df_region, selected_indicator, highlight_countries=[])
        title = f"{selected_region} Country Trends: {_format_label(selected_indicator)}"
        
    elif mode == "single_country":
        # Show all countries in the same region, highlight selected
        selected_country = selected_countries[0]
        country_region = df_filtered[df_filtered['country_name'] == selected_country]['region'].iloc[0]
        df_region = df_filtered[df_filtered['region'] == country_region]
        fig = _create_country_trends(df_region, selected_indicator, highlight_countries=selected_countries)
        title = f"{country_region} Country Trends: {_format_label(selected_indicator)}"
        
    elif mode == "multi_country":
        # Show only selected countries
        df_countries = df_filtered[df_filtered['country_name'].isin(selected_countries)]
        fig = _create_country_trends(df_countries, selected_indicator, highlight_countries=[])
        title = f"Selected Countries Trends: {_format_label(selected_indicator)}"
        
    else:
        return _create_empty_chart(selected_indicator)
    
    fig.update_layout(title=dict(text=title, font=dict(size=16)))
    
    return dcc.Graph(figure=fig, id="viz-3")


def _create_regional_trends(df, indicator):
    """Create line chart with one line per region."""
    # Calculate regional averages by year
    # First get country averages, then average by region and year
    regional_yearly = df.groupby(['region', 'year'])[indicator].mean().reset_index()
    
    fig = go.Figure()
    
    # Add a line for each region with Turbo colors
    regions = sorted(regional_yearly['region'].unique())
    for idx, region in enumerate(regions):
        region_data = regional_yearly[regional_yearly['region'] == region].sort_values('year')
        color = TURBO_COLORS[idx % len(TURBO_COLORS)]
        
        fig.add_trace(go.Scatter(
            x=region_data['year'],
            y=region_data[indicator],
            mode='lines+markers',
            name=region,
            line=dict(width=2, color=color),
            marker=dict(size=6, color=color),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Year: %{x}<br>' +
                         _format_label(indicator) + ': %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        xaxis=dict(
            title="Year",
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title=_format_label(indicator),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        template="plotly_white",
        height=400,
        margin=dict(l=80, r=50, t=80, b=60),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        hovermode='closest'
    )
    
    return fig


def _create_country_trends(df, indicator, highlight_countries=None):
    """Create line chart with one line per country, optionally highlighting some."""
    highlight_countries = highlight_countries or []
    
    # Get country data by year
    country_yearly = df.groupby(['country_name', 'year'])[indicator].mean().reset_index()
    
    fig = go.Figure()
    
    # Separate highlighted and non-highlighted countries
    all_countries = sorted(country_yearly['country_name'].unique())
    
    # Add non-highlighted countries first with Turbo colors
    non_highlighted = [c for c in all_countries if c not in highlight_countries]
    for idx, country in enumerate(non_highlighted):
        country_data = country_yearly[country_yearly['country_name'] == country].sort_values('year')
        color = TURBO_COLORS[idx % len(TURBO_COLORS)]
        
        fig.add_trace(go.Scatter(
            x=country_data['year'],
            y=country_data[indicator],
            mode='lines+markers',
            name=country,
            line=dict(width=1.5, color=color),
            marker=dict(size=4, color=color),
            opacity=0.6 if highlight_countries else 0.8,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Year: %{x}<br>' +
                         _format_label(indicator) + ': %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
    
    # Add highlighted countries (thicker, more prominent) - use bright orange from Turbo
    for country in highlight_countries:
        if country in all_countries:
            country_data = country_yearly[country_yearly['country_name'] == country].sort_values('year')
            
            fig.add_trace(go.Scatter(
                x=country_data['year'],
                y=country_data[indicator],
                mode='lines+markers',
                name=f"{country} ⭐",
                line=dict(width=3, color='#ffa15a'),
                marker=dict(size=8, color='#ffa15a'),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Year: %{x}<br>' +
                             _format_label(indicator) + ': %{y:.2f}<br>' +
                             '<extra></extra>'
            ))
    
    fig.update_layout(
        xaxis=dict(
            title="Year",
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title=_format_label(indicator),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        template="plotly_white",
        height=400,
        margin=dict(l=80, r=50, t=80, b=60),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10)
        ),
        hovermode='closest'
    )
    
    return fig


def _create_empty_chart(indicator):
    """Create an empty chart with a message."""
    fig = go.Figure()
    fig.add_annotation(
        text="No data available for the selected filters",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="gray")
    )
    fig.update_layout(
        title=f"Trends: {_format_label(indicator)}",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template="plotly_white",
        height=400
    )
    return dcc.Graph(figure=fig, id="viz-3")


def _format_label(column_name):
    """Convert column name to properly formatted label."""
    if not column_name:
        return "Indicator"
    
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
    
    return label_mapping.get(column_name, column_name.replace('_', ' ').title())
