import os
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash
from dash import dash_table
from dash_split_pane import DashSplitPane

DATA_FOLDER = '/data'

def get_csv_files():
    return [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv') or f.endswith('.cands')]

def create_layout():
    return html.Div([
        # ---- Stores ----
        dcc.Store(id='clicked-point'),
        dcc.Store(id='click-counter', data=0),
        dcc.Store(id='clear-clickdata', data=False),
        dcc.Store(id='cached-csv-data'),
        dcc.Store(id='last-modified-timestamp', data=""),
        dcc.Store(id='ml-label-store', data={}),   # 🔑 NEW
        html.Button(id='close-popup-hidden', style={'display': 'none'}),

        # ---- Intervals ----
        dcc.Interval(id='interval-component', interval=5000, n_intervals=0),
        dcc.Interval(id='refresh-files-interval', interval=10000, n_intervals=0),

        dbc.Container([
            dbc.Row([
                # ===================== Sidebar =====================
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H4("Selection Panel", className="mb-0", style={"color": "black"})
                        ),
                        dbc.CardBody([
                            dbc.Alert(
                                id='file-load-alert',
                                is_open=False,
                                duration=4000,
                                dismissable=True
                            ),

                            html.H2("TransientXplorer", className="display-5 mb-3",
                                    style={"color": "black"}),

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

                            dbc.Label("Refresh interval (s):", style={"color": "black"}),
                            dcc.Input(
                                id='interval-input',
                                type='number',
                                value=5,
                                min=1,
                                step=1,
                                style={"marginBottom": "15px", "width": "100%"}
                            ),

                            dbc.Label("Select CSV file", className="mt-3 fw-semibold",
                                      style={"color": "black"}),
                            dcc.Dropdown(
                                id='csv-selector',
                                options=[],
                                placeholder='Choose a CSV file',
                                className="mb-3"
                            ),

                            html.Hr(),

                            html.Label("X-axis:", style={"color": "black"}),
                            dcc.Dropdown(
                                id='x-axis',
                                options=[],
                                placeholder='Select X-axis column',
                                persistence=True
                            ),

                            html.Label("X-axis Scale:", style={"color": "black"}),
                            dcc.RadioItems(
                                id='x-scale',
                                options=[{'label': s, 'value': s} for s in ['linear', 'log']],
                                value='linear',
                                inline=True
                            ),

                            html.Label("Y-axis:", style={"color": "black"}),
                            dcc.Dropdown(
                                id='y-axis',
                                options=[],
                                placeholder='Select Y-axis column',
                                persistence=True
                            ),

                            html.Label("Y-axis Scale:", style={"color": "black"}),
                            dcc.RadioItems(
                                id='y-scale',
                                options=[{'label': s, 'value': s} for s in ['linear', 'log']],
                                value='linear',
                                inline=True
                            ),

                            html.Hr(),
                        ])
                    ], color="light", className="shadow-sm", style={
                        "borderRadius": "12px",
                        "padding": "15px",
                        "height": "100%"
                    }),
                ], width=3, style={"height": "100vh"}),

                # ===================== Main Panel =====================
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H4("Monitoring Interface", className="mb-0")
                        ),
                        dbc.CardBody([
                            DashSplitPane(
                                split="horizontal",
                                size="60%",
                                minSize=100,
                                allowResize=True,
                                children=[
                                    dcc.Graph(
                                        id="scatter-plot",
                                        style={"width": "100%", "height": "100%"}
                                    ),
                                    html.Div(
                                        dash_table.DataTable(
                                            id='main-table',
                                            columns=[],
                                            data=[],
                                            page_size=6,
                                            filter_action='native',
                                            sort_action='native',
                                            row_selectable='single',
                                            selected_rows=[],
                                            style_table={
                                                'overflowX': 'auto',
                                                'height': '100%'
                                            },
                                            style_cell={'textAlign': 'left'},
                                        ),
                                        id='table-container',
                                        style={'height': '100%'}
                                    )
                                ],
                                style={"height": "80vh"}
                            ),

                            # ===================== Modal =====================
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Button(
                                                        "RFI",
                                                        id="label-rfi",
                                                        color="danger",
                                                        size="sm"
                                                    ),
                                                    width="auto"
                                                ),
                                                dbc.Col(
                                                    dbc.Button(
                                                        "Pulse",
                                                        id="label-pulse",
                                                        color="success",
                                                        size="sm"
                                                    ),
                                                    width="auto"
                                                ),
                                                dbc.Col(
                                                    dbc.Button(
                                                        "✖",
                                                        id="close-popup",
                                                        n_clicks=0,
                                                        color="link",
                                                        style={"fontSize": "18px"}
                                                    ),
                                                    width="auto"
                                                ),
                                            ],
                                            justify="end",
                                            align="center",
                                            className="g-2"
                                        ),
                                        close_button=False
                                    ),

                                    dbc.ModalBody([
                                        html.Img(
                                            id='popup-image',
                                            style={
                                                "width": "100%",
                                                "height": "auto",
                                                "border": "2px solid #ccc",
                                                "display": "block",
                                                "margin": "0 auto"
                                            }
                                        ),
                                        html.P(
                                            id='popup-mjd',
                                            style={"fontSize": "12px", "marginTop": "10px"}
                                        ),
                                        html.P(
                                            id='popup-dm',
                                            style={"fontSize": "12px"}
                                        ),
                                    ])
                                ],
                                id='image-modal',
                                is_open=False,
                                centered=True,
                                backdrop="static",
                                keyboard=False,
                            ),

                            html.Div(id='dynamic-content', style={"marginTop": "20px"})
                        ], style={"height": "100%", "overflowY": "auto"})
                    ], className="shadow-sm", style={
                        "borderRadius": "12px",
                        "height": "100%"
                    })
                ], width=9, style={"height": "100vh"}),

            ], className="gx-4 bg-dark", style={"height": "100%"})
        ], fluid=True, className="p-0 m-0", style={"height": "100%"}),
    ], style={"height": "100vh", "margin": 0, "padding": 0})

