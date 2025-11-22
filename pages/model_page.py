"""
Model exploration page for FLFP predictions
Contains sliders for predictor selection and prediction display
"""

from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc
from utils.data_loader import load_flfp_data
from components.pred_comparison_viz_1 import create_prediction_comparison_viz_1
from components.pred_comparison_viz_2 import create_prediction_comparison_viz_2

def create_model_layout():
    """
    Create the model exploration page layout.
    
    Returns:
        dmc.Container: The complete model page layout
    """
    # Load data for reference
    df = load_flfp_data()
    
    # Get numeric columns that might be predictors
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Remove year and other non-predictor columns
    predictor_candidates = [col for col in numeric_cols 
                           if col not in ['year'] and not col.startswith('flfp')]
    
    # Default predictor values (to be updated based on actual model)
    # These are placeholders - the team will need to set appropriate ranges
    default_predictors = {
        'gdp_per_capita_const': 5000,
        'fertility_rate': 2.5,
        'secondary_enroll_fe': 50,
        'urban_population': 50,
    }
    
    return dmc.Container(
        [
            # Top half: Prediction display and comparison visualizations
            dmc.Grid(
                [
                    # Prediction box
                    dmc.GridCol(
                        [
                            dmc.Paper(
                                [
                                    dmc.Title("Predicted Probability", order=3, mb="md"),
                                    dmc.Text(
                                        id="prediction-display",
                                        size="xl",
                                        fw=700,
                                        ta="center",
                                        style={"fontSize": "48px", "color": "#228be6"}
                                    ),
                                    dmc.Text(
                                        "FLFP Rate",
                                        size="sm",
                                        c="dimmed",
                                        ta="center",
                                        mt="xs"
                                    )
                                ],
                                p="xl",
                                withBorder=True,
                                style={"height": "100%", "textAlign": "center"}
                            )
                        ],
                        span=4
                    ),
                    
                    # First comparison visualization
                    dmc.GridCol(
                        [
                            dmc.Paper(
                                [
                                    html.Div(id="pred-comparison-viz-1-container")
                                ],
                                p="md",
                                withBorder=True,
                                style={"height": "100%"}
                            )
                        ],
                        span=4
                    ),
                    
                    # Second comparison visualization
                    dmc.GridCol(
                        [
                            dmc.Paper(
                                [
                                    html.Div(id="pred-comparison-viz-2-container")
                                ],
                                p="md",
                                withBorder=True,
                                style={"height": "100%"}
                            )
                        ],
                        span=4
                    ),
                ],
                gutter="md",
                mb="md"
            ),
            
            # Bottom half: Sliders for predictor selection
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Paper(
                                [
                                    dmc.Title("Model Predictors", order=3, mb="md"),
                                    
                                    # Dynamic sliders will be created here
                                    # For now, we'll create placeholders for common predictors
                                    html.Div(id="predictor-sliders-container"),
                                    
                                    # Placeholder sliders (to be replaced with dynamic generation)
                                    dmc.Stack(
                                        [
                                            dmc.Text("GDP per Capita (constant)", size="sm", fw=500, mb="xs"),
                                            dmc.Slider(
                                                id="slider-gdp-per-capita",
                                                min=0,
                                                max=100000,
                                                value=5000,
                                                step=100,
                                                marks=[
                                                    {"value": 0, "label": "0"},
                                                    {"value": 25000, "label": "25k"},
                                                    {"value": 50000, "label": "50k"},
                                                    {"value": 75000, "label": "75k"},
                                                    {"value": 100000, "label": "100k"},
                                                ],
                                                mb="lg"
                                            ),
                                            
                                            dmc.Text("Fertility Rate", size="sm", fw=500, mb="xs"),
                                            dmc.Slider(
                                                id="slider-fertility-rate",
                                                min=0,
                                                max=10,
                                                value=2.5,
                                                step=0.1,
                                                marks=[
                                                    {"value": 0, "label": "0"},
                                                    {"value": 2.5, "label": "2.5"},
                                                    {"value": 5, "label": "5"},
                                                    {"value": 7.5, "label": "7.5"},
                                                    {"value": 10, "label": "10"},
                                                ],
                                                mb="lg"
                                            ),
                                            
                                            dmc.Text("Female Secondary Enrollment", size="sm", fw=500, mb="xs"),
                                            dmc.Slider(
                                                id="slider-secondary-enroll",
                                                min=0,
                                                max=100,
                                                value=50,
                                                step=1,
                                                marks=[
                                                    {"value": 0, "label": "0%"},
                                                    {"value": 25, "label": "25%"},
                                                    {"value": 50, "label": "50%"},
                                                    {"value": 75, "label": "75%"},
                                                    {"value": 100, "label": "100%"},
                                                ],
                                                mb="lg"
                                            ),
                                            
                                            dmc.Text("Urban Population %", size="sm", fw=500, mb="xs"),
                                            dmc.Slider(
                                                id="slider-urban-pop",
                                                min=0,
                                                max=100,
                                                value=50,
                                                step=1,
                                                marks=[
                                                    {"value": 0, "label": "0%"},
                                                    {"value": 25, "label": "25%"},
                                                    {"value": 50, "label": "50%"},
                                                    {"value": 75, "label": "75%"},
                                                    {"value": 100, "label": "100%"},
                                                ],
                                                mb="lg"
                                            ),
                                        ],
                                        gap="md"
                                    )
                                ],
                                p="md",
                                withBorder=True
                            )
                        ],
                        span=12
                    ),
                ],
                gutter="md"
            ),
            
            # Store for prediction value
            dcc.Store(id="prediction-store", data={"predicted_probability": 0.0}),
        ],
        fluid=True,
        style={"padding": "20px"}
    )

@callback(
    [Output("prediction-display", "children"),
     Output("pred-comparison-viz-1-container", "children"),
     Output("pred-comparison-viz-2-container", "children"),
     Output("prediction-store", "data")],
    [Input("slider-gdp-per-capita", "value"),
     Input("slider-fertility-rate", "value"),
     Input("slider-secondary-enroll", "value"),
     Input("slider-urban-pop", "value")]
)
def update_model_prediction(gdp, fertility, secondary_enroll, urban_pop):
    """
    Update the model prediction based on slider values.
    This is a placeholder - the actual model will be implemented later.
    
    Args:
        gdp: GDP per capita value
        fertility: Fertility rate value
        secondary_enroll: Secondary enrollment value
        urban_pop: Urban population percentage
        
    Returns:
        tuple: (prediction_display, viz_1, viz_2, prediction_data)
    """
    # Placeholder prediction (to be replaced with actual model)
    # For now, just a simple calculation to show the framework works
    predicted_probability = 0.0  # Placeholder - will be calculated by actual model
    
    # Format prediction for display
    prediction_display = f"{predicted_probability:.1f}%"
    
    # Load real data for comparison
    df = load_flfp_data()
    
    # Create comparison visualizations
    viz_1 = create_prediction_comparison_viz_1(predicted_probability, df)
    viz_2 = create_prediction_comparison_viz_2(predicted_probability, df)
    
    prediction_data = {"predicted_probability": predicted_probability}
    
    return prediction_display, viz_1, viz_2, prediction_data

