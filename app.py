"""
Main Dash application for FLFP Data Explorer
Two-page app with dashboard and model exploration
"""

import dash
from dash import html, dcc
import dash_mantine_components as dmc

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        # Mantine components come with their own styles
    ],
    suppress_callback_exceptions=True
)

# Set app title
app.title = "FLFP Data Explorer"

# Import page modules to register their callbacks
from pages.dashboard_page import create_dashboard_layout
from pages.model_page import create_model_layout

# Define the app layout
app.layout = dmc.MantineProvider(
    [
        # Navigation tabs
        dmc.Container(
            [
                dmc.Tabs(
                    [
                        dmc.TabsList(
                            [
                                dmc.TabsTab("Dashboard", value="dashboard"),
                                dmc.TabsTab("Model Explorer", value="model"),
                            ],
                            grow=True
                        ),
                        dmc.TabsPanel(
                            create_dashboard_layout(),
                            value="dashboard"
                        ),
                        dmc.TabsPanel(
                            create_model_layout(),
                            value="model"
                        ),
                    ],
                    value="dashboard",
                    id="main-tabs"
                )
            ],
            fluid=True,
            style={"padding": "0px"}
        ),
    ],
    theme={
        "colorScheme": "light",
        "primaryColor": "blue",
    }
)

if __name__ == "__main__":
    app.run(debug=True, port=8050)

