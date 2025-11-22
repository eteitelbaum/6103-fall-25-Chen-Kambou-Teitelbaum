"""
Sunburst Chart for Dashboard
Interactive chart showing regions and countries sized by labor force
"""

import plotly.graph_objects as go
from dash import dcc
import pandas as pd


def create_sunburst(df_filtered, selected_indicator, mode=None, selected_region=None, selected_countries=None):
    """
    Create an interactive sunburst chart.
    
    Args:
        df_filtered: Filtered pandas DataFrame
        selected_indicator: Name of the indicator column (used for coloring)
        mode: Display mode (optional, for visual feedback)
        selected_region: Selected region name (for highlighting)
        selected_countries: List of selected country names (for highlighting)
        
    Returns:
        dcc.Graph: Plotly sunburst chart component
    """
    if df_filtered.empty or 'labor_force_total' not in df_filtered.columns:
        return _create_empty_chart(selected_indicator)
    
    if selected_indicator not in df_filtered.columns:
        return _create_empty_chart(selected_indicator)
    
    # Prepare data for sunburst
    sunburst_data = _prepare_sunburst_data(df_filtered, selected_indicator)
    
    if sunburst_data.empty:
        return _create_empty_chart(selected_indicator)
    
    # Determine which items to highlight
    highlight_items = set()
    if selected_region and mode == "region_only":
        highlight_items.add(selected_region)
    elif selected_countries and mode == "single_country":
        highlight_items.update(selected_countries)
    
    # Create the sunburst chart
    fig = _create_sunburst_figure(sunburst_data, selected_indicator, highlight_items)
    
    return dcc.Graph(
        figure=fig, 
        id="viz-2",
        config={'displayModeBar': False}
    )


def _prepare_sunburst_data(df, indicator):
    """
    Prepare hierarchical data for sunburst chart.
    Structure: Root -> Regions -> Countries
    Sized by total labor force, colored by indicator value.
    """
    # Calculate total labor force and average indicator per country
    country_data = df.groupby(['country_name', 'region']).agg({
        'labor_force_total': 'sum',
        indicator: 'mean'
    }).reset_index()
    country_data = country_data[country_data['labor_force_total'] > 0]  # Filter out zeros
    
    if country_data.empty:
        return pd.DataFrame()
    
    # Calculate regional totals and averages (weighted by labor force)
    regional_data = df.groupby('region').agg({
        'labor_force_total': 'sum',
        indicator: 'mean'
    }).reset_index()
    
    # Calculate global average
    global_labor_force = country_data['labor_force_total'].sum()
    global_indicator = df[indicator].mean()
    
    # Build hierarchical structure
    labels = ["World"]  # Root
    parents = [""]
    values = [global_labor_force]
    colors = [global_indicator]
    
    # Add regions
    for _, row in regional_data.iterrows():
        labels.append(row['region'])
        parents.append("World")
        values.append(row['labor_force_total'])
        colors.append(row[indicator])
    
    # Add countries
    for _, row in country_data.iterrows():
        labels.append(row['country_name'])
        parents.append(row['region'])
        values.append(row['labor_force_total'])
        colors.append(row[indicator])
    
    return pd.DataFrame({
        'labels': labels,
        'parents': parents,
        'values': values,
        'colors': colors
    })


def _create_sunburst_figure(data, indicator, highlight_items=None):
    """Create the sunburst visualization colored by indicator value."""
    highlight_items = highlight_items or set()
    
    # Format indicator label
    indicator_label = _format_label(indicator)
    
    fig = go.Figure(go.Sunburst(
        labels=data['labels'],
        parents=data['parents'],
        values=data['values'],
        branchvalues='total',
        marker=dict(
            colors=data['colors'],
            colorscale='Plotly3',
            cmid=data['colors'].mean(),
            line=dict(color='white', width=2),
            colorbar=dict(
                title=indicator_label,
                thickness=15,
                len=0.7
            )
        ),
        hovertemplate='<b>%{label}</b><br>' +
                      'Labor Force: %{value:,.0f}<br>' +
                      indicator_label + ': %{color:.2f}<br>' +
                      '<extra></extra>',
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Labor Force Distribution by Region and Country<br><sub>Colored by {indicator_label}</sub>",
            font=dict(size=16)
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=400,
        template="plotly_white"
    )
    
    return fig


def _create_empty_chart(indicator=None):
    """Create an empty chart with a message."""
    fig = go.Figure()
    fig.add_annotation(
        text="No labor force data available",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="gray")
    )
    fig.update_layout(
        title="Labor Force Distribution",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template="plotly_white",
        height=500
    )
    return dcc.Graph(figure=fig, id="viz-2", config={'displayModeBar': False})


def _format_label(column_name):
    """Convert snake_case column name to Title Case label."""
    if not column_name:
        return "Indicator"
    return column_name.replace('_', ' ').title()
