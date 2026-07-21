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

# Directory where .cands files and PNGs are stored
image_directory = '/data'

# Cache for file modification times to optimize refresh
file_mod_times = {}

# Column names for the PulsarX .cands data rows, in file order
DATA_COLUMNS = [
    'id', 'dm_old', 'dm_new', 'dm_err', 'dist_ymw16',
    'f0_old', 'f0_new', 'f0_err', 'f1_old', 'f1_new', 'f1_err',
    'acc_old', 'acc_new', 'acc_err', 'S/N', 'S/N_new'
]

# Metadata keys found in the '#Key value' header lines at the top of the file
HEADER_KEYS = [
    'Filename', 'Telescope', 'Source_name', 'Beam', 'Date',
    'RA', 'DEC', 'GL', 'GB', 'MaxDM_YMW16', 'Pepoch'
]

# Friendlier axis labels for the plot / table
AXIS_LABEL_MAP = {
    'id': 'Candidate ID',
    'dm_old': 'DM old (pc cm⁻³)',
    'dm_new': 'DM new (pc cm⁻³)',
    'dm_err': 'DM error (pc cm⁻³)',
    'dist_ymw16': 'Distance YMW16 (pc)',
    'f0_old': 'F0 old (Hz)',
    'f0_new': 'F0 new (Hz)',
    'f0_err': 'F0 error (Hz)',
    'f1_old': 'F1 old (Hz/s)',
    'f1_new': 'F1 new (Hz/s)',
    'f1_err': 'F1 error (Hz/s)',
    'acc_old': 'Acceleration old (m/s²)',
    'acc_new': 'Acceleration new (m/s²)',
    'acc_err': 'Acceleration error (m/s²)',
    'S/N': 'S/N (old)',
    'S/N_new': 'S/N (new)',
}


def check_file_mod_time(filename: str) -> float:
    csv_path = os.path.join(image_directory, filename)
    return os.path.getmtime(csv_path)


def parse_cands_header(filepath: str) -> dict:
    """Parse the leading '#Key value' comment lines of a PulsarX .cands file."""
    meta = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.startswith('#'):
                break
            content = line[1:].strip()
            if not content:
                continue
            parts = content.split(None, 1)
            key = parts[0]
            if key in HEADER_KEYS:
                meta[key] = parts[1].strip() if len(parts) > 1 else ''
    return meta


def load_csv_to_df(filename: str) -> pd.DataFrame:
    """
    Load a PulsarX .cands file into a DataFrame.

    The file has a block of '#Key value' header/metadata lines (including a
    '#id dm_old dm_new ...' column-name line), followed by whitespace-delimited
    data rows. The candidate's row 'id' maps to a PNG named
    '_{Date}_{Beam}_{id:05d}.png' living alongside the .cands file.
    """
    csv_path = os.path.join(image_directory, filename)
    meta = parse_cands_header(csv_path)

    df_new = pd.read_csv(
        csv_path,
        comment='#',
        sep=r'\s+',
        header=None,
        names=DATA_COLUMNS,
        engine='python'
    )

    df_new['id'] = df_new['id'].astype(int)

    date_str = meta.get('Date', '')
    beam_str = meta.get('Beam', '')
    df_new['ImageFilename'] = df_new['id'].apply(
        lambda i: f"_{date_str}_{beam_str}_{i:05d}.png"
    )

    # Per-file metadata, attached as constant columns (handy for reference/labeling)
    df_new['Source_name'] = meta.get('Source_name', '')
    df_new['Beam'] = beam_str
    df_new['MJD'] = date_str

    return df_new


