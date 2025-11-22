"""
Horizontal Column Chart for Dashboard
Displays regional or country-level averages based on selection state
"""

import plotly.graph_objects as go
from dash import dcc
import pandas as pd


def create_column_chart(df_filtered, selected_indicator, mode, selected_region=None, selected_countries=None):
    """
    Create a horizontal column chart based on selection mode.
    
    Args:
        df_filtered: Filtered pandas DataFrame
        selected_indicator: Name of the indicator column to visualize
        mode: Display mode - "all_regions", "region_only", "single_country", "multi_country"
        selected_region: Selected region name (if mode is "region_only" or "single_country")
        selected_countries: List of selected country names (if mode is "single_country" or "multi_country")
        
    Returns:
        dcc.Graph: Plotly graph component with horizontal bars
    """
    if df_filtered.empty or selected_indicator not in df_filtered.columns:
        return _create_empty_chart(selected_indicator)
    
    # Calculate averages based on mode
    if mode == "all_regions":
        chart_data = _calculate_regional_averages(df_filtered, selected_indicator)
        title = f"Regional Averages: {_format_label(selected_indicator)}"
        highlight_items = []
        
    elif mode == "region_only":
        # Show countries within selected region
        df_region = df_filtered[df_filtered['region'] == selected_region]
        chart_data = _calculate_country_averages(df_region, selected_indicator)
        title = f"{selected_region}: {_format_label(selected_indicator)}"
        highlight_items = []
        
    elif mode == "single_country":
        # Show all countries in the same region, highlight selected
        selected_country = selected_countries[0]
        country_region = df_filtered[df_filtered['country_name'] == selected_country]['region'].iloc[0]
        df_region = df_filtered[df_filtered['region'] == country_region]
        chart_data = _calculate_country_averages(df_region, selected_indicator)
        title = f"{country_region} Countries: {_format_label(selected_indicator)}"
        highlight_items = selected_countries
        
    elif mode == "multi_country":
        # Show only selected countries
        df_countries = df_filtered[df_filtered['country_name'].isin(selected_countries)]
        chart_data = _calculate_country_averages(df_countries, selected_indicator)
        title = f"Selected Countries: {_format_label(selected_indicator)}"
        highlight_items = []
        
    else:
        return _create_empty_chart(selected_indicator)
    
    # Create the horizontal bar chart
    fig = _create_bar_chart(chart_data, title, selected_indicator, highlight_items)
    
    return dcc.Graph(figure=fig, id="viz-1")


def _calculate_regional_averages(df, indicator):
    """Calculate average indicator value per region across all years."""
    # First calculate country averages, then average by region
    country_avg = df.groupby(['region', 'country_name'])[indicator].mean().reset_index()
    regional_avg = country_avg.groupby('region')[indicator].mean().reset_index()
    regional_avg.columns = ['name', 'value']
    # Filter out NaN values (regions with no data)
    regional_avg = regional_avg.dropna(subset=['value'])
    return regional_avg.sort_values('value', ascending=True)


def _calculate_country_averages(df, indicator):
    """Calculate average indicator value per country across all years."""
    country_avg = df.groupby('country_name')[indicator].mean().reset_index()
    country_avg.columns = ['name', 'value']
    # Filter out NaN values (countries with no data)
    country_avg = country_avg.dropna(subset=['value'])
    return country_avg.sort_values('value', ascending=True)


def _create_bar_chart(data, title, indicator, highlight_items=None):
    """Create a horizontal bar chart with optional highlighting."""
    if data.empty:
        return _create_empty_figure(title)
    
    # Determine colors
    # Using teal - distinct from Plotly3 gradient used in sunburst
    highlight_items = highlight_items or []
    colors = ['#00cc96' if name not in highlight_items else '#ffa15a' 
              for name in data['name']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data['value'],
        y=data['name'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        text=data['value'].round(2),
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>' +
                      _format_label(indicator) + ': %{x:.2f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16)
        ),
        xaxis=dict(
            title=_format_label(indicator),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title="",
            automargin=True
        ),
        template="plotly_white",
        height=max(350, len(data) * 18 + 100),
        margin=dict(l=150, r=50, t=80, b=50),
        showlegend=False,
        bargap=0.15
    )
    
    return fig


def _create_empty_chart(indicator):
    """Create an empty chart with a message."""
    fig = _create_empty_figure(f"Column Chart: {_format_label(indicator)}")
    return dcc.Graph(figure=fig, id="viz-1")


def _create_empty_figure(title):
    """Create an empty figure with a message."""
    fig = go.Figure()
    fig.add_annotation(
        text="No data available for the selected filters",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="gray")
    )
    fig.update_layout(
        title=title,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template="plotly_white",
        height=400
    )
    return fig


def _format_label(column_name):
    """Convert snake_case column name to Title Case label."""
    if not column_name:
        return "Indicator"
    return column_name.replace('_', ' ').title()
