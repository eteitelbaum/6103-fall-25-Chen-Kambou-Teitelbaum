"""
Model Page Comparison Visualization 1
Clickable choropleth map showing actual FLFP rates by country
"""

import plotly.express as px
from dash import dcc
import seaborn as sns
from utils.map_data_utils import load_test_set_data

def create_prediction_comparison_viz_1(predicted_probability, df_real_data):
    """
    Create interactive choropleth map showing actual FLFP rates by country.
    Click on a country to update the sliders with that country's values.
    
    Args:
        predicted_probability: The predicted FLFP value (float, for display)
        df_real_data: DataFrame with real country data (not used, kept for compatibility)
        
    Returns:
        dcc.Graph: Plotly graph component with interactive map
    """
    # Load test set data with ISO codes
    test_df = load_test_set_data()
    
    # Get Mako colors from seaborn and convert to hex
    mako_colors = sns.color_palette("mako", as_cmap=False, n_colors=256)
    mako_hex = ['#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255)) for r, g, b in mako_colors]
    
    # Create choropleth map
    fig = px.choropleth(
        test_df,
        locations='iso3c',
        locationmode='ISO-3',
        color='flfp_15_64',
        hover_name='country_name',
        hover_data={
            'iso3c': False,  # Hide ISO code
            'flfp_15_64': ':.1f',  # Format FLFP to 1 decimal
            'year': True
        },
        color_continuous_scale=mako_hex,  # Mako palette from seaborn
        range_color=[0, 90],
        labels={'flfp_15_64': 'FLFP Rate (%)'},
        title='Actual FLFP Rates by Country (Click to Load Values)'
    )
    
    # Update map layout
    fig.update_geos(
        showcountries=True,
        countrycolor='lightgray',
        showcoastlines=True,
        coastlinecolor='white',
        projection_type='natural earth',
        bgcolor='#f8f9fa'
    )
    
    # Update overall layout
    fig.update_layout(
        title=dict(
            text=f'Actual FLFP Rates by Country<br><sub>Click a country to load its values | Predicted: {predicted_probability:.1f}%</sub>',
            font=dict(size=14, color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        height=None,  # Let container control height
        autosize=True,
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(
            title='FLFP Rate (%)',
            ticksuffix='%',
            len=0.7,
            yanchor='middle',
            y=0.5
        ),
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Arial'
        )
    )
    
    return dcc.Graph(
        figure=fig,
        id="pred-comparison-viz-1",
        config={
            'displayModeBar': False,
            'scrollZoom': False
        },
        style={"height": "100%"}  # Fill container
    )

