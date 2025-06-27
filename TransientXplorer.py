from dash import Dash, Output, Input
from layout import create_layout
from callbacks import register_all_callbacks  # no df here anymore
import dash_bootstrap_components as dbc

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

# Register callbacks WITHOUT passing a preloaded dataframe
register_all_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)


