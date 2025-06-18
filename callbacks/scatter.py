import os
import pandas as pd
from dash import html, Input, Output, State, callback_context, no_update
import plotly.express as px
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from utils.image import encode_image

# Directory where CSVs and images are stored
image_directory = './utils/'

# Cache for file modification times to optimize refresh
file_mod_times = {}

def check_file_mod_time(filename: str) -> float:
    """Return the last modification time for a given file."""
    csv_path = os.path.join(image_directory, filename)
    return os.path.getmtime(csv_path)

def load_csv_to_df(filename: str) -> pd.DataFrame:
    """Load CSV file into a DataFrame with proper preprocessing."""
    csv_path = os.path.join(image_directory, filename)
    df_new = pd.read_csv(csv_path, delim_whitespace=True, header=None)
    df_new.columns = ['col1', 'col2', 'MJD', 'Burst_DM', 'col5', 'S/N',
                      'col7', 'col8', 'ImagePath', 'col10', 'col11']
    # Extract just the image filename from the full path
    df_new['ImageFilename'] = df_new['ImagePath'].apply(lambda x: os.path.basename(x))
    return df_new

def register_callbacks(app):
    @app.callback(
        Output('csv-selector', 'options'),
        Input('refresh-files-interval', 'n_intervals')
    )
    def refresh_csv_options(n):
        # List CSV and .cands files in utils directory
        files = [f for f in os.listdir(image_directory) if f.endswith('.csv') or f.endswith('.cands')]
        return [{'label': f, 'value': f} for f in files]

    @app.callback(
        Output('dynamic-content', 'children'),
        Output('x-axis', 'options'),
        Output('y-axis', 'options'),
        Output('x-axis', 'value'),
        Output('y-axis', 'value'),
        Output('main-table', 'data'),
        Output('main-table', 'columns'),
        Output('interval-component', 'interval'),
        Output('last-modified-timestamp', 'data'),
        Input('csv-selector', 'value'),
        Input('interval-component', 'n_intervals'),
        Input('auto-refresh-toggle', 'value'),
        Input('interval-selector', 'value'),
        State('last-modified-timestamp', 'data'),
    )
    def update_data_and_controls(selected_csv, n_intervals, auto_refresh_values, interval_value, last_mod_time):
        if not selected_csv:
            # No CSV selected: reset everything
            return (
                html.Div("Please select a CSV."),
                [], [], None, None,
                [], [],
                5000,
                ""
            )

        # Get current file modification time
        try:
            current_mod_time = check_file_mod_time(selected_csv)
        except Exception as e:
            return (html.Div(f"Error loading file: {e}"), [], [], None, None, [], [], 5000, "")

        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        # Auto-refresh logic: only update if file changed
        if triggered_id == 'interval-component':
            if not auto_refresh_values or 'enabled' not in auto_refresh_values:
                raise PreventUpdate
            if last_mod_time and float(last_mod_time) == current_mod_time:
                raise PreventUpdate

        # Load CSV data
        try:
            df_new = load_csv_to_df(selected_csv)
        except Exception as e:
            return (html.Div(f"Error parsing file: {e}"), [], [], None, None, [], [], 5000, "")

        # Update cache with latest mod time
        file_mod_times[selected_csv] = current_mod_time

        # Columns for dropdowns and table
        numeric_cols = [col for col in ['MJD', 'Burst_DM', 'S/N'] if col in df_new and pd.api.types.is_numeric_dtype(df_new[col])]
        visible_cols = [col for col in ['MJD', 'Burst_DM', 'S/N', 'ImageFilename'] if col in df_new]

        options = [{'label': col, 'value': col} for col in numeric_cols]

        # Defaults for x and y axis dropdowns
        x_val = numeric_cols[0] if numeric_cols else None
        y_val = numeric_cols[1] if len(numeric_cols) > 1 else (numeric_cols[0] if numeric_cols else None)

        # Prepare table data and columns
        table_data = df_new[visible_cols].to_dict('records')
        table_columns = [{"name": col, "id": col} for col in visible_cols]

        return (
            html.Div(f"Loaded: {selected_csv}"),
            options,
            options,
            x_val,
            y_val,
            table_data,
            table_columns,
            interval_value or 5000,
            current_mod_time
        )

    @app.callback(
        Output("scatter-plot", "figure"),
        Input("x-axis", "value"),
        Input("y-axis", "value"),
        Input("x-scale", "value"),
        Input("y-scale", "value"),
        Input('main-table', 'derived_virtual_data'),  # filtered data if any
        State('main-table', 'data'),  # fallback to full data
    )
    def update_figure(x_col, y_col, x_scale, y_scale, table_data_virtual, table_data_fallback):
        table_data = table_data_virtual if table_data_virtual is not None else table_data_fallback

        if not table_data:
            return px.scatter(title="No data to plot.")

        df = pd.DataFrame(table_data)

        if x_col not in df or y_col not in df or 'S/N' not in df:
            return px.scatter(title="Invalid or missing columns.")

        fig = px.scatter(df, x=x_col, y=y_col, size='S/N', size_max=20)

        fig.update_traces(
            hoverinfo="none",
            hovertemplate=None,
            customdata=df[[col for col in ['ImageFilename', 'MJD', 'Burst_DM'] if col in df]].values
        )
        fig.update_layout(xaxis_type=x_scale, yaxis_type=y_scale)

        return fig

    @app.callback(
        Output('clicked-point', 'data'),
        Output('click-counter', 'data'),
        Input('scatter-plot', 'clickData'),
        Input('main-table', 'selected_rows'),
        Input('close-popup', 'n_clicks'),
        State('main-table', 'data'),
        State('click-counter', 'data'),
    )
    def update_clicked_point(clickData, selected_rows, close_clicks, table_data, click_counter):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'scatter-plot' and clickData:
            return clickData["points"][0], (click_counter or 0) + 1
        elif trigger == 'main-table' and selected_rows:
            try:
                df = pd.DataFrame(table_data)
                row = df.iloc[selected_rows[0]]
                customdata = [row.get(k, '') for k in ['ImageFilename', 'MJD', 'Burst_DM']]
                return {"customdata": customdata}, (click_counter or 0) + 1
            except Exception:
                return no_update, no_update
        elif trigger == 'close-popup':
            return None, 0
        return no_update, no_update

    @app.callback(
        Output('image-popup', 'children'),
        Output('image-popup', 'style'),
        Input('clicked-point', 'data'),
        Input('click-counter', 'data'),
    )
    def display_click_popup(point_data, _):
        if not point_data or 'customdata' not in point_data:
            return "", {'display': 'none'}

        image_filename, mjd, burst_dm = point_data["customdata"]
        image_path = os.path.join(image_directory, image_filename)
        encoded = encode_image(image_path)

        if not encoded:
            return "", {'display': 'none'}

        modal = dbc.Modal([
            dbc.ModalHeader(
                dbc.Button('✖', id='close-popup', n_clicks=0, color='link',
                           style={'fontSize': '20px', 'float': 'right'}),
                close_button=False
            ),
            dbc.ModalBody([
                html.Img(src=f"data:image/png;base64,{encoded}", style={
                    "width": "100%", "height": "auto", "border": "2px solid #ccc", "display": "block", "margin": "0 auto"
                }),
                html.P(f"MJD: {mjd}", style={"fontSize": "12px", "marginTop": "10px"}),
                html.P(f"Burst DM: {burst_dm}", style={"fontSize": "12px"}),
                html.A("View Full Image", href=f"/assets/Images/{image_filename}", target="_blank", style={
                    "display": "block", "marginTop": "12px", "textAlign": "center", "color": "#007bff",
                    "fontWeight": "bold", "textDecoration": "underline", "fontSize": "14px"
                })
            ])
        ], id='image-modal', is_open=True, centered=True, backdrop="static", keyboard=False)

        return modal, {'display': 'block'}
