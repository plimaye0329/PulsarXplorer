import os
import pandas as pd
import numpy as np
from dash import html, Input, Output, State, callback_context, no_update
import plotly.express as px
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from utils.image import encode_image
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Directory where CSVs and images are stored
image_directory = '/data'

# Cache for file modification times to optimize refresh
file_mod_times = {}

def check_file_mod_time(filename: str) -> float:
    csv_path = os.path.join(image_directory, filename)
    return os.path.getmtime(csv_path)

def load_csv_to_df(filename: str) -> pd.DataFrame:
    csv_path = os.path.join(image_directory, filename)
    df_new = pd.read_csv(csv_path, delim_whitespace=True, header=None)
    df_new.columns = ['col1', 'col2', 'MJD', 'Burst_DM', 'width', 'S/N',
                      'col7', 'col8', 'ImagePath', 'col10', 'col11']


    df_new['ImageFilename'] = df_new['ImagePath'].apply(lambda x: os.path.basename(x))
    return df_new

def register_callbacks(app):
    @app.callback(
        Output('csv-selector', 'options'),
        Input('refresh-files-interval', 'n_intervals')
    )
    def refresh_csv_options(n):
        files = [f for f in os.listdir(image_directory) if f.endswith('.csv') or f.endswith('.cands')]
        return [{'label': f, 'value': f} for f in files]

    @app.callback(
        Output('dynamic-content', 'children'),
        Output('main-table', 'data'),
        Output('main-table', 'columns'),
        Output('interval-component', 'interval'),
        Output('last-modified-timestamp', 'data'),
        Output('x-axis', 'options'),
        Output('y-axis', 'options'),
        Output('x-axis', 'value'),
        Output('y-axis', 'value'),
        Output('file-load-alert', 'children'),
        Output('file-load-alert', 'color'),
        Output('file-load-alert', 'is_open'),
        Input('csv-selector', 'value'),
        Input('interval-component', 'n_intervals'),
        Input('auto-refresh-toggle', 'value'),
        Input('interval-input', 'value'),
        State('last-modified-timestamp', 'data'),
    )
    def update_data_and_controls(selected_csv, n_intervals, auto_refresh_values, interval_value, last_mod_time):
        if not selected_csv:
            return (
                html.Div("Please select a CSV."), [], [], 5000, "",
                [], [], None, None, "","", False
            )

        try:
            current_mod_time = check_file_mod_time(selected_csv)
        except Exception as e:
            return (html.Div(f"Error loading file: {e}"), [], [], 5000, "", [], [], None, None, "", "", False)

        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        if triggered_id == 'interval-component':
            if not auto_refresh_values or 'enabled' not in auto_refresh_values:
                raise PreventUpdate
            if last_mod_time and float(last_mod_time) == current_mod_time:
                raise PreventUpdate

        try:
            df_new = load_csv_to_df(selected_csv)
        except Exception as e:
            return (html.Div(f"Error parsing file: {e}"), [], [], 5000, "", [], [], None, None, "", "", False)

        file_mod_times[selected_csv] = current_mod_time

        numeric_cols = [col for col in ['MJD', 'Burst_DM', 'width', 'S/N'] if col in df_new and pd.api.types.is_numeric_dtype(df_new[col])]
        visible_cols = [col for col in ['MJD', 'Burst_DM', 'width', 'S/N', 'ImageFilename'] if col in df_new]

        axis_options = [{'label': col, 'value': col} for col in numeric_cols]
        x_val = 'MJD' if 'MJD' in numeric_cols else (numeric_cols[0] if numeric_cols else None)
        y_val = 'Burst_DM' if 'Burst_DM' in numeric_cols else (numeric_cols[1] if len(numeric_cols) > 1 else x_val)

        table_data = df_new[visible_cols].to_dict('records')
        table_columns = [{"name": col, "id": col, "type": "numeric" if col in numeric_cols else "text"} for col in visible_cols]

        if triggered_id == 'csv-selector':
            alert_msg = f"Successfully loaded {selected_csv}"
            alert_color = "success"
            alert_open = True
        else:
            alert_msg = ""
            alert_color = ""
            alert_open = False

        return (
            html.Div(f"Loaded: {selected_csv}"),
            table_data,
            table_columns,
            (interval_value or 5)*1000,
            current_mod_time,
            axis_options,
            axis_options,
            x_val,
            y_val,
            alert_msg,
            alert_color,
            alert_open
        )

    @app.callback(
        Output("scatter-plot", "figure"),
        Input("x-axis", "value"),
        Input("y-axis", "value"),
        Input("x-scale", "value"),
        Input("y-scale", "value"),
        Input('main-table', 'derived_virtual_data'),
        State('main-table', 'data'),
    )
    def update_figure(x_col, y_col, x_scale, y_scale, table_data_virtual, table_data_fallback):
        table_data = table_data_virtual if table_data_virtual is not None else table_data_fallback

        if not table_data:
            return px.scatter(title="No data to plot.")

        df = pd.DataFrame(table_data)

        if x_col not in df or y_col not in df or 'S/N' not in df:
            return px.scatter(title="Invalid or missing columns.")
    
        axis_label_map = {
            'MJD': 'MJD',
            'Burst_DM': 'DM (pc cm⁻³)',
            'width': 'Width (ms)',
            'S/N': 'S/N Ratio',
        }

    # Create subplots: main plot and vertical histogram
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.8, 0.2],
            shared_yaxes=True,
            horizontal_spacing=0.02,
            specs=[[{"type": "scatter"}, {"type": "histogram"}]]
        )
        sn = df['S/N']
        sn_scaled = 10 + 15 * (sn - sn.min()) / (sn.max() - sn.min() + 1e-9)

    # Main scatter plot
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                
                marker=dict(
                    size=sn_scaled,
                    color=df['width'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Width (ms)")
                ),
                customdata=df[[col for col in ['ImageFilename', 'MJD', 'Burst_DM'] if col in df]].values,
                hovertemplate=None,
                showlegend=False,
            ),
            row=1, col=1
        )

    # Histogram for Y-axis
        fig.add_trace(
            go.Histogram(
                y=df[y_col],
                nbinsy=30,
                marker=dict(color='gray'),
                showlegend=False
            ),
            row=1, col=2
        )

        fig.update_layout(
            xaxis_type=x_scale,
            yaxis_type=y_scale,
            xaxis_title=axis_label_map.get(x_col, x_col),
            yaxis_title=axis_label_map.get(y_col, y_col),
            hovermode="closest",
            margin=dict(l=50, r=20, t=40, b=40),
        )

        return fig

    @app.callback(
        Output('clicked-point', 'data'),
        Output('click-counter', 'data'),
        Input('scatter-plot', 'clickData'),
        Input('main-table','active_cell'),
        Input('close-popup', 'n_clicks'),
        State('main-table', 'derived_virtual_data'),
        State('click-counter', 'data'),
    )
    def update_clicked_point(clickData, active_cell, close_clicks, virtual_data, click_counter):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update

        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'scatter-plot' and clickData:
            return clickData["points"][0], (click_counter or 0) + 1

        elif trigger == 'main-table' and active_cell:
            if not virtual_data or active_cell.get('row') is None:
                return no_update, no_update
            try:
                row = virtual_data[active_cell['row']]
                customdata = [row.get(k, '') for k in ['ImageFilename', 'MJD', 'Burst_DM']]
                return {"customdata": customdata}, (click_counter or 0) + 1
            except Exception as e:
                print(f"Error accessing row: {e}")
                return no_update, no_update

        elif trigger == 'close-popup':
            return None, 0

        return no_update, no_update
    
    

    @app.callback(
        Output('image-modal', 'is_open'),
        Output('popup-image', 'src'),
        Output('popup-mjd', 'children'),
        Output('popup-dm', 'children'),
        Input('clicked-point', 'data'),
        Input('click-counter', 'data'),
        Input('close-popup', 'n_clicks'),
        State('image-modal', 'is_open'),
    )
    def toggle_modal(point_data, click_counter, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return False, None, "", ""

        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        # Close modal on close button click
        if trigger == 'close-popup':
            return False, None, "", ""

        # Show modal on scatter-plot or table click
        if trigger in ['clicked-point', 'click-counter'] and point_data and 'customdata' in point_data:
            image_filename, mjd, burst_dm = point_data["customdata"]
            image_path = os.path.join(image_directory, image_filename)
            encoded = encode_image(image_path)
            if not encoded:
                return False, None, "", ""

            src = f"data:image/png;base64,{encoded}"
            mjd_text = f"MJD: {mjd}"
            dm_text = f"Burst DM: {burst_dm}"
            return True, src, mjd_text, dm_text

        return is_open, no_update, no_update, no_update


