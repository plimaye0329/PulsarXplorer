from dash import Dash, Output, Input  # Add Output, Input import
from layout import create_layout
from utils.data import load_data
from callbacks import register_all_callbacks
import dash_bootstrap_components as dbc


df = load_data()

app = Dash(external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)    
app.layout = create_layout()
app.clientside_callback(
    """
    function(n_clicks) {
        // When close-popup is clicked, clear clickData
        if (n_clicks) {
            return null;
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('scatter-plot', 'clickData'),
    Input('close-popup', 'n_clicks'),
    prevent_initial_call=True
)


register_all_callbacks(app, df)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)

