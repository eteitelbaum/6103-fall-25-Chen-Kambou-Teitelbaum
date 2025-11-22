"""
Dashboard page for exploring FLFP dataset
Contains sidebar filters and three visualizations
"""

from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc
from utils.data_loader import load_flfp_data, get_data_summary, get_indicator_options
from components.viz_1 import create_viz_1
from components.viz_2 import create_viz_2
from components.viz_3 import create_viz_3

def create_dashboard_layout():
    """
    Create the dashboard page layout with sidebar and visualizations.
    
    Returns:
        dmc.Container: The complete dashboard layout
    """
    # Load data summary for filter options
    summary = get_data_summary()
    
    # Get unique values for filters
    years = summary.get("years", [])
    countries = summary.get("countries", [])
    regions = summary.get("regions", [])
    indicators = get_indicator_options()
    
    # Initial data load
    df = load_flfp_data()
    
    return dmc.Container(
        [
            dmc.Grid(
                [
                    # Sidebar column
                    dmc.GridCol(
                        [
                            dmc.Paper(
                                [
                                    dmc.Title("Filters", order=3, mb="md"),
                                    
                                    # Indicator selector
                                    dmc.Text("Indicator", size="sm", fw=500, mb="xs"),
                                    dmc.Select(
                                        id="indicator-selector",
                                        data=indicators,
                                        value=indicators[0]["value"] if indicators else None,
                                        placeholder="Select an indicator",
                                        clearable=False,
                                        searchable=True,
                                        mb="lg"
                                    ),
                                    
                                    # Region multi-select
                                    dmc.Text("Regions", size="sm", fw=500, mb="xs"),
                                    dmc.MultiSelect(
                                        id="region-selector",
                                        data=[{"value": r, "label": r} for r in regions],
                                        placeholder="Select regions",
                                        clearable=True,
                                        searchable=True,
                                        mb="lg"
                                    ),
                                    
                                    # Country multi-select
                                    dmc.Text("Countries", size="sm", fw=500, mb="xs"),
                                    dmc.MultiSelect(
                                        id="country-selector",
                                        data=[{"value": c, "label": c} for c in countries],
                                        placeholder="Select countries",
                                        clearable=True,
                                        searchable=True,
                                        mb="lg"
                                    ),
                                    
                                    # Year range selector
                                    dmc.Text("Year Range", size="sm", fw=500, mb="xs"),
                                    dmc.RangeSlider(
                                        id="year-range-slider",
                                        min=min(years) if years else 2000,
                                        max=max(years) if years else 2023,
                                        value=[min(years) if years else 2000, max(years) if years else 2023],
                                        marks=[
                                            {"value": year, "label": str(year)}
                                            for year in [min(years) if years else 2000, max(years) if years else 2023]]
                                        if years else [],
                                        mb="lg"
                                    ),
                                    
                                ],
                                p="md",
                                withBorder=True,
                                style={"height": "100%"}
                            )
                        ],
                        span=3,
                        style={"height": "100vh", "overflow-y": "auto"}
                    ),
                    
                    # Main content column
                    dmc.GridCol(
                        [
                            # First row: Two equally sized visualizations
                            dmc.Grid(
                                [
                                    dmc.GridCol(
                                        [
                                            dmc.Paper(
                                                [
                                                    html.Div(id="viz-1-container")
                                                ],
                                                p="md",
                                                withBorder=True,
                                                style={"height": "100%"}
                                            )
                                        ],
                                        span=6
                                    ),
                                    dmc.GridCol(
                                        [
                                            dmc.Paper(
                                                [
                                                    html.Div(id="viz-2-container")
                                                ],
                                                p="md",
                                                withBorder=True,
                                                style={"height": "100%"}
                                            )
                                        ],
                                        span=6
                                    ),
                                ],
                                gutter="md",
                                mb="md"
                            ),
                            
                            # Second row: One full-width visualization
                            dmc.Grid(
                                [
                                    dmc.GridCol(
                                        [
                                            dmc.Paper(
                                                [
                                                    html.Div(id="viz-3-container")
                                                ],
                                                p="md",
                                                withBorder=True,
                                                style={"height": "100%"}
                                            )
                                        ],
                                        span=12
                                    ),
                                ],
                                gutter="md"
                            ),
                        ],
                        span=9
                    ),
                ],
                gutter="md"
            ),
            
            # Store filtered data
            dcc.Store(id="filtered-data-store", data=df.to_dict("records")),
        ],
        fluid=True,
        style={"padding": "20px"}
    )

@callback(
    [Output("filtered-data-store", "data"),
     Output("viz-1-container", "children"),
     Output("viz-2-container", "children"),
     Output("viz-3-container", "children")],
    [Input("year-range-slider", "value"),
     Input("region-selector", "value"),
     Input("country-selector", "value"),
     Input("indicator-selector", "value")]
)
def update_dashboard(year_range, selected_regions, selected_countries, selected_indicator):
    """
    Update the dashboard based on filter selections.
    
    Args:
        year_range: List of [min_year, max_year]
        selected_regions: List of selected region names
        selected_countries: List of selected country names
        selected_indicator: Selected indicator column name
        
    Returns:
        tuple: (filtered_data_dict, viz_1, viz_2, viz_3)
    """
    import pandas as pd
    
    # Load and filter data
    df = load_flfp_data()
    
    # Apply filters
    if year_range:
        df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    if selected_regions:
        df = df[df['region'].isin(selected_regions)]
    
    if selected_countries:
        df = df[df['country_name'].isin(selected_countries)]
    
    # Create visualizations with selected indicator
    viz_1 = create_viz_1(df, selected_indicator)
    viz_2 = create_viz_2(df, selected_indicator)
    viz_3 = create_viz_3(df, selected_indicator)
    
    return df.to_dict("records"), viz_1, viz_2, viz_3

