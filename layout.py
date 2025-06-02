import os
import pandas as pd
from dash import html, dash_table, dcc, Input, Output, State, ctx, callback
import dash

# Folder containing CSV files
DATA_FOLDER = './utils/'  # change to your folder path

# Initialize the app
app = dash.Dash(__name__)
server = app.server  # for deployment

def get_csv_files():
    # Accept both .csv and .txt files
    return [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv') or f.endswith('.txt')]

def create_layout():
    return html.Div([
        dcc.Store(id='data-store'),  # Ensure data-store always exists
        html.H1('TransientXplorer'),

        # File selection
        html.Label("Select a CSV file:"),
        dcc.Dropdown(
            id='csv-selector',
            options=[{'label': f, 'value': f} for f in get_csv_files()],
            placeholder='Choose a CSV file'
        ),

        # Dynamic content area for controls, table, and plot
        html.Div(id='dynamic-content')
    ])

app.layout = create_layout()

