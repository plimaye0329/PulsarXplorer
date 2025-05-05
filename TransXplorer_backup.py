from dash import Dash, html, dash_table, dcc, Input, Output, State, no_update, callback_context
import pandas as pd
import plotly.express as px
import os
import base64

# Load Data
df = pd.read_csv('band1_3.txt', delim_whitespace=True, header=None)
df.columns = ['col1', 'col2', 'MJD', 'Burst_DM', 'col5', 'S/N', 'col7', 'col8', 'ImagePath', 'col10', 'col11']
df['ImageFilename'] = df['ImagePath'].apply(lambda x: os.path.basename(x).replace('.png', '_replot.png'))

image_directory = './'

# Utility: encode image
def encode_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Image not found: {image_path}")
        return None

# Layout
def create_layout(df):
    numeric_columns = ['MJD', 'Burst_DM', 'S/N']
    visible_columns = ['MJD', 'Burst_DM', 'S/N', 'ImageFilename']

    return html.Div([
        html.H1('TransXplorer'),

        html.Div([
            html.Label("X-axis:"),
            dcc.Dropdown(id='x-axis', options=[{'label': col, 'value': col} for col in numeric_columns],
                         value='MJD'),
            html.Label("X-axis Scale:"),
            dcc.RadioItems(id='x-scale', options=['linear', 'log'], value='linear', inline=True),

            html.Label("Y-axis:"),
            dcc.Dropdown(id='y-axis', options=[{'label': col, 'value': col} for col in numeric_columns],
                         value='Burst_DM'),
            html.Label("Y-axis Scale:"),
            dcc.RadioItems(id='y-scale', options=['linear', 'log'], value='linear', inline=True),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        dash_table.DataTable(
            data=df[visible_columns].to_dict('records'),
            columns=[{"name": col, "id": col} for col in visible_columns],
            page_size=3
        ),

        dcc.Graph(id="scatter-plot", clear_on_unhover=True, style={"width": "100%"}),

        dcc.Store(id='clicked-point'),

        # 🔧 Add placeholder with close-popup ID (initially hidden)
        html.Button(id='close-popup', style={'display': 'none'}),

        html.Div(id='image-popup', style={'display': 'none'})
    ])

# Callbacks
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
        fig.update_layout(
            xaxis_type=x_scale,
            yaxis_type=y_scale
        )
        return fig

    # ✅ Combined callback to handle click and close
    @app.callback(
        Output('clicked-point', 'data'),
        Input('scatter-plot', 'clickData'),
        Input('close-popup', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_clicked_point(clickData, close_clicks):
        ctx = callback_context

        if not ctx.triggered:
            return no_update

        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'scatter-plot' and clickData:
            return clickData["points"][0]
        elif trigger == 'close-popup':
            return None

        return no_update

    # Show/hide popup
    @app.callback(
        Output('image-popup', 'children'),
        Output('image-popup', 'style'),
        Input('clicked-point', 'data'),
        prevent_initial_call=True
    )
    def display_click_popup(point_data):
        if not point_data:
            return no_update, {'display': 'none'}

        custom_data = point_data.get("customdata", [])
        if len(custom_data) < 3:
            return no_update, {'display': 'none'}

        image_filename, mjd, burst_dm = custom_data
        image_path = os.path.join(image_directory, image_filename)
        encoded = encode_image(image_path)

        if not encoded:
            return no_update, {'display': 'none'}

        popup_content = html.Div([
            html.Button('✖', id='close-popup', n_clicks=0,
                        style={'position': 'absolute', 'top': '5px', 'right': '10px', 'background': 'none',
                               'border': 'none', 'fontSize': '20px', 'cursor': 'pointer'}),
            html.Img(src=f"data:image/png;base64,{encoded}",
                     style={"width": "400px", "height": "auto", "border": "2px solid #ccc"}),
            html.P(f"MJD: {mjd}", style={"fontSize": "12px", "marginTop": "10px"}),
            html.P(f"Burst DM: {burst_dm}", style={"fontSize": "12px"}),
            html.P(f"{image_filename}", style={"fontSize": "10px", "wordBreak": "break-all"})
        ], style={
            'position': 'fixed',
            'top': '50%',
            'left': '50%',
            'transform': 'translate(-50%, -50%)',
            'zIndex': 999,
            'backgroundColor': 'white',
            'padding': '20px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.2)',
            'borderRadius': '8px',
            'width': '440px'
        })

        return popup_content, {'display': 'block'}

# Main
app = Dash(__name__)
app.layout = create_layout(df)
register_callbacks(app, df)

if __name__ == '__main__':
    app.run(debug=True)

