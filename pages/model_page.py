"""
Model exploration page for FLFP predictions
Contains sliders for predictor selection and prediction display
"""

from dash import html, dcc, Input, Output, callback, State, no_update
import dash_mantine_components as dmc
from utils.data_loader import load_flfp_data
from utils.model_utils import (
    load_model_artifacts,
    load_feature_stats,
    get_feature_importance_order,
    make_prediction,
    get_feature_label,
    get_population_slider_marks,
    format_population_value,
    get_region_features,
    get_region_options
)
from components.pred_comparison_map import create_prediction_comparison_viz_1
from components.pred_comparison_hist import create_prediction_comparison_viz_2
from utils.map_data_utils import get_country_features


def create_slider_for_feature(feature_name, stats, default_value=None):
    """
    Create a slider component for a given feature.
    
    Args:
        feature_name (str): Name of the feature
        stats (dict): Feature statistics (min, max, mean)
        default_value: Default value for the slider
        
    Returns:
        html.Div: Slider component
    """
    label = get_feature_label(feature_name)
    
    # Handle income level encoding
    if feature_name == 'income_level_encoded':
        return html.Div([
            dmc.Text(label, size="sm", fw=500, mb="xs"),
            dmc.Slider(
                id=f"slider-{feature_name}",
                min=0,
                max=3,
                value=default_value if default_value is not None else 1,
                step=1,
                marks=[
                    {"value": 0, "label": "Low"},
                    {"value": 1, "label": "Lower-Mid"},
                    {"value": 2, "label": "Upper-Mid"},
                    {"value": 3, "label": "High"},
                ],
                mb="lg"
            )
        ])
    
    # Handle population with log scale
    elif feature_name == 'population_total':
        log_min = stats['min']
        log_max = stats['max']
        log_mean = stats['mean']
        
        default = default_value if default_value is not None else log_mean
        
        # Create logarithmically-spaced marks with actual population labels
        marks = get_population_slider_marks(log_min, log_max, n_marks=5)
        
        return html.Div([
            dmc.Text(f"{label} (logarithmic scale)", size="sm", fw=500, mb="xs"),
            dmc.Text(
                id=f"display-{feature_name}",
                size="xs",
                c="dimmed",
                mb="xs"
            ),
            dmc.Slider(
                id=f"slider-{feature_name}",
                min=log_min,
                max=log_max,
                value=default,
                step=0.01,
                marks=marks,
                mb="lg"
            )
        ], style={"marginBottom": "1rem"})
    
    # Handle regular numeric features
    else:
        min_val = stats['min']
        max_val = stats['max']
        mean_val = stats['mean']
        
        # Determine step size based on feature type
        if 'percent' in feature_name.lower() or feature_name in ['urban_population', 'secondary_enroll_fe', 'services_gdp', 'industry_gdp']:
            step_size = 1
        elif feature_name in ['fertility_rate', 'fertility_adolescent']:
            step_size = 0.1
        elif feature_name in ['rule_of_law']:
            step_size = 0.1
        else:
            step_size = max((max_val - min_val) / 100, 0.1)
        
        default = default_value if default_value is not None else mean_val
        
        # Create marks for slider
        marks = [
            {"value": min_val, "label": f"{min_val:.1f}"},
            {"value": mean_val, "label": f"{mean_val:.1f}"},
            {"value": max_val, "label": f"{max_val:.1f}"},
        ]
        
        return html.Div([
            dmc.Text(label, size="sm", fw=500, mb="xs"),
            dmc.Slider(
                id=f"slider-{feature_name}",
                min=min_val,
                max=max_val,
                value=default,
                step=step_size,
                marks=marks,
                mb="lg"
            )
        ])


