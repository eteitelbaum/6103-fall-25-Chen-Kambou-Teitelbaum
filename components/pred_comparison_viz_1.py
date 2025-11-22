"""
Model Page Comparison Visualization 1
First comparison visualization showing where predicted probability falls
in relation to real countries.
Team members can work on this module independently.
"""

import plotly.graph_objects as go
from dash import dcc
import pandas as pd

def create_prediction_comparison_viz_1(predicted_probability, df_real_data):
    """
    Create the first comparison visualization for the model page.
    Shows where the predicted probability falls in relation to real countries.
    
    Args:
        predicted_probability: The predicted probability value
        df_real_data: DataFrame with real country data
        
    Returns:
        dcc.Graph: Plotly graph component
    """
    # Placeholder: Create an empty figure
    fig = go.Figure()
    fig.add_annotation(
        text="Prediction Comparison Viz 1 - To be implemented",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        title="Comparison Visualization 1",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template="plotly_white"
    )
    
    return dcc.Graph(figure=fig, id="pred-comparison-viz-1")