def write_labeled_cands(original_file, label_store):
    input_path = os.path.join(image_directory, original_file)
    df = load_csv_to_df(original_file)

    df['ML_Label'] = np.nan
    for idx, row in df.iterrows():
        key = row['ImageFilename']
        if key in label_store:
            df.at[idx, 'ML_Label'] = label_store[key]

    # Preserve the original '#...' header lines verbatim
    header_lines = []
    with open(input_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                header_lines.append(line.rstrip('\n'))
            else:
                break

    output_file = original_file.replace('.cands', '_labeled.cands')
    output_path = os.path.join(image_directory, output_file)

    out_cols = DATA_COLUMNS + ['ML_Label']

    with open(output_path, 'w') as f:
        for line in header_lines:
            f.write(line + '\n')
        df[out_cols].to_csv(f, sep='\t', header=False, index=False, na_rep='NaN')


def register_callbacks(app):
    @app.callback(
        Output('csv-selector', 'options'),
        Input('refresh-files-interval', 'n_intervals')
    )
    def refresh_csv_options(n):
        files = [f for f in os.listdir(image_directory) if f.endswith('.cands')]
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
                html.Div("Please select a .cands file."), [], [], 5000, "",
                [], [], None, None, "", "", False
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

        numeric_cols = [col for col in DATA_COLUMNS if col in df_new and pd.api.types.is_numeric_dtype(df_new[col])]
        visible_cols = [c for c in (DATA_COLUMNS + ['ImageFilename']) if c in df_new]

        axis_options = [{'label': AXIS_LABEL_MAP.get(col, col), 'value': col} for col in numeric_cols]

        # Default view: candidate S/N vs DM (prefer the refined/'new' values)
        if 'dm_new' in numeric_cols:
            x_val = 'dm_new'
        elif 'dm_old' in numeric_cols:
            x_val = 'dm_old'
        else:
            x_val = numeric_cols[0] if numeric_cols else None

        if 'S/N_new' in numeric_cols:
            y_val = 'S/N_new'
        elif 'S/N' in numeric_cols:
            y_val = 'S/N'
        else:
            y_val = numeric_cols[1] if len(numeric_cols) > 1 else x_val

        table_data = df_new[visible_cols].to_dict('records')
        table_columns = [
            {"name": AXIS_LABEL_MAP.get(col, col), "id": col,
             "type": "numeric" if col in numeric_cols else "text"}
            for col in visible_cols
        ]

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
            (interval_value or 5) * 1000,
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
        Input('ml-label-store', 'data'),  # <- make Input
        State('main-table', 'data')
    )
    def update_figure(x_col, y_col, x_scale, y_scale, table_data_virtual, label_store, table_data_fallback):
        table_data = table_data_virtual if table_data_virtual is not None else table_data_fallback
        label_store = label_store or {}

        if not table_data or not x_col or not y_col:
            return px.scatter(title="No data to plot.")

        df = pd.DataFrame(table_data)
        if x_col not in df or y_col not in df:
            return px.scatter(title="Invalid or missing columns.")

        sn_col = 'S/N_new' if 'S/N_new' in df else ('S/N' if 'S/N' in df else y_col)
        sn = pd.to_numeric(df[sn_col], errors='coerce').fillna(0)
        sn_scaled = 10 + 15 * (sn - sn.min()) / (sn.max() - sn.min() + 1e-9)

        # Marker color and symbol by ML label
        colors, symbols = [], []
        for _, row in df.iterrows():
            key = row.get('ImageFilename', '')
            label = label_store.get(key, np.nan)
            if label == 0:
                colors.append('red')
                symbols.append('x')
            elif label == 1:
                colors.append('green')
                symbols.append('circle')
            else:
                colors.append('blue')
                symbols.append('circle-open')

        x_label = AXIS_LABEL_MAP.get(x_col, x_col)
        y_label = AXIS_LABEL_MAP.get(y_col, y_col)

        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.8, 0.2],
            shared_yaxes=True,
            horizontal_spacing=0.02,
            specs=[[{"type": "scatter"}, {"type": "histogram"}]]
        )

        # Fixed customdata schema used for click-to-popup matching
        for col in ['ImageFilename', 'id', 'dm_new', 'S/N_new']:
            if col not in df:
                df[col] = ''

        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                marker=dict(
                    size=sn_scaled,
                    color=colors,
                    symbol=symbols,
                    opacity=0.7,
                    line=dict(width=1, color='black')
                ),
                customdata=df[['ImageFilename', 'id', 'dm_new', 'S/N_new']].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Candidate ID: %{customdata[1]}<br>"
                    "DM: %{customdata[2]}<br>"
                    "S/N: %{customdata[3]}<extra></extra>"
                ),
                showlegend=False,
            ),
            row=1, col=1
        )

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
            xaxis_title=x_label,
            yaxis_title=y_label,
            hovermode="closest",
            margin=dict(l=50, r=20, t=40, b=40)
        )

        return fig

    @app.callback(
        Output('clicked-point', 'data'),
        Output('click-counter', 'data'),
        Input('scatter-plot', 'clickData'),
        Input('main-table', 'active_cell'),
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
                customdata = [row.get(k, '') for k in ['ImageFilename', 'id', 'dm_new', 'S/N_new']]
                return {"customdata": customdata}, (click_counter or 0) + 1
            except Exception as e:
                print(f"Error accessing row: {e}")
                return no_update, no_update
        elif trigger == 'close-popup':
            return None, 0
        return no_update, no_update

    @app.callback(
        Output('ml-label-store', 'data'),
        Output('label-rfi', 'color'),
        Output('label-rfi', 'outline'),
        Output('label-pulse', 'color'),
        Output('label-pulse', 'outline'),
        Input('label-rfi', 'n_clicks'),
        Input('label-pulse', 'n_clicks'),
        State('clicked-point', 'data'),
        State('ml-label-store', 'data'),
        prevent_initial_call=True
    )
    def update_ml_labels(rfi_clicks, pulse_clicks, point_data, label_store):
        if not point_data or 'customdata' not in point_data:
            raise PreventUpdate
        key = point_data['customdata'][0]  # ImageFilename uniquely identifies a candidate
        label_store = label_store or {}
        ctx = callback_context
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'label-rfi':
            label_store[key] = 0
        elif trigger == 'label-pulse':
            label_store[key] = 1

        rfi_color, rfi_outline = ('danger', False) if label_store.get(key) == 0 else ('danger', True)
        pulse_color, pulse_outline = ('success', False) if label_store.get(key) == 1 else ('success', True)

        return label_store, rfi_color, rfi_outline, pulse_color, pulse_outline

    @app.callback(
        Output('image-modal', 'is_open'),
        Output('popup-image', 'src'),
        Output('popup-id', 'children'),
        Output('popup-dm', 'children'),
        Output('popup-sn', 'children'),
        Input('clicked-point', 'data'),
        Input('click-counter', 'data'),
        Input('close-popup', 'n_clicks'),
        State('image-modal', 'is_open'),
        State('ml-label-store', 'data'),
        State('csv-selector', 'value'),
    )
    def toggle_modal(point_data, click_counter, close_clicks, is_open, label_store, selected_csv):
        ctx = callback_context
        if not ctx.triggered:
            return False, None, "", "", ""
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'close-popup':
            if label_store and selected_csv and selected_csv.endswith('.cands'):
                write_labeled_cands(selected_csv, label_store)
            return False, None, "", "", ""

        if trigger in ['clicked-point', 'click-counter'] and point_data and 'customdata' in point_data:
            image_filename, cand_id, dm_new, sn_new = point_data["customdata"]
            image_path = os.path.join(image_directory, image_filename)
            encoded = encode_image(image_path)
            if not encoded:
                return False, None, "", "", ""
            src = f"data:image/png;base64,{encoded}"
            id_text = f"Candidate ID: {cand_id}"
            dm_text = f"DM: {dm_new} pc cm⁻³"
            sn_text = f"S/N: {sn_new}"
            return True, src, id_text, dm_text, sn_text

        return is_open, no_update, no_update, no_update, no_update
