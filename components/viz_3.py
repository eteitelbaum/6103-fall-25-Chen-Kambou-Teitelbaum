"""
Dashboard Visualization 3
Bottom row (full-width) visualization on the dashboard page.
Team members can work on this module independently.
"""

import plotly.graph_objects as go
from dash import dcc
import pandas as pd

def create_viz_3(df_filtered, selected_indicator=None):
    """
    Create the third visualization (placeholder).
    This will be displayed in the bottom row (full width) on the dashboard.
    
    Args:
        df_filtered: Filtered pandas DataFrame
        selected_indicator: Name of the indicator column to visualize
        
    Returns:
        dcc.Graph: Plotly graph component
    """
    # Placeholder: Create an empty figure
    fig = go.Figure()
    
    # Get indicator label for display
    indicator_label = selected_indicator.replace('_', ' ').title() if selected_indicator else "Indicator"
    
    fig.add_annotation(
        text=f"Visualization 3 - To be implemented\nSelected indicator: {indicator_label}",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        title=f"Visualization 3: {indicator_label}",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template="plotly_white"
    )
    
    return dcc.Graph(figure=fig, id="viz-3")

