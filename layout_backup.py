from dash import html, dash_table, dcc

def create_layout(df):
    numeric_columns = ['MJD', 'Burst_DM', 'S/N']
    visible_columns = ['MJD', 'Burst_DM', 'S/N', 'ImageFilename']

    return html.Div([
        html.H1('TransientXplorer'),

        # Controls for plot axes and scales
        html.Div([
            html.Label("X-axis:"),
            dcc.Dropdown(
                id='x-axis',
                options=[{'label': col, 'value': col} for col in numeric_columns],
                value='MJD'
            ),

            html.Label("X-axis Scale:"),
            dcc.RadioItems(
                id='x-scale',
                options=[{'label': s, 'value': s} for s in ['linear', 'log']],
                value='linear',
                inline=True
            ),

            html.Label("Y-axis:"),
            dcc.Dropdown(
                id='y-axis',
                options=[{'label': col, 'value': col} for col in numeric_columns],
                value='Burst_DM'
            ),

            html.Label("Y-axis Scale:"),
            dcc.RadioItems(
                id='y-scale',
                options=[{'label': s, 'value': s} for s in ['linear', 'log']],
                value='linear',
                inline=True
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # Data Table
        dash_table.DataTable(
            data=df[visible_columns].to_dict('records'),
            columns=[{"name": col, "id": col} for col in visible_columns],
            page_size=3,
            filter_action='native',
            sort_action='native'
        ),

        # Main scatter plot
        dcc.Graph(id="scatter-plot"),

        # Store to keep track of clicked point for the popup modal
        dcc.Store(id='clicked-point'),
        dcc.Store(id='click-counter', data=0),
        dcc.Store(id='clear-clickdata', data=False),

        # Invisible button for closing the popup via callback
        html.Button(id='close-popup', style={'display': 'none'}),

        # Popup modal will be rendered here dynamically
        html.Div(id='image-popup', style={'display': 'none'})
    ])