def create_model_layout():
    """
    Create the model exploration page layout.
    
    Returns:
        dmc.Container: The complete model page layout
    """
    # Load model artifacts and feature stats
    artifacts = load_model_artifacts()
    feature_stats = load_feature_stats()
    
    # Get features ordered by importance
    ordered_features = get_feature_importance_order()
    
    # Get region features
    region_features = get_region_features()
    
    # Get default values
    default_values = feature_stats.get('default_values', {})
    
    # Create sliders for non-region features
    slider_components = []
    for feature in ordered_features:
        if feature not in region_features:
            if feature in feature_stats:
                default_val = default_values.get(feature)
                slider = create_slider_for_feature(feature, feature_stats[feature], default_val)
                slider_components.append(slider)
    
    # Create region selection radio group
    region_options = get_region_options()
    
    # Determine default region
    default_region = None
    for region in region_features:
        if default_values.get(region, 0) == 1:
            default_region = region
            break
    if default_region is None:
        default_region = region_features[0]  # Fallback to first region
    
    region_selector = html.Div([
        dmc.Text("Region", size="sm", fw=500, mb="xs"),
        dmc.RadioGroup(
            id="radio-region",
            children=dmc.Stack([
                dmc.Radio(opt['label'], value=opt['value'])
                for opt in region_options
            ], gap="xs"),
            value=default_region,
            mb="lg"
        )
    ])
    
    return dmc.Container(
        [
            # Two-column layout with fixed heights
            dmc.Grid(
                [
                    # Left column: Sliders (scrollable, fixed height)
                    dmc.GridCol(
                        [
                            dmc.Paper(
                                [
                                    dmc.Title("Model Predictors", order=4, mb="md"),
                                    dmc.Text(
                                        "Ordered by feature importance",
                                        size="xs",
                                        c="dimmed",
                                        mb="md"
                                    ),
                                    dmc.Stack(
                                        [region_selector] + slider_components,
                                        gap="md"
                                    )
                                ],
                                p="md",
                                withBorder=True,
                                style={
                                    "height": "93vh",
                                    "overflowY": "auto",
                                    "overflowX": "hidden"
                                }
                            )
                        ],
                        span=5
                    ),
                    
                    # Right column: Fixed visualizations (no scroll)
                    dmc.GridCol(
                        [
                            dmc.Stack(
                                [
                                    # Prediction box (15vh)
                                    dmc.Paper(
                                        [
                                            dmc.Title("Predicted FLFP Rate", order=4, mb="sm"),
                                            dmc.Center([
                                                dmc.Text(
                                                    id="prediction-display",
                                                    size="48px",
                                                    fw=700,
                                                    c="blue"
                                                )
                                            ]),
                                            dmc.Text(
                                                "Female Labor Force Participation Rate (%)",
                                                size="xs",
                                                c="dimmed",
                                                ta="center"
                                            )
                                        ],
                                        p="md",
                                        withBorder=True,
                                        style={"height": "15vh"}
                                    ),
                                    
                                    # Choropleth map (45vh)
                                    dmc.Paper(
                                        [
                                            html.Div(
                                                id="pred-comparison-viz-1-container",
                                                style={"height": "100%"}
                                            )
                                        ],
                                        p="md",
                                        withBorder=True,
                                        style={"height": "45vh"}
                                    ),
                                    
                                    # Histogram (30vh)
                                    dmc.Paper(
                                        [
                                            html.Div(
                                                id="pred-comparison-viz-2-container",
                                                style={"height": "100%"}
                                            )
                                        ],
                                        p="md",
                                        withBorder=True,
                                        style={"height": "30vh"}
                                    ),
                                ],
                                gap="md"
                            )
                        ],
                        span=7
                    ),
                ],
                gutter="md"
            ),
            
            # Store for prediction value
            dcc.Store(id="prediction-store", data={"predicted_flfp": 0.0}),
        ],
        fluid=True,
        style={"padding": "20px"}
    )


# Create the prediction callback
def _register_callbacks():
    """Register callbacks for the model page"""
    
    # Get ordered features
    ordered_features = get_feature_importance_order()
    region_features = get_region_features()
    
    # Create Input list dynamically (excluding region features, adding region radio)
    inputs = [Input("radio-region", "value")]
    for feature in ordered_features:
        if feature not in region_features:
            inputs.append(Input(f"slider-{feature}", "value"))
    
    @callback(
        [Output("prediction-display", "children"),
         Output("pred-comparison-viz-1-container", "children"),
         Output("pred-comparison-viz-2-container", "children"),
         Output("prediction-store", "data")],
        inputs
    )
    def update_model_prediction(selected_region, *slider_values):
        """
        Update the model prediction based on slider values.
        
        Args:
            selected_region (str): Selected region from radio group
            *slider_values: Values from all non-region sliders
            
        Returns:
            tuple: (prediction_display, viz_1, viz_2, prediction_data)
        """
        # Map slider values to feature names
        feature_values = {}
        
        # Add region features (one-hot encoding)
        for region in region_features:
            feature_values[region] = 1 if region == selected_region else 0
        
        # Add non-region features
        non_region_features = [f for f in ordered_features if f not in region_features]
        for feature, value in zip(non_region_features, slider_values):
            feature_values[feature] = value
        
        # Make prediction
        predicted_flfp = make_prediction(feature_values)
        
        # Format prediction for display
        prediction_display = f"{predicted_flfp:.1f}%"
        
        # Load real data for comparison
        df = load_flfp_data()
        
        # Create comparison visualizations (placeholders for now)
        viz_1 = create_prediction_comparison_viz_1(predicted_flfp, df)
        viz_2 = create_prediction_comparison_viz_2(predicted_flfp, df)
        
        prediction_data = {"predicted_flfp": predicted_flfp}
        
        return prediction_display, viz_1, viz_2, prediction_data
    
    # Population display callback
    @callback(
        Output("display-population_total", "children"),
        Input("slider-population_total", "value")
    )
    def update_population_display(log_pop):
        """Display the actual population value as user moves slider"""
        if log_pop is None:
            return ""
        return f"Current: {format_population_value(log_pop)}"
    
    # Map click callback - updates all sliders when a country is clicked
    @callback(
        [Output("radio-region", "value")] + 
        [Output(f"slider-{feature}", "value") for feature in ordered_features if feature not in region_features],
        Input("pred-comparison-viz-1", "clickData"),
        prevent_initial_call=True
    )
    def update_sliders_from_map_click(click_data):
        """
        Update all sliders when a country is clicked on the map.
        
        Args:
            click_data: Click data from the choropleth map
            
        Returns:
            tuple: Values for region radio and all feature sliders
        """
        if click_data is None:
            return no_update
        
        # Extract country name from click data
        try:
            country_name = click_data['points'][0]['hovertext']
        except (KeyError, IndexError, TypeError):
            return no_update
        
        # Get features for this country
        country_features = get_country_features(country_name)
        
        if country_features is None:
            return no_update
        
        # Find which region is active
        selected_region = None
        for region in region_features:
            if country_features.get(region, 0) == 1:
                selected_region = region
                break
        
        if selected_region is None:
            selected_region = region_features[0]  # Fallback
        
        # Build output values: region first, then all non-region features in order
        output_values = [selected_region]
        
        non_region_features = [f for f in ordered_features if f not in region_features]
        for feature in non_region_features:
            value = country_features.get(feature, 0)
            output_values.append(value)
        
        return output_values


# Register callbacks when module is imported
_register_callbacks()
