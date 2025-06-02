from dash import Input, Output, State, callback_context, no_update, html, dcc, dash_table
import plotly.express as px
import os
import pandas as pd
from utils.image import encode_image
import dash_bootstrap_components as dbc

image_directory = 'assets/Images'



def get_numeric_columns(df):
    # Helper to get numeric columns for dropdowns
    return [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

def generate_controls_and_plot(df):
    print(df.dtypes)
    allowed = ['MJD', 'Burst_DM', 'S/N']
    numeric_columns = [col for col in allowed if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    visible_columns = [col for col in ['MJD', 'Burst_DM', 'S/N', 'ImageFilename'] if col in df.columns]
    return [
        dcc.Store(id='data-store', data=df.to_json(date_format='iso', orient='split')),
        # Controls for plot axes and scales
        dbc.Row([
            dbc.Col(
                [
                    html.H5("Plot Controls"),
                    html.Label("X-axis:"),
                    dcc.Dropdown(
                        id='x-axis',
                        options=[{'label': col, 'value': col} for col in numeric_columns],
                        value=numeric_columns[0] if numeric_columns else None,
                        style={"color": "black"} 
                    ),
                    html.Label("X-axis Scale:"),
                    dcc.RadioItems(
                        id='x-scale',
                        options=[{'label': s, 'value': s} for s in ['linear', 'log']],
                        value='linear',
                        inline=True,
                        style={"color": "white"} 
                    ),
                    html.Label("Y-axis:"),
                    dcc.Dropdown(
                        id='y-axis',
                        options=[{'label': col, 'value': col} for col in numeric_columns],
                        value=numeric_columns[1] if len(numeric_columns) > 1 else (numeric_columns[0] if numeric_columns else None),
                        style={"color": "black"} 
                    ),
                    html.Label("Y-axis Scale:"),
                    dcc.RadioItems(
                        id='y-scale',
                        options=[{'label': s, 'value': s} for s in ['linear', 'log']],
                        value='linear',
                        inline=True,
                        style={"color": "white"} 
                    ),
                ],
                width=3,  # Side panel width
                style={"background": "#222", "padding": "20px", "borderRadius": "8px", "color": "#fff", "minHeight": "500px"}
            ),
            dbc.Col(
                [
                    dcc.Tabs(id='main-tabs', value='tab-graph', children=[
                        dcc.Tab(label='Graph', value='tab-graph', children=[
                            dcc.Graph(id="scatter-plot")
                        ]),
                        dcc.Tab(label='Table', value='tab-table', children=[
                            dash_table.DataTable(
                                id='main-table',
                                data=df[visible_columns].to_dict('records'),
                                columns=[{"name": col, "id": col} for col in visible_columns],
                                page_size=6,
                                filter_action='native',
                                sort_action='native',
                                row_selectable='single',
                                selected_rows=[],
                            )
                        ])
                    ])
                ],
                width=9  # Main content width
            )
        ]),
        dcc.Store(id='clicked-point'),
        dcc.Store(id='click-counter', data=0),
        dcc.Store(id='clear-clickdata', data=False),
        html.Button(id='close-popup', style={'display': 'none'}),
        html.Div(id='image-popup', style={'display': 'none'})
    ]




def register_callbacks(app, df):
    @app.callback(
        Output("scatter-plot", "figure"),
        Input("x-axis", "value"),
        Input("y-axis", "value"),
        Input("x-scale", "value"),
        Input("y-scale", "value"),
        Input('data-store', 'data'),
        prevent_initial_call=False
    )
    def update_figure(x_col, y_col, x_scale, y_scale, data_json):
        if data_json is None:
            return px.scatter(title="No data loaded.")
        df = pd.read_json(data_json, orient='split')
        # Defensive: check if columns exist and are numeric
        if x_col not in df.columns or y_col not in df.columns or 'S/N' not in df.columns:
            return px.scatter(title="Selected columns not found in data.")
        if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]) or not pd.api.types.is_numeric_dtype(df['S/N']):
            return px.scatter(title="Selected columns must be numeric.")
        try:
            fig = px.scatter(df, x=x_col, y=y_col, size='S/N', size_max=20, title=f"{y_col} vs {x_col}")
            fig.update_traces(
                hoverinfo="none",
                hovertemplate=None,
                customdata=df[[col for col in ['ImageFilename', 'MJD', 'Burst_DM'] if col in df.columns]].values
            )
            fig.update_layout(xaxis_type=x_scale, yaxis_type=y_scale)
            return fig
        except Exception as e:
            return px.scatter(title=f"Error: {e}")
    

    
    
    # Store to hold clicked point data
    # Store to hold a click counter that increments every click (even same point)
    @app.callback(
        Output('clicked-point', 'data'),
        Output('click-counter', 'data'),
        Input('scatter-plot', 'clickData'),
        Input('close-popup', 'n_clicks'),
        Input('main-table', 'selected_rows'),
        State('data-store', 'data'),
        State('click-counter', 'data'),
        prevent_initial_call=False
    )
    def update_clicked_point(clickData, close_clicks, selected_rows, data_json, click_counter):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'scatter-plot' and clickData:
            new_count = (click_counter or 0) + 1
            return clickData["points"][0], new_count

        elif trigger == 'main-table' and selected_rows is not None and len(selected_rows) > 0:
            df = pd.read_json(data_json, orient='split')
            row = df.iloc[selected_rows[0]]
            customdata = [
                row.get('ImageFilename', ''),
                row.get('MJD', ''),
                row.get('Burst_DM', '')
            ]
            point_data = {"customdata": customdata}
            new_count = (click_counter or 0) + 1
            return point_data, new_count

        elif trigger == 'close-popup':
            return None, 0

        return no_update, no_update
    

    

    @app.callback(
        Output('image-popup', 'children'),
        Output('image-popup', 'style'),
        Input('clicked-point', 'data'),
        Input('click-counter', 'data'),
        prevent_initial_call=True
    )
    def display_click_popup(point_data, click_counter):
        if not point_data:
            popup_content = dbc.Modal([
                dbc.ModalHeader(
                    dbc.Button('✖', id='close-popup', n_clicks=0, color='link', style={
                        'fontSize': '20px', 'float': 'right', 'margin': 0, 'padding': 0
                    }),
                    close_button=False
                ),
                dbc.ModalBody([])
            ], id='image-modal', is_open=False, centered=True, backdrop="static", keyboard=False, style={"zIndex": 1050})
            return popup_content, {'display': 'block'}

        custom_data = point_data.get("customdata", [])
        if len(custom_data) < 3:
            popup_content = dbc.Modal([
                dbc.ModalHeader(
                    dbc.Button('✖', id='close-popup', n_clicks=0, color='link', style={
                        'fontSize': '20px', 'float': 'right', 'margin': 0, 'padding': 0
                    }),
                    close_button=False
                ),
                dbc.ModalBody([])
            ], id='image-modal', is_open=False, centered=True, backdrop="static", keyboard=False, style={"zIndex": 1050})
            return popup_content, {'display': 'block'}

        image_filename, mjd, burst_dm = custom_data
        image_path = os.path.join(image_directory, image_filename)
        encoded = encode_image(image_path)
        if not encoded:
            popup_content = dbc.Modal([
                dbc.ModalHeader(
                    dbc.Button('✖', id='close-popup', n_clicks=0, color='link', style={
                        'fontSize': '20px', 'float': 'right', 'margin': 0, 'padding': 0
                    }),
                    close_button=False
                ),
                dbc.ModalBody([])
            ], id='image-modal', is_open=False, centered=True, backdrop="static", keyboard=False, style={"zIndex": 1050})
            return popup_content, {'display': 'block'}

        popup_content = dbc.Modal([
            dbc.ModalHeader(
                dbc.Button('✖', id='close-popup', n_clicks=0, color='link', style={
                    'fontSize': '20px', 'float': 'right', 'margin': 0, 'padding': 0
                }),
                close_button=False
            ),
            dbc.ModalBody([
                html.Img(src=f"data:image/png;base64,{encoded}", style={
                    "width": "100%", "height": "auto", "border": "2px solid #ccc",
                    "display": "block", "margin": "0 auto"
                }),
                html.P(f"MJD: {mjd}", style={"fontSize": "12px", "marginTop": "10px"}),
                html.P(f"Burst DM: {burst_dm}", style={"fontSize": "12px"}),
                #html.P(f"{image_filename}", style={"fontSize": "10px", "wordBreak": "break-all"}),
                html.A("View Full Image", href=f"/assets/Images/{image_filename}", target="_blank", style={
                    "display": "block", "marginTop": "12px", "textAlign": "center", "color": "#007bff",
                    "fontWeight": "bold", "textDecoration": "underline", "fontSize": "14px"
                })
            ])
        ], id='image-modal', is_open=True, centered=True, backdrop="static", keyboard=False, style={"zIndex": 1050})

        return popup_content, {'display': 'block'}

    @app.callback(
        Output('dynamic-content', 'children'),
        Output('data-store', 'data'),
        Input('csv-selector', 'value'),
        prevent_initial_call=False
    )
    def update_dynamic_content(selected_csv):
        if not selected_csv:
            return html.Div("Please select a CSV file."), None
        csv_path = os.path.join('./utils', selected_csv)
        try:
            # Use the same logic as load_data()
            df_new = pd.read_csv(csv_path, delim_whitespace=True, header=None)
            df_new.columns = ['col1', 'col2', 'MJD', 'Burst_DM', 'col5', 'S/N', 'col7', 'col8', 'ImagePath', 'col10', 'col11']
            df_new['ImageFilename'] = df_new['ImagePath'].apply(lambda x: os.path.basename(x).replace('.png', '_replot.png'))
        except Exception as e:
            return html.Div(f"Error loading file: {e}"), None
        return generate_controls_and_plot(df_new), df_new.to_json(date_format='iso', orient='split')

    # Add callbacks for opening/closing modals
    @app.callback(
        Output('table-modal', 'is_open'),
        [Input('open-table-btn', 'n_clicks'), Input('close-table-btn', 'n_clicks')],
        [State('table-modal', 'is_open')],
        prevent_initial_call=False
    )
    def toggle_table_modal(open_clicks, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return False
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger == 'open-table-btn':
            return True
        elif trigger == 'close-table-btn':
            return False
        return is_open

    @app.callback(
        Output('graph-modal', 'is_open'),
        [Input('open-graph-btn', 'n_clicks'), Input('close-graph-btn', 'n_clicks')],
        [State('graph-modal', 'is_open')],
        prevent_initial_call=False
    )
    def toggle_graph_modal(open_clicks, close_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return False
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger == 'open-graph-btn':
            return True
        elif trigger == 'close-graph-btn':
            return False
        return is_open

    @app.callback(
        Output('table-url', 'pathname'),
        Input('open-table-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def open_table_window(n):
        if n:
            import webbrowser
            webbrowser.open_new('/table')
        return no_update

    @app.callback(
        Output('graph-url', 'pathname'),
        Input('open-graph-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def open_graph_window(n):
        if n:
            import webbrowser
            webbrowser.open_new('/graph')
        return no_update

    @app.callback(
        Output('dynamic-content', 'children', allow_duplicate=True),
        Input('table-url', 'pathname'),
        prevent_initial_call=True
    )
    def render_table_page(path):
        if path == '/table':
            data_json = app.layout.children[0].data
            df = pd.read_json(data_json, orient='split')
            visible_columns = [col for col in ['MJD', 'Burst_DM', 'S/N', 'ImageFilename'] if col in df.columns]
            return dash_table.DataTable(
                data=df[visible_columns].to_dict('records'),
                columns=[{"name": col, "id": col} for col in visible_columns],
                page_size=10,
                filter_action='native',
                sort_action='native',
                style_table={'overflowX': 'auto'}
            )
        return no_update

    @app.callback(
        Output('dynamic-content', 'children', allow_duplicate=True),
        Input('graph-url', 'pathname'),
        prevent_initial_call=True
    )
    def render_graph_page(path):
        if path == '/graph':
            data_json = app.layout.children[0].data
            df = pd.read_json(data_json, orient='split')
            numeric_columns = get_numeric_columns(df)
            return dcc.Graph(
                id="scatter-plot",
                figure=px.scatter(df, x=numeric_columns[0], y=numeric_columns[1], size='S/N', size_max=20)
            )
        return no_update


