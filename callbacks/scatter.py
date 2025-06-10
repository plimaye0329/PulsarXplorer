from dash import Input, Output, State, callback_context, no_update, html, dcc, dash_table
import plotly.express as px
import os
import pandas as pd
import dash_bootstrap_components as dbc
from utils.image import encode_image

image_directory = 'assets/Images'

def register_callbacks(app, df):

    @app.callback(
        Output("scatter-plot", "figure"),
        Input("x-axis", "value"),
        Input("y-axis", "value"),
        Input("x-scale", "value"),
        Input("y-scale", "value"),
        Input('data-store', 'data'),
    )
    def update_figure(x_col, y_col, x_scale, y_scale, data_json):
        if not data_json:
            return px.scatter(title="No data loaded.")
        df = pd.read_json(data_json, orient='split')
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
        State('data-store', 'data'),
        State('click-counter', 'data'),
    )
    def update_clicked_point(clickData, selected_rows, close_clicks, data_json, click_counter):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'scatter-plot' and clickData:
            return clickData["points"][0], (click_counter or 0) + 1
        elif trigger == 'main-table' and selected_rows:
            df = pd.read_json(data_json, orient='split')
            row = df.iloc[selected_rows[0]]
            customdata = [row.get(k, '') for k in ['ImageFilename', 'MJD', 'Burst_DM']]
            return {"customdata": customdata}, (click_counter or 0) + 1
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

    @app.callback(
        Output('dynamic-content', 'children'),
        Output('data-store', 'data'),
        Output('x-axis', 'options'),
        Output('y-axis', 'options'),
        Output('x-axis', 'value'),
        Output('y-axis', 'value'),
        Output('main-table', 'data'),
        Output('main-table', 'columns'),
        Input('csv-selector', 'value'),
    )
    def update_dynamic_content(selected_csv):
        if not selected_csv:
            return html.Div("Please select a CSV."), None, [], [], None, None, [], []

        csv_path = os.path.join('./utils', selected_csv)
        try:
            df_new = pd.read_csv(csv_path, delim_whitespace=True, header=None)
            df_new.columns = ['col1', 'col2', 'MJD', 'Burst_DM', 'col5', 'S/N',
                              'col7', 'col8', 'ImagePath', 'col10', 'col11']
            df_new['ImageFilename'] = df_new['ImagePath'].apply(
                lambda x: os.path.basename(x).replace('.png', '_replot.png'))
        except Exception as e:
            return html.Div(f"Error loading file: {e}"), None, [], [], None, None, [], []

        numeric_columns = [col for col in ['MJD', 'Burst_DM', 'S/N']
                           if col in df_new and pd.api.types.is_numeric_dtype(df_new[col])]
        visible_columns = [col for col in ['MJD', 'Burst_DM', 'S/N', 'ImageFilename'] if col in df_new]

        options = [{'label': col, 'value': col} for col in numeric_columns]
        return (
            html.Div("Data loaded."),  # Placeholder
            df_new.to_json(date_format='iso', orient='split'),
            options,
            options,
            numeric_columns[0] if numeric_columns else None,
            numeric_columns[1] if len(numeric_columns) > 1 else (numeric_columns[0] if numeric_columns else None),
            df_new[visible_columns].to_dict('records'),
            [{"name": col, "id": col} for col in visible_columns]
        )

