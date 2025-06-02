from dash import Input, Output, State, callback_context, no_update, html
import plotly.express as px
import os
from utils.image import encode_image
import dash_bootstrap_components as dbc

image_directory = 'assets/Images'

def register_callbacks(app, df):
    @app.callback(
        Output("scatter-plot", "figure"),
        Input("x-axis", "value"),
        Input("y-axis", "value"),
        Input("x-scale", "value"),
        Input("y-scale", "value")
    )
    def update_figure(x_col, y_col, x_scale, y_scale):
        fig = px.scatter(df, x=x_col, y=y_col, size='S/N', size_max=20, title=f"{y_col} vs {x_col}")
        fig.update_traces(
            hoverinfo="none",
            hovertemplate=None,
            customdata=df[['ImageFilename', 'MJD', 'Burst_DM']].values
        )
        fig.update_layout(xaxis_type=x_scale, yaxis_type=y_scale)
        return fig

    # Store to hold clicked point data
    # Store to hold a click counter that increments every click (even same point)
    @app.callback(
        Output('clicked-point', 'data'),
        Output('click-counter', 'data'),
        Input('scatter-plot', 'clickData'),
        Input('close-popup', 'n_clicks'),
        State('click-counter', 'data'),
        prevent_initial_call=False
    )
    def update_clicked_point(clickData, close_clicks, click_counter):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'scatter-plot' and clickData:
            # increment counter to force popup refresh even if same point clicked
            new_count = (click_counter or 0) + 1
            return clickData["points"][0], new_count

        elif trigger == 'close-popup':
            # reset on close
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
                html.P(f"{image_filename}", style={"fontSize": "10px", "wordBreak": "break-all"}),
                html.A("View Full Image", href=f"/assets/Images/{image_filename}", target="_blank", style={
                    "display": "block", "marginTop": "12px", "textAlign": "center", "color": "#007bff",
                    "fontWeight": "bold", "textDecoration": "underline", "fontSize": "14px"
                })
            ])
        ], id='image-modal', is_open=True, centered=True, backdrop="static", keyboard=False, style={"zIndex": 1050})

        return popup_content, {'display': 'block'}


