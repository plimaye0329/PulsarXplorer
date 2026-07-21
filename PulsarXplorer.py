import argparse
from dash import Dash, Output, Input
from layout import create_layout
from callbacks import register_all_callbacks
import dash_bootstrap_components as dbc

# --- Argument parser for selecting the port ---
parser = argparse.ArgumentParser(description='Run the PulsarXplorer Dash app.')
parser.add_argument('--port', type=int, default=8050, help='Port number to run the server on')
args = parser.parse_args()

# --- Dash App Setup ---
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
app.title = "PulsarXplorer"
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

# Register callbacks without preloaded DataFrame
register_all_callbacks(app)

# --- Run the app on specified port ---
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=args.port)
