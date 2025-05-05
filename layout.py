from dash import html, dash_table, dcc

def create_layout(df):
    numeric_columns = ['MJD', 'Burst_DM', 'S/N']
    visible_columns = ['MJD', 'Burst_DM', 'S/N', 'ImageFilename']

    return html.Div([
        html.H1('TransXplorer'),

        html.Div([
            html.Label("X-axis:"),
            dcc.Dropdown(id='x-axis', options=[{'label': col, 'value': col} for col in numeric_columns], value='MJD'),
            html.Label("X-axis Scale:"),
            dcc.RadioItems(id='x-scale', options=['linear', 'log'], value='linear', inline=True),
            html.Label("Y-axis:"),
            dcc.Dropdown(id='y-axis', options=[{'label': col, 'value': col} for col in numeric_columns], value='Burst_DM'),
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
        html.Button(id='close-popup', style={'display': 'none'}),
        html.Div(id='image-popup', style={'display': 'none'})
    ])

