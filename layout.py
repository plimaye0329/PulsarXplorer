import os
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import dash_table
from dash_split_pane import DashSplitPane

DATA_FOLDER = '/data'


def create_layout():
    return html.Div(
        [
            # =====================================================
            # Stores
            # =====================================================
            dcc.Store(id='clicked-point'),
            dcc.Store(id='click-counter', data=0),
            dcc.Store(id='seen-points-store', data=[]),
            dcc.Store(id='ml-label-store', data={}),
            dcc.Store(id='last-modified-timestamp', data=""),

            # =====================================================
            # Intervals
            # =====================================================
            dcc.Interval(id='interval-component', interval=5000, n_intervals=0),
            dcc.Interval(id='refresh-files-interval', interval=10000, n_intervals=0),

            dbc.Container(
                fluid=True,
                className="p-0 m-0",
                children=[
                    dbc.Row(
                        className="gx-3",
                        children=[
                            # =================================================
                            # Sidebar
                            # =================================================
                            dbc.Col(
                                width=3,
                                style={"height": "100vh"},
                                children=[
                                    dbc.Card(
                                        className="h-100 shadow-sm",
                                        children=[
                                            dbc.CardHeader(
                                                html.H5("PulsarXplorer", className="mb-0")
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dbc.Alert(
                                                        id='file-load-alert',
                                                        is_open=False,
                                                        dismissable=True,
                                                        duration=4000
                                                    ),

                                                    # -------------------------
                                                    # Auto refresh controls
                                                    # -------------------------
                                                    dbc.Checklist(
                                                        id='auto-refresh-toggle',
                                                        options=[
                                                            {
                                                                'label': 'Auto Refresh',
                                                                'value': 'enabled'
                                                            }
                                                        ],
                                                        value=['enabled'],
                                                        inline=True,
                                                    ),

                                                    dbc.Label("Refresh interval (seconds)"),
                                                    dcc.Input(
                                                        id='interval-input',
                                                        type='number',
                                                        value=5,
                                                        min=1,
                                                        step=1,
                                                        style={
                                                            "width": "100%",
                                                            "marginBottom": "10px"
                                                        }
                                                    ),

                                                    html.Hr(),

                                                    # -------------------------
                                                    # .cands file selector
                                                    # -------------------------
                                                    dbc.Label("Select .cands file"),
                                                    dcc.Dropdown(
                                                        id='csv-selector',
                                                        options=[],
                                                        placeholder='Choose a .cands file'
                                                    ),

                                                    html.Hr(),

                                                    # -------------------------
                                                    # Axes controls
                                                    # -------------------------
                                                    dbc.Label("X-axis"),
                                                    dcc.Dropdown(
                                                        id='x-axis',
                                                        options=[],
                                                        placeholder='Select X-axis'
                                                    ),

                                                    dcc.RadioItems(
                                                        id='x-scale',
                                                        options=[
                                                            {'label': s, 'value': s}
                                                            for s in ['linear', 'log']
                                                        ],
                                                        value='linear',
                                                        inline=True
                                                    ),

                                                    html.Br(),

                                                    dbc.Label("Y-axis"),
                                                    dcc.Dropdown(
                                                        id='y-axis',
                                                        options=[],
                                                        placeholder='Select Y-axis'
                                                    ),

                                                    dcc.RadioItems(
                                                        id='y-scale',
                                                        options=[
                                                            {'label': s, 'value': s}
                                                            for s in ['linear', 'log']
                                                        ],
                                                        value='linear',
                                                        inline=True
                                                    ),
                                                ]
                                            ),
                                        ]
                                    )
                                ],
                            ),

                            # =================================================
                            # Main panel
                            # =================================================
                            dbc.Col(
                                width=9,
                                style={"height": "100vh"},
                                children=[
                                    dbc.Card(
                                        className="h-100 shadow-sm",
                                        children=[
                                            dbc.CardHeader(
                                                html.H5("Pulsar Candidate Monitoring", className="mb-0")
                                            ),
                                            dbc.CardBody(
                                                style={"padding": "0"},
                                                children=[
                                                    DashSplitPane(
                                                        split="horizontal",
                                                        size="60%",
                                                        minSize=120,
                                                        allowResize=True,
                                                        style={"height": "75vh"},
                                                        children=[
                                                            dcc.Graph(
                                                                id='scatter-plot',
                                                                style={
                                                                    "width": "100%",
                                                                    "height": "100%"
                                                                }
                                                            ),
                                                            dash_table.DataTable(
                                                                id='main-table',
                                                                columns=[],
                                                                data=[],
                                                                page_size=6,
                                                                filter_action='native',
                                                                sort_action='native',
                                                                row_selectable='single',
                                                                style_table={
                                                                    'height': '100%',
                                                                    'overflowY': 'auto',
                                                                    'overflowX': 'auto'
                                                                },
                                                                style_cell={
                                                                    'textAlign': 'left'
                                                                },
                                                            )
                                                        ]
                                                    ),

                                                    # -------------------------
                                                    # Modal
                                                    # -------------------------
                                                    dbc.Modal(
                                                        [
                                                            dbc.ModalHeader(
                                                                [
                                                                    dbc.Button(
                                                                        "RFI",
                                                                        id="label-rfi",
                                                                        color="danger",
                                                                        size="sm"
                                                                    ),
                                                                    dbc.Button(
                                                                        "Pulse",
                                                                        id="label-pulse",
                                                                        color="success",
                                                                        size="sm"
                                                                    ),
                                                                    dbc.Button(
                                                                        "✖",
                                                                        id="close-popup",
                                                                        color="link",
                                                                        style={"fontSize": "18px"}
                                                                    ),
                                                                ],
                                                                close_button=False
                                                            ),

                                                            dbc.ModalBody(
                                                                [
                                                                    html.Img(
                                                                        id='popup-image',
                                                                        style={
                                                                            "width": "100%",
                                                                            "border": "2px solid #ccc",
                                                                            "display": "block",
                                                                            "margin": "0 auto"
                                                                        }
                                                                    ),
                                                                    html.P(
                                                                        id='popup-id',
                                                                        style={
                                                                            "fontSize": "12px",
                                                                            "marginTop": "10px"
                                                                        }
                                                                    ),
                                                                    html.P(
                                                                        id='popup-dm',
                                                                        style={"fontSize": "12px"}
                                                                    ),
                                                                    html.P(
                                                                        id='popup-sn',
                                                                        style={"fontSize": "12px"}
                                                                    ),
                                                                ]
                                                            ),
                                                        ],
                                                        id='image-modal',
                                                        is_open=False,
                                                        centered=True,
                                                        backdrop="static",
                                                        keyboard=False,
                                                    ),

                                                    # -------------------------
                                                    # REQUIRED placeholder
                                                    # -------------------------
                                                    html.Div(id='dynamic-content'),
                                                ],
                                            ),
                                        ],
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ],
        style={"height": "100vh"},
    )
