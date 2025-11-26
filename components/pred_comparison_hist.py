"""
Model Page Comparison Visualization 2
Histogram showing distribution of actual FLFP rates with predicted value marked
"""

import plotly.graph_objects as go
from dash import dcc
import numpy as np
import seaborn as sns
from utils.map_data_utils import get_flfp_distribution

def create_prediction_comparison_viz_2(predicted_probability, df_real_data):
    """
    Create histogram showing distribution of actual FLFP rates from test set
    with the predicted value marked as a vertical line.
    
    Args:
        predicted_probability: The predicted FLFP value (float)
        df_real_data: DataFrame with real country data (not used, kept for compatibility)
        
    Returns:
        dcc.Graph: Plotly graph component with histogram
    """
    # Get actual FLFP values from test set
    flfp_values, country_names = get_flfp_distribution()
    
    # Calculate percentile of prediction
    percentile = (flfp_values < predicted_probability).sum() / len(flfp_values) * 100
    
    # Get Mako color for histogram bars (mid-range color from palette)
    mako_colors = sns.color_palette("mako", n_colors=10)
    mako_blue = '#%02x%02x%02x' % (int(mako_colors[5][0]*255), int(mako_colors[5][1]*255), int(mako_colors[5][2]*255))
    
    # Create histogram
    fig = go.Figure()
    
    # Add histogram with Mako color
    fig.add_trace(go.Histogram(
        x=flfp_values,
        nbinsx=15,  # 15 bins for ~5% width each
        name='Countries',
        marker=dict(
            color=mako_blue,  # Mako blue from seaborn palette
            line=dict(color='white', width=1)
        ),
        hovertemplate='<b>FLFP Range:</b> %{x:.1f}%<br>' +
                      '<b>Count:</b> %{y} countries<br>' +
                      '<extra></extra>'
    ))
    
    # Add vertical line for predicted value (Plotly orange)
    fig.add_vline(
        x=predicted_probability,
        line=dict(color='#EF553B', width=3, dash='dash'),
        annotation=dict(
            text=f"Predicted: {predicted_probability:.1f}%",
            textangle=-90,
            yshift=10,
            font=dict(size=12, color='#EF553B')
        )
    )
    
    # Add shaded area to show percentile
    fig.add_vrect(
        x0=flfp_values.min(),
        x1=predicted_probability,
        fillcolor='#EF553B',
        opacity=0.1,
        line_width=0,
        annotation=dict(
            text=f"{percentile:.0f}th percentile",
            textangle=0,
            x=predicted_probability/2,
            y=0.95,
            yref='paper',
            showarrow=False,
            font=dict(size=10, color='#666')
        )
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Where Does This Prediction Fall?",
            font=dict(size=14, color='#2c3e50')
        ),
        xaxis=dict(
            title='Female Labor Force Participation Rate (%)',
            range=[0, 90],
            ticksuffix='%',
            gridcolor='#e0e0e0'
        ),
        yaxis=dict(
            title='Number of Countries',
            gridcolor='#e0e0e0'
        ),
        template='plotly_white',
        showlegend=False,
        height=None,  # Let container control height
        autosize=True,
        margin=dict(l=50, r=30, t=50, b=50),
        hovermode='x'
    )
    
    return dcc.Graph(
        figure=fig,
        id="pred-comparison-viz-2",
        config={'displayModeBar': False},
        style={"height": "100%"}  # Fill container
    )

