import os
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash
from dash import dash_table

DATA_FOLDER = './utils/'

def get_csv_files():
    return [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv') or f.endswith('.cands')]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

def create_layout():
    interval_options = [
        {'label': '5 seconds', 'value': 5000},
        {'label': '30 seconds', 'value': 30000},
        {'label': '500 seconds', 'value': 500000},
    ]

    interval_selector = dcc.RadioItems(
        id='interval-selector',
        options=interval_options,
        value=5000,  # default to 5 seconds
        labelStyle={'display': 'inline-block', 'marginRight': '15px'},
        style={"color": "black", "marginBottom": "15px"}
    )
    
    return dbc.Container([
        dcc.Store(id='clicked-point'),
        dcc.Store(id='click-counter', data=0),
        dcc.Store(id='clear-clickdata', data=False),
        html.Button(id='close-popup', style={'display': 'none'}),
        dcc.Interval(id='interval-component', interval=5000, n_intervals=0),
        dcc.Store(id='cached-csv-data'),
        dcc.Store(id='last-modified-timestamp', data=""),

        dbc.Row([
            # Sidebar controls
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Selection Panel", className="mb-0", style={"color": "black"})),
                    dbc.CardBody([
                        html.H2("TransientXplorer", className="display-5 mb-3", style={"color": "black"}),
                        html.P(
                            "Interactive tool for exploring transient burst data.",
                            className="text-muted fst-italic"
                        ),

                        dbc.Checklist(
                            id='auto-refresh-toggle',
                            options=[{'label': 'Auto Refresh', 'value': 'enabled'}],
                            value=['enabled'],
                            inline=True,
                            style={"color": "black", "marginBottom": "15px"}
                        ),

                        interval_selector,

                        dbc.Label("Select CSV file", className="mt-3 fw-semibold", style={"color": "black"}),
                        dcc.Dropdown(
                            id='csv-selector',
                            options=[{'label': f, 'value': f} for f in get_csv_files()],
                            placeholder='Choose a CSV file',
                            style={"color": "black"},
                            className="mb-3"
                        ),
                        html.Hr(),

                        html.Label("X-axis:", style={"color": "black"}),
                        dcc.Dropdown(id='x-axis', options=[], value=None, style={"color": "black"},persistence=True),

                        html.Label("X-axis Scale:", style={"color": "black"}),
                        dcc.RadioItems(
                            id='x-scale',
                            options=[{'label': s, 'value': s} for s in ['linear', 'log']],
                            value='linear',
                            inline=True,
                            style={"color": "black"}
                        ),

                        html.Label("Y-axis:", style={"color": "black"}),
                        dcc.Dropdown(id='y-axis', options=[], value=None, style={"color": "black"},persistence=True),

                        html.Label("Y-axis Scale:", style={"color": "black"}),
                        dcc.RadioItems(
                            id='y-scale',
                            options=[{'label': s, 'value': s} for s in ['linear', 'log']],
                            value='linear',
                            inline=True,
                            style={"color": "black"}
                        ),
                    ])
                ], color="light", className="shadow-sm", style={
                    "borderRadius": "12px",
                    "background": "black",
                    "color": "black",
                    "padding": "15px"
                }),
            ], width=3),

            # Main content (Graph + Table tabs)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Monitoring Interface", className="mb-0")),
                    dbc.CardBody([
                        dcc.Tabs(id='main-tabs', value='tab-graph', children=[
                            dcc.Tab(label='Graph', value='tab-graph', children=[
                                dcc.Graph(id="scatter-plot")
                            ]),
                            dcc.Tab(label='Table', value='tab-table', children=[
                                dash_table.DataTable(
                                    id='main-table',
                                    columns=[],  # will be populated dynamically
                                    data=[],
                                    page_size=6,
                                    filter_action='native',
                                    sort_action='native',
                                    row_selectable='single',
                                    selected_rows=[],
                                    style_table={'overflowX': 'auto'},
                                )
                            ])
                        ]),
                        html.Div(id='image-popup', style={'display': 'none'}),
                        html.Div(id='dynamic-content', style={"marginTop": "20px"})
                    ])
                ], className="shadow-sm", style={"borderRadius": "12px"})
            ], width=9),
        ], className="mt-4 gx-4 bg-dark")
    ], fluid=True)

app.layout = create_layout()


